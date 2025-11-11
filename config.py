
"""
Configurações do projeto.

Centraliza a configuração do banco de dados para permitir fácil migração
para containers/serviços (ex: Postgres) no futuro.

Formato recomendado de `DATABASE_URL`:
 - SQLite (fallback): sqlite:///c:/caminho/para/nexus_pesquisa.db
 - Postgres: postgresql://user:pass@host:5432/dbname

Se `DATABASE_URL` não estiver definida, o código usa um arquivo SQLite
local em `nexus_pesquisa.db` (na raiz do projeto).
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# Lê a variável de ambiente DATABASE_URL (opcional)
# Exemplos:
#   sqlite:///C:/path/to/nexus_pesquisa.db
#   postgresql://user:pass@db:5432/nexus_db
DATABASE_URL = os.environ.get(
	'DATABASE_URL',
	f"sqlite:///{BASE_DIR / 'nexus_pesquisa.db'}"
)


def is_sqlite_url(url: str) -> bool:
	"""Retorna True se a URL corresponder a um SQLite local (file-based)."""
	if not url:
		return False
	return url.startswith('sqlite:') or url.endswith('.db')


def sqlite_path_from_url(url: str) -> str:
	"""Extrai o caminho do arquivo .db de uma DATABASE_URL sqlite:///<path>.

	Se a URL não estiver no formato esperado, retorna caminho padrão.
	"""
	if not url:
		return str(BASE_DIR / 'nexus_pesquisa.db')

	# suportar formatos como sqlite:///C:/path/to/db.db
	if url.startswith('sqlite:///'):
		return url.replace('sqlite:///', '')

	# suporte simples: se terminar em .db, trate como caminho direto
	if url.endswith('.db'):
		return url

	return str(BASE_DIR / 'nexus_pesquisa.db')
