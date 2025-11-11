"""
Exemplos de uso do CRUD do NEXUS Pesquisa.
Execute este arquivo para testar a funcionalidade do banco de dados.

Uso:
    python -m database.test_crud
"""

from datetime import datetime
from database.db_manager import DatabaseManager
from database.models import AffiliationVariation, Article, SearchHistory, ErrorLog


def test_affiliation_variations():
    """Testa CRUD de variações de afiliação."""
    print("\n" + "="*60)
    print("TESTANDO: AFFILIATION VARIATIONS")
    print("="*60)

    with DatabaseManager() as db:
        # CREATE
        print("\n1. CRIANDO variações de afiliação...")
        var1 = AffiliationVariation(
            original_text="HC*EBSERH",
            normalized_text="Hospital das Clínicas EBSERH",
            institution="HC-UFPE",
            platform="PubMed"
        )
        id1 = db.create_affiliation_variation(var1)

        var2 = AffiliationVariation(
            original_text='"HC*UFPE"',
            normalized_text="Hospital das Clínicas - UFPE",
            institution="HC-UFPE",
            platform="Scielo"
        )
        id2 = db.create_affiliation_variation(var2)

        # READ
        print("\n2. LENDO variação por ID...")
        read_var = db.read_affiliation_variation(id1)
        print(f"   Encontrado: {read_var}")

        print("\n3. LENDO TODAS as variações...")
        all_vars = db.read_all_affiliation_variations()
        print(f"   Total: {len(all_vars)} variações")
        for v in all_vars:
            print(f"   - {v}")

        print("\n4. FILTRANDO por instituição...")
        hc_vars = db.read_affiliation_variations_by_institution("HC-UFPE")
        print(f"   Encontradas {len(hc_vars)} variações para HC-UFPE")

        # UPDATE
        print("\n5. ATUALIZANDO variação...")
        var1.normalized_text = "Hospital das Clínicas - Universidade Federal de Pernambuco"
        db.update_affiliation_variation(var1)

        # DELETE
        print("\n6. DELETANDO variação...")
        db.delete_affiliation_variation(id2)


def test_articles():
    """Testa CRUD de artigos."""
    print("\n" + "="*60)
    print("TESTANDO: ARTICLES")
    print("="*60)

    with DatabaseManager() as db:
        # CREATE
        print("\n1. CRIANDO artigos...")
        art1 = Article(
            title="Clinical and laboratory profiles with suspected dengue",
            authors="Marinho, P. E. M., et al.",
            doi="10.1177/03000605211048865",
            platform="PubMed",
            publication_date="2022-01-15",
            abstract="Este estudo analisou perfis de infecção...",
            url="https://pubmed.ncbi.nlm.nih.gov/34719912/",
            status="VALIDADO"
        )
        id1 = db.create_article(art1)

        art2 = Article(
            title="Medication use among elderly patients",
            authors="Silva, A. C., Santos, R. F.",
            doi="10.1590/0104-1169.1111",
            platform="Scielo",
            publication_date="2023-05-20",
            abstract="Estudo qualitativo sobre polifarmácia...",
            url="https://www.scielo.br/",
            status="NOVO"
        )
        id2 = db.create_article(art2)

        # READ
        print("\n2. LENDO artigos VALIDADOS...")
        validated = db.read_articles_by_status("VALIDADO")
        print(f"   Encontrados: {len(validated)} artigos validados")

        print("\n3. LENDO artigos NOVOS...")
        new_articles = db.read_articles_by_status("NOVO")
        print(f"   Encontrados: {len(new_articles)} artigos novos")

        # UPDATE
        print("\n4. ATUALIZANDO status de artigo...")
        db.update_article_status(id2, "VALIDADO")


def test_search_history():
    """Testa registro de histórico de buscas."""
    print("\n" + "="*60)
    print("TESTANDO: SEARCH HISTORY")
    print("="*60)

    with DatabaseManager() as db:
        # CREATE
        print("\n1. REGISTRANDO buscas no histórico...")
        search1 = SearchHistory(
            search_term="Polifarmácia idosos",
            platforms="Scielo,PubMed",
            date_start="2023-01-01",
            date_end="2024-01-01",
            results_count=45
        )
        id1 = db.create_search_history(search1)

        search2 = SearchHistory(
            search_term="Hospital das Clínicas",
            platforms="Lilacs",
            date_start="2020-01-01",
            date_end="2024-01-01",
            results_count=120
        )
        id2 = db.create_search_history(search2)

        # READ
        print("\n2. LENDO histórico de buscas...")
        history = db.read_search_history(limit=10)
        print(f"   Encontradas {len(history)} buscas")
        for s in history:
            print(f"   - '{s.search_term}' ({s.results_count} resultados)")


def test_error_logs():
    """Testa registro de logs de erro."""
    print("\n" + "="*60)
    print("TESTANDO: ERROR LOGS")
    print("="*60)

    with DatabaseManager() as db:
        # CREATE
        print("\n1. REGISTRANDO erros...")
        error1 = ErrorLog(
            error_type="Rejeição de Conteúdo",
            search_term="Polifarmácia",
            article_title="Dados de 2018",
            article_doi="N/A",
            platform="Lilacs",
            error_reason="Artigo fora do período configurado"
        )
        id1 = db.create_error_log(error1)

        error2 = ErrorLog(
            error_type="Erro de Conexão",
            search_term="HC-UFPE",
            article_title="N/A",
            article_doi="N/A",
            platform="PubMed",
            error_reason="Timeout na conexão com a API"
        )
        id2 = db.create_error_log(error2)

        # READ
        print("\n2. LENDO logs de erro...")
        errors = db.read_error_logs(limit=10)
        print(f"   Encontrados {len(errors)} erros")
        for e in errors:
            print(f"   - {e.error_type} ({e.platform}): {e.error_reason}")


def test_stats():
    """Testa função de estatísticas."""
    print("\n" + "="*60)
    print("TESTANDO: STATISTICS")
    print("="*60)

    with DatabaseManager() as db:
        stats = db.get_stats()
        print("\nEstatísticas do Banco de Dados:")
        print(f"  Variações de Afiliação: {stats['affiliation_variations']}")
        print(f"  Total de Artigos: {stats['articles_total']}")
        print(f"  Artigos Validados: {stats['articles_validated']}")
        print(f"  Buscas Registradas: {stats['searches']}")
        print(f"  Erros Registrados: {stats['errors']}")


def main():
    """Executa todos os testes."""
    print("\n")
    print("=" * 60)
    print("  TESTE COMPLETO DO CRUD - NEXUS PESQUISA".center(60))
    print("=" * 60)

    try:
        test_affiliation_variations()
        test_articles()
        test_search_history()
        test_error_logs()
        test_stats()

        print("\n" + "="*60)
        print("[OK] TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERRO] ERRO durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
