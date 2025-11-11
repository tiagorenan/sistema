## 📚 ROADMAP: Próximas Etapas - Integração PubMed

*Guia passo a passo para implementar a coleta de dados do PubMed*

---

## 🎯 OBJETIVO DA PRÓXIMA ETAPA

Implementar o módulo `processing/collectors/pubmed.py` para:
- ✅ Buscar artigos no PubMed usando Entrez (BIoPython)
- ✅ Validar afiliações com dados da tabela `affiliation_variations`
- ✅ Salvar artigos validados no banco de dados
- ✅ Registrar erros de validação

---

## 📋 DEPENDÊNCIAS NECESSÁRIAS

### Já Instaladas
```
✅ PySide6        (Interface)
✅ SQLite3        (Banco de dados - padrão do Python)
```

### Precisa Instalar
```bash
pip install biopython
pip install openpyxl  # Para exportar depois
```

---

## 🔧 ESTRUTURA DO `pubmed.py`

```python
# processing/collectors/pubmed.py

from Bio import Entrez
from database import DatabaseManager, Article, AffiliationVariation, ErrorLog
from datetime import datetime

class PubMedCollector:
    """Coleta artigos do PubMed"""
    
    def __init__(self):
        self.db = DatabaseManager()
        Entrez.email = "seu_email@example.com"  # Obrigatório
    
    def search_articles(self, search_term: str, date_start: str, date_end: str) -> list:
        """Busca artigos no PubMed"""
        # Implementar
        pass
    
    def fetch_article_details(self, pmid: str) -> dict:
        """Busca detalhes de um artigo específico"""
        # Implementar
        pass
    
    def validate_affiliation(self, article: dict) -> bool:
        """Verifica se o artigo tem afiliação com HC-UFPE"""
        # Implementar
        pass
    
    def save_article(self, article_data: dict, validated: bool):
        """Salva artigo no banco de dados"""
        # Implementar
        pass
    
    def collect_and_save(self, search_term: str, date_start: str, date_end: str):
        """Pipeline completo: buscar → validar → salvar"""
        # Implementar
        pass
```

---

## 📝 PASSO A PASSO DE IMPLEMENTAÇÃO

### Passo 1: Instalar BIoPython
```bash
pip install biopython
```

### Passo 2: Entender a API do Entrez
```python
from Bio import Entrez

Entrez.email = "tiago.renan@example.com"  # IMPORTANTE!

# Buscar
handle = Entrez.esearch(db="pubmed", term="Hospital das Clínicas", retmax=100)
records = Entrez.read(handle)

# Obter IDs
pmids = records["IdList"]

# Buscar detalhes
handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="xml")
records = Entrez.read(handle)
```

### Passo 3: Extrair Dados do XML
```python
for record in records['PubmedArticle']:
    # Extrair campos
    title = record['MedlineCitation']['Article']['ArticleTitle']
    authors = record['MedlineCitation']['Article'].get('AuthorList', [])
    abstract = record['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', [''])[0]
    doi = # ... extrair do artigo
    pubdate = # ... extrair data
```

### Passo 4: Validar Afiliação
```python
def validate_affiliation(article_text: str) -> bool:
    """Verifica se o texto menciona HC-UFPE ou variações"""
    
    # Obter todas as variações cadastradas
    with DatabaseManager() as db:
        variations = db.read_affiliation_variations_by_institution("HC-UFPE")
    
    # Verificar se alguma variação está no artigo
    for var in variations:
        if var.original_text.lower() in article_text.lower():
            return True
    
    return False
```

### Passo 5: Salvar no Banco
```python
def save_article(article_data: dict, validated: bool):
    """Salva artigo no banco de dados"""
    
    with DatabaseManager() as db:
        article = Article(
            title=article_data['title'],
            authors=article_data['authors'],
            doi=article_data['doi'],
            platform="PubMed",
            publication_date=article_data['pubdate'],
            abstract=article_data['abstract'],
            url=article_data['url'],
            status="VALIDADO" if validated else "NOVO"
        )
        
        article_id = db.create_article(article)
        
        # Se não passou na validação, registrar erro
        if not validated:
            error = ErrorLog(
                error_type="Rejeição de Conteúdo",
                article_title=article_data['title'],
                article_doi=article_data['doi'],
                platform="PubMed",
                error_reason="Nenhuma afiliação com HC-UFPE encontrada"
            )
            db.create_error_log(error)
```

---

## 🧪 PSEUDOCÓDIGO COMPLETO

```python
# processing/collectors/pubmed.py

class PubMedCollector:
    
    def __init__(self):
        self.db = DatabaseManager()
        Entrez.email = "tiago@example.com"
    
    def collect_and_save(self, search_term, date_start, date_end):
        """Pipeline completo"""
        
        print(f"🔍 Buscando '{search_term}' no PubMed...")
        
        # 1. Buscar no PubMed
        pmids = self.search_articles(search_term, date_start, date_end)
        print(f"   Encontrados {len(pmids)} artigos")
        
        # 2. Registrar busca no histórico
        with self.db as db:
            from database import SearchHistory
            search = SearchHistory(
                search_term=search_term,
                platforms="PubMed",
                date_start=date_start,
                date_end=date_end,
                results_count=len(pmids)
            )
            db.create_search_history(search)
        
        # 3. Para cada artigo
        validated_count = 0
        rejected_count = 0
        
        for pmid in pmids:
            try:
                # Obter detalhes
                article_data = self.fetch_article_details(pmid)
                
                # Validar afiliação
                validated = self.validate_affiliation(article_data)
                
                # Salvar no banco
                self.save_article(article_data, validated)
                
                if validated:
                    validated_count += 1
                else:
                    rejected_count += 1
                    
            except Exception as e:
                print(f"   ✗ Erro processando PMID {pmid}: {e}")
                rejected_count += 1
        
        print(f"   ✓ {validated_count} artigos VALIDADOS")
        print(f"   ✗ {rejected_count} artigos REJEITADOS")
```

---

## 🔗 COMO INTEGRAR COM A INTERFACE

No `main_window.py`, quando o usuário clica em "PESQUISAR":

```python
# Interface/main_window.py

def iniciar_busca(self):
    search_term = self.search_term_input.text()
    date_start = self.date_start_input.date().toString("yyyy-MM-dd")
    date_end = self.date_end_input.date().toString("yyyy-MM-dd")
    platforms = self.default_search_config['platforms']
    
    # Importar collector
    from processing.collectors.pubmed import PubMedCollector
    
    collector = PubMedCollector()
    
    # Se PubMed está selecionado
    if "PubMed" in platforms:
        collector.collect_and_save(search_term, date_start, date_end)
    
    # Depois mostrar resultados
    with DatabaseManager() as db:
        articles = db.read_articles_by_status("VALIDADO")
    
    self.open_results_window(articles)
```

---

## 📊 FLUXOGRAMA

```
┌─────────────────────────────────────────┐
│  Usuário clica "PESQUISAR" na GUI      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  PubMedCollector.collect_and_save()    │
│  search_term: "Hospital das Clínicas"  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  1. Buscar no PubMed (Entrez.esearch) │
│     → Retorna 500 PMIDs                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Registrar no Histórico              │
│     SearchHistory table                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Para cada PMID:                    │
│     - Obter detalhes (Entrez.efetch)  │
│     - Validar afiliação                │
│     - Salvar no BD                     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
    ✓ VALIDADO     ✗ REJEITADO
     (Salvar)      (Log erro)
       │                │
       └───────┬────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. Retornar artigos para GUI           │
│     db.read_articles_by_status()       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Mostrar resultados na tela             │
└─────────────────────────────────────────┘
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Instalar BIoPython: `pip install biopython`
- [ ] Criar `processing/collectors/pubmed.py`
- [ ] Implementar `search_articles()`
- [ ] Implementar `fetch_article_details()`
- [ ] Implementar `validate_affiliation()`
- [ ] Implementar `save_article()`
- [ ] Implementar `collect_and_save()`
- [ ] Testar com dados reais do PubMed
- [ ] Integrar com interface GUI
- [ ] Adicionar tratamento de erros
- [ ] Documentar a classe

---

## 🚀 TEMPO ESTIMADO

- Estudo da API Entrez: 30 min
- Implementação básica: 1-2 horas
- Testes: 30 min - 1 hora
- Integração com GUI: 30 min
- **Total: 2-4 horas**

---

## 📚 RECURSOS ÚTEIS

- [BIoPython Documentation](https://biopython.org/)
- [NCBI Entrez Tutorial](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
- [PubMed XML Structure](https://www.nlm.nih.gov/bsd/mms/medlinexml_structure.html)
- Documentação completa do CRUD: `DATABASE_CRUD_GUIDE.md`

---

## 💡 DICAS

1. **Teste localmente primeiro** com um único termo
2. **Use rate limiting** (NCBI pede esperar entre requisições)
3. **Trate timeouts** (conexão pode falhar)
4. **Cache resultados** se possível (economiza requisições)
5. **Registre erros** em ErrorLog para debug

---

## 🎓 EXEMPLO FINAL

```python
if __name__ == "__main__":
    collector = PubMedCollector()
    
    # Exemplo de busca
    collector.collect_and_save(
        search_term="Hospital das Clínicas UFPE",
        date_start="2023-01-01",
        date_end="2024-12-31"
    )
    
    # Verificar resultados
    with DatabaseManager() as db:
        stats = db.get_stats()
        print(f"Artigos salvos: {stats['articles_total']}")
```

---

**Pronto para começar? Boa sorte! 🚀**
