"""
Dados iniciais (seed) para o banco de dados.
Contém as variações padrão de nomes do Hospital das Clínicas - UFPE.

Estes dados são carregados automaticamente na primeira execução ou sob demanda.
"""

from .models import AffiliationVariation


# Variações de nomes para Hospital das Clínicas - UFPE / HC-UFPE / EBSERH
DEFAULT_AFFILIATIONS = [
    AffiliationVariation(
        original_text="Hospital das Clinicas - UFPE",
        normalized_text="Hospital das Clínicas - UFPE",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas - UFPE",
        normalized_text="Hospital das Clínicas - UFPE",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clinicas da UFPE",
        normalized_text="Hospital das Clínicas da UFPE",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas da UFPE",
        normalized_text="Hospital das Clínicas da UFPE",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="HC UFPE",
        normalized_text="HC UFPE",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="HC EBSERH",
        normalized_text="HC EBSERH",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Universidade Federal de Pernambuco hospital",
        normalized_text="Hospital - Universidade Federal de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clinicas - Universidade Federal de Pernambuco",
        normalized_text="Hospital das Clínicas - Universidade Federal de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas - Universidade Federal de Pernambuco",
        normalized_text="Hospital das Clínicas - Universidade Federal de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clinicas da Universidade Federal de Pernambuco",
        normalized_text="Hospital das Clínicas da Universidade Federal de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas da Universidade Federal de Pernambuco",
        normalized_text="Hospital das Clínicas da Universidade Federal de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clinicas, Universidade Federal de Pernambuco",
        normalized_text="Hospital das Clínicas, Universidade Federal de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas, Universidade Federal de Pernambuco",
        normalized_text="Hospital das Clínicas, Universidade Federal de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clinicas de Pernambuco",
        normalized_text="Hospital das Clínicas de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas de Pernambuco",
        normalized_text="Hospital das Clínicas de Pernambuco",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clinicas de Pernambuco-Empresa Brasileira de Servicos Hospitalares",
        normalized_text="Hospital das Clínicas de Pernambuco - EBSERH",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas de Pernambuco-Empresa Brasileira de Serviços Hospitalares",
        normalized_text="Hospital das Clínicas de Pernambuco - EBSERH",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clinicas/EBSER-UFPE",
        normalized_text="Hospital das Clínicas / EBSERH - UFPE",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Hospital das Clínicas/EBSER-UFPE",
        normalized_text="Hospital das Clínicas / EBSERH - UFPE",
        institution="HC-UFPE",
        platform="General"
    ),
    AffiliationVariation(
        original_text="Clinics Hospital of Pernambuco Federal University",
        normalized_text="Clinics Hospital of Pernambuco Federal University",
        institution="HC-UFPE",
        platform="General"
    ),
]


def seed_affiliation_variations(db_manager):
    """
    Popula a tabela de variações de afiliação com dados padrão.

    Usa um mecanismo idempotente: só insere se a tabela estiver vazia
    (verifica se já existe alguma variação para HC-UFPE).

    Args:
        db_manager: Instância de DatabaseManager já conectada.
    """
    # Verificar se já existem variações para HC-UFPE
    existing = db_manager.read_affiliation_variations_by_institution("HC-UFPE")

    if existing:
        print(f"✓ Dados de afiliação já existem ({len(existing)} variações). Pulando seed.")
        return

    print("📥 Carregando dados padrão de variações de afiliação...")
    inserted_count = 0

    for affiliation in DEFAULT_AFFILIATIONS:
        try:
            db_manager.create_affiliation_variation(affiliation)
            inserted_count += 1
        except Exception as e:
            print(f"  ⚠️ Erro ao inserir {affiliation.original_text}: {e}")

    print(f"✅ {inserted_count} variações de afiliação carregadas com sucesso!")


if __name__ == "__main__":
    # Script de teste: pode ser executado manualmente para recarregar dados
    from .db_manager import DatabaseManager

    with DatabaseManager() as db:
        seed_affiliation_variations(db)
