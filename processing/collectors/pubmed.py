"""
Coletor simples para PubMed usando as E-utilities (esearch + efetch).

Busca será feita no campo Affiliation conforme solicitado. Não depende de
bibliotecas externas (usa urllib + xml.etree) para minimizar dependências.

Função pública:
 - search_by_affiliation(terms, date_start=None, date_end=None, max_results=100)

Retorna lista de dicionários com campos compatíveis com o restante da aplicação
('title', 'authors', 'doi', 'platform', 'publication_date', 'abstract', 'url', 'id').
Se DOI existir, ele será usado como 'id' externo; caso contrário, usa o PMID.
"""
from typing import List, Union, Optional, Dict
import urllib.parse
import urllib.request
import json
import xml.etree.ElementTree as ET
from datetime import datetime

PUBMED_EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _build_affiliation_term_from_list(terms: List[str]) -> str:
    """Transforma uma lista de termos em query que pesquisa cada termo no campo Affiliation.

    Ex: ['HC UFPE', 'Hospital das Clinicas'] -> '("HC UFPE"[Affiliation] OR "Hospital das Clinicas"[Affiliation])'
    """
    if not terms:
        return ""
    quoted = []
    for t in terms:
        t = t.strip()
        if not t:
            continue
        # garantir que aspas existam se o termo tiver espaços
        if '"' in t:
            q = t
        else:
            q = f'"{t}"'
        quoted.append(f"{q}[Affiliation]")
    if not quoted:
        return ""
    if len(quoted) == 1:
        return quoted[0]
    return "(" + " OR ".join(quoted) + ")"


def _http_get(url: str, params: dict = None, timeout: int = 15) -> str:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "NEXUS-Pesquisa/1.0 (Python)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8')


def _esearch_affiliation(query: str, date_start: Optional[str] = None, date_end: Optional[str] = None, retmax: int = 100) -> List[str]:
    params = {
        'db': 'pubmed',
        'term': query,
        'retmode': 'json',
        'retmax': str(retmax)
    }
    # usar datetype=pdat e mindate/maxdate no formato YYYY/MM/DD quando fornecido
    if date_start:
        try:
            ds = datetime.strptime(date_start, "%d/%m/%Y").strftime("%Y/%m/%d")
            params['datetype'] = 'pdat'
            params['mindate'] = ds
        except Exception:
            pass
    if date_end:
        try:
            de = datetime.strptime(date_end, "%d/%m/%Y").strftime("%Y/%m/%d")
            params['datetype'] = 'pdat'
            params['maxdate'] = de
        except Exception:
            pass

    url = PUBMED_EUTILS_BASE + "/esearch.fcgi"
    body = _http_get(url, params=params)
    data = json.loads(body)
    idlist = data.get('esearchresult', {}).get('idlist', [])
    return idlist


def _efetch_summaries(id_list: List[str]) -> List[Dict]:
    if not id_list:
        return []
    url = PUBMED_EUTILS_BASE + "/efetch.fcgi"
    params = {
        'db': 'pubmed',
        'id': ",".join(id_list),
        'retmode': 'xml'
    }
    body = _http_get(url, params=params)
    root = ET.fromstring(body)
    articles = []
    for article in root.findall('.//PubmedArticle'):
        try:
            medline = article.find('MedlineCitation')
            article_elem = medline.find('Article') if medline is not None else None
            # título
            title = ''
            if article_elem is not None:
                t = article_elem.find('ArticleTitle')
                if t is not None and t.text:
                    title = ''.join(t.itertext()).strip()

            # abstract
            abstract = ''
            if article_elem is not None:
                abstract_elem = article_elem.find('Abstract')
                if abstract_elem is not None:
                    parts = ["".join(p.itertext()).strip() for p in abstract_elem.findall('AbstractText')]
                    abstract = "\n".join([p for p in parts if p])

            # autores
            authors = []
            if article_elem is not None:
                author_list = article_elem.find('AuthorList')
                if author_list is not None:
                    for a in author_list.findall('Author'):
                        last = a.find('LastName')
                        initials = a.find('Initials')
                        name = ''
                        if last is not None and last.text:
                            name = last.text
                            if initials is not None and initials.text:
                                name = f"{name} {initials.text}"
                        else:
                            # names like CollectiveName
                            coll = a.find('CollectiveName')
                            if coll is not None and coll.text:
                                name = coll.text
                        if name:
                            authors.append(name)

            # ids (PMID, DOI)
            pmid = None
            doi = None
            aidlist = article.find('.//ArticleIdList')
            if aidlist is not None:
                for aid in aidlist.findall('ArticleId'):
                    idtype = aid.attrib.get('IdType', '').lower()
                    if idtype == 'pubmed' and (aid.text or '').strip():
                        pmid = aid.text.strip()
                    if idtype == 'doi' and (aid.text or '').strip():
                        doi = aid.text.strip()

            # data de publicação (ano)
            pub_date = None
            if article_elem is not None:
                journal = article_elem.find('Journal')
                if journal is not None:
                    jissue = journal.find('JournalIssue')
                    if jissue is not None:
                        pubdate = jissue.find('PubDate')
                        if pubdate is not None:
                            year = pubdate.find('Year')
                            med_year = None
                            if year is not None and year.text:
                                med_year = year.text
                            else:
                                # alguns registros usam MedlineDate
                                md = pubdate.find('MedlineDate')
                                if md is not None and md.text:
                                    med_year = md.text.split()[0]
                            pub_date = med_year

            # url via DOI quando disponível
            url_link = ''
            if doi:
                url_link = f"https://doi.org/{doi}"
            elif pmid:
                url_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            articles.append({
                'title': title,
                'authors': ", ".join(authors),
                'doi': doi or '',
                'platform': 'PubMed',
                'publication_date': pub_date,
                'abstract': abstract,
                'url': url_link,
                'id': doi or pmid or ''
            })
        except Exception:
            # ignorar artigo que falhar no parsing e continuar
            continue
    return articles


def search_by_affiliation(terms: Union[List[str], str], date_start: Optional[str] = None,
                          date_end: Optional[str] = None, max_results: int = 100) -> List[Dict]:
    """Busca artigos no PubMed usando termos aplicados ao campo Affiliation.

    Args:
        terms: Lista de termos ou string (quando for string será usada tal qual no term)
        date_start/date_end: strings no formato 'dd/MM/YYYY' (opcionais)
        max_results: número máximo de ids a recuperar via esearch

    Returns:
        Lista de dicionários representando artigos.
    """
    # construir query
    if isinstance(terms, str):
        # se for uma string contendo OR/() assumimos que já está formatada
        query = terms
    else:
        query = _build_affiliation_term_from_list(terms)

    if not query:
        return []

    try:
        pmids = _esearch_affiliation(query, date_start=date_start, date_end=date_end, retmax=max_results)
    except Exception:
        return []

    # efetch em lotes (limitar tamanho do URL)
    batch_size = 100
    results = []
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        try:
            fetched = _efetch_summaries(batch)
            results.extend(fetched)
        except Exception:
            continue

    return results
