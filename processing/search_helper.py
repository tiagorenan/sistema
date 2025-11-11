"""
Módulo auxiliar para integração de busca com variações de afiliação.

Fornece funções para recuperar e usar os termos padrão cadastrados
na tabela affiliation_variations durante buscas no PubMed.
"""

from database import DatabaseManager


def get_search_terms_for_affiliation(institution: str = "HC-UFPE") -> list:
    """
    Recupera todos os termos de busca (variações) cadastrados para uma instituição.

    Args:
        institution: Nome da instituição (ex: "HC-UFPE").

    Returns:
        Lista de strings com os termos de busca.

    Exemplo:
        terms = get_search_terms_for_affiliation("HC-UFPE")
        # Retorna: ["Hospital das Clinicas - UFPE", "HC UFPE", ...]
    """
    try:
        with DatabaseManager() as db:
            variations = db.read_affiliation_variations_by_institution(institution)
            # Retornar os textos originais (como aparecem em artigos)
            return [v.original_text for v in variations]
    except Exception as e:
        print(f"⚠️ Erro ao recuperar termos de afiliação: {e}")
        return []


def format_search_query_for_pubmed(terms: list) -> str:
    """
    Formata uma lista de termos como query para busca no PubMed.

    Args:
        terms: Lista de strings de busca.

    Returns:
        String formatada como query PubMed (ex: (term1 OR term2 OR term3)).

    Exemplo:
        terms = ["HC UFPE", "Hospital das Clinicas - UFPE"]
        query = format_search_query_for_pubmed(terms)
        # Retorna: ("HC UFPE" OR "Hospital das Clinicas - UFPE")
    """
    if not terms:
        return ""

    # Adicionar aspas em cada termo e juntar com OR
    formatted = [f'"{term}"' for term in terms]
    return "(" + " OR ".join(formatted) + ")"


def validate_article_has_affiliation(article_abstract: str, article_affiliations: str = None,
                                     institution: str = "HC-UFPE") -> bool:
    """
    Verifica se um artigo contém alguma variação de afiliação cadastrada.

    Args:
        article_abstract: Texto do abstract do artigo.
        article_affiliations: Campo de afiliações do artigo (se disponível).
        institution: Instituição a verificar (ex: "HC-UFPE").

    Returns:
        True se alguma variação foi encontrada, False caso contrário.

    Exemplo:
        is_valid = validate_article_has_affiliation(
            article_abstract="...Hospital das Clinicas UFPE...",
            article_affiliations="...HC-UFPE...",
            institution="HC-UFPE"
        )
    """
    search_terms = get_search_terms_for_affiliation(institution)

    if not search_terms:
        return False

    # Juntar abstract e affiliations para buscar
    full_text = f"{article_abstract or ''} {article_affiliations or ''}".lower()

    # Verificar se algum termo está presente (case-insensitive)
    for term in search_terms:
        if term.lower() in full_text:
            return True

    return False


# =====================================================================
# Exemplo de uso (pode ser executado diretamente)
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO: Usando termos padrão de busca")
    print("=" * 60)

    # 1. Recuperar todos os termos
    terms = get_search_terms_for_affiliation("HC-UFPE")
    print(f"\n✓ Termos cadastrados para HC-UFPE: {len(terms)}")
    for i, term in enumerate(terms[:5], 1):
        print(f"  {i}. {term}")
    if len(terms) > 5:
        print(f"  ... e mais {len(terms) - 5} termos")

    # 2. Formatar como query PubMed
    query = format_search_query_for_pubmed(terms)
    print(f"\n✓ Query formatada para PubMed:")
    print(f"  {query[:100]}...")

    # 3. Validar um artigo
    test_abstract = "Study conducted at Hospital das Clinicas UFPE in Pernambuco"
    is_valid = validate_article_has_affiliation(test_abstract, institution="HC-UFPE")
    print(f"\n✓ Artigo teste válido? {is_valid}")

    print("\n" + "=" * 60)
