"""
Módulo de Database do NEXUS Pesquisa.
Expõe as classes principais para importação.

Ao importar este módulo, os dados padrão de afiliações são carregados
automaticamente na primeira execução (idempotente).
"""

from .db_manager import DatabaseManager, get_db
from .models import AffiliationVariation, Article, SearchHistory, ErrorLog
from .queries import SearchQueries, QueryBuilder
from .seed_data import seed_affiliation_variations

__all__ = [
    'DatabaseManager',
    'get_db',
    'AffiliationVariation',
    'Article',
    'SearchHistory',
    'ErrorLog',
    'SearchQueries',
    'QueryBuilder',
    'seed_affiliation_variations',
]

# Carregar dados padrão automaticamente na primeira importação
def _initialize_default_data():
    """Carrega dados padrão de afiliação na primeira execução."""
    try:
        with DatabaseManager() as db:
            seed_affiliation_variations(db)
    except Exception as e:
        print(f"[AVISO] Nao foi possivel carregar dados padrao: {e}")

# Executar na primeira importação
_initialize_default_data()
