"""
Exemplo de Integração CRUD com PubMed.
Este arquivo mostra como usar o CRUD para salvar dados do PubMed.

Para implementar a coleta real, você precisará:
1. Instalar: pip install biopython
2. Importar: from Bio import Entrez
3. Fazer requisições à API PubMed
"""

from datetime import datetime
from database import DatabaseManager, Article, SearchHistory, ErrorLog

# =====================================================================
# EXEMPLO: Simular coleta de dados do PubMed e salvar no BD
# =====================================================================

def save_pubmed_articles_to_db(articles_data: list):
    """
    Exemplo de como salvar artigos coletados do PubMed no banco de dados.
    
    Args:
        articles_data: Lista de dicionários com dados dos artigos
    
    Exemplo de estrutura esperada:
    [
        {
            "title": "Título do artigo",
            "authors": "Autor 1, Autor 2",
            "doi": "10.1234/example",
            "publication_date": "2024-01-15",
            "abstract": "Resumo...",
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
            "validated": True  # Opcional: se foi validado pelo critério de afiliação
        },
        ...
    ]
    """
    
    with DatabaseManager() as db:
        saved_count = 0
        error_count = 0
        
        for article_data in articles_data:
            try:
                # Criar objeto Article
                article = Article(
                    title=article_data.get("title", ""),
                    authors=article_data.get("authors", ""),
                    doi=article_data.get("doi", ""),
                    platform="PubMed",
                    publication_date=article_data.get("publication_date"),
                    abstract=article_data.get("abstract", ""),
                    url=article_data.get("url", ""),
                    status="VALIDADO" if article_data.get("validated", False) else "NOVO",
                    collected_at=datetime.now()
                )
                
                # Salvar no banco
                article_id = db.create_article(article)
                saved_count += 1
                
            except Exception as e:
                error_count += 1
                # Registrar erro no log
                error = ErrorLog(
                    error_type="Erro ao Salvar Artigo",
                    search_term=article_data.get("title", "N/A"),
                    article_title=article_data.get("title", ""),
                    platform="PubMed",
                    error_reason=str(e)
                )
                db.create_error_log(error)
                print(f"  ✗ Erro salvando artigo: {e}")
        
        print(f"  ✓ {saved_count} artigos salvos")
        print(f"  ✗ {error_count} erros")
        
        return saved_count, error_count


def log_search_to_history(search_term: str, platforms: list, date_start: str, 
                         date_end: str, results_count: int):
    """
    Registra uma busca no histórico.
    
    Args:
        search_term: Termo buscado
        platforms: Lista de plataformas
        date_start: Data inicial (formato: YYYY-MM-DD)
        date_end: Data final (formato: YYYY-MM-DD)
        results_count: Número de resultados encontrados
    """
    
    with DatabaseManager() as db:
        search = SearchHistory(
            search_term=search_term,
            platforms=",".join(platforms),
            date_start=date_start,
            date_end=date_end,
            results_count=results_count,
            search_date=datetime.now()
        )
        
        search_id = db.create_search_history(search)
        print(f"✓ Busca registrada no histórico (ID: {search_id})")
        
        return search_id


def handle_validation_error(article_title: str, article_doi: str, 
                           search_term: str, error_reason: str):
    """
    Registra artigos rejeitados no log de erros.
    
    Args:
        article_title: Título do artigo
        article_doi: DOI do artigo
        search_term: Termo de busca que encontrou o artigo
        error_reason: Motivo da rejeição
    """
    
    with DatabaseManager() as db:
        error = ErrorLog(
            error_type="Rejeição de Conteúdo",
            search_term=search_term,
            article_title=article_title,
            article_doi=article_doi,
            platform="PubMed",
            error_reason=error_reason
        )
        
        error_id = db.create_error_log(error)
        print(f"✓ Erro registrado no log (ID: {error_id}): {error_reason}")
        
        return error_id


# =====================================================================
# EXEMPLO DE USO PRÁTICO
# =====================================================================

if __name__ == "__main__":
    
    print("=" * 60)
    print("EXEMPLO: Integração CRUD com PubMed")
    print("=" * 60)
    
    # Dados simulados de artigos coletados do PubMed
    simulated_pubmed_articles = [
        {
            "title": "Clinical outcomes of patients with COVID-19 in a Brazilian hospital",
            "authors": "Silva, A. C.; Santos, R. F.; Costa, L.",
            "doi": "10.1234/example.001",
            "publication_date": "2023-06-15",
            "abstract": "Estudo sobre resultados clínicos de pacientes com COVID-19...",
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
            "validated": True  # Passou na validação de afiliação
        },
        {
            "title": "Drug interactions in elderly patients with comorbidities",
            "authors": "Martins, P. E.; Oliveira, J. S.",
            "doi": "10.1234/example.002",
            "publication_date": "2023-07-20",
            "abstract": "Investigação sobre interações medicamentosas...",
            "url": "https://pubmed.ncbi.nlm.nih.gov/87654321/",
            "validated": True
        },
        {
            "title": "International survey on telemedicine practices",
            "authors": "Johnson, M.; Williams, K.",
            "doi": "10.1234/example.003",
            "publication_date": "2023-05-10",
            "abstract": "Survey internacional sobre telemedicina...",
            "url": "https://pubmed.ncbi.nlm.nih.gov/11111111/",
            "validated": False  # Falhou na validação (sem afiliação HC-UFPE)
        }
    ]
    
    print("\n1. SALVANDO ARTIGOS DO PUBMED...")
    saved, errors = save_pubmed_articles_to_db(simulated_pubmed_articles)
    
    print("\n2. REGISTRANDO BUSCA NO HISTÓRICO...")
    log_search_to_history(
        search_term="Hospital das Clínicas UFPE",
        platforms=["PubMed"],
        date_start="2023-01-01",
        date_end="2023-12-31",
        results_count=len(simulated_pubmed_articles)
    )
    
    print("\n3. REGISTRANDO ARTIGO REJEITADO...")
    handle_validation_error(
        article_title=simulated_pubmed_articles[2]["title"],
        article_doi=simulated_pubmed_articles[2]["doi"],
        search_term="Hospital das Clínicas UFPE",
        error_reason="Artigo não menciona afiliação com HC-UFPE ou EBSERH"
    )
    
    print("\n4. CONSULTANDO DADOS SALVOS...")
    with DatabaseManager() as db:
        all_articles = db.read_articles_by_status("VALIDADO")
        print(f"\nArtigos VALIDADOS: {len(all_articles)}")
        for art in all_articles:
            print(f"  - {art.title[:50]}...")
        
        errors = db.read_error_logs(limit=5)
        print(f"\nErros Registrados: {len(errors)}")
        for err in errors:
            print(f"  - {err.error_type}: {err.error_reason}")
        
        stats = db.get_stats()
        print(f"\nEstatísticas:")
        print(f"  Total de artigos: {stats['articles_total']}")
        print(f"  Artigos validados: {stats['articles_validated']}")
        print(f"  Buscas registradas: {stats['searches']}")
        print(f"  Erros: {stats['errors']}")
    
    print("\n" + "=" * 60)
    print("✓ EXEMPLO CONCLUÍDO COM SUCESSO!")
    print("=" * 60)


# =====================================================================
# PRÓXIMOS PASSOS:
# 
# 1. Implementar função real de coleta PubMed:
#    - Instalar: pip install biopython
#    - Usar Entrez.esearch() para buscar
#    - Usar Entrez.efetch() para obter detalhes
#    - Validar afiliações usando tabela affiliation_variations
#
# 2. Integrar com processing/collectors/pubmed.py
#
# 3. Chamar estas funções a partir da interface GUI
#
# =====================================================================
