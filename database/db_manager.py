"""
Gerenciador de Banco de Dados para NEXUS Pesquisa.
Responsável por todas as operações CRUD com o banco de dados SQLite.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import AffiliationVariation, Article, SearchHistory, ErrorLog

# Leitura centralizada da configuração (preparação para DATABASE_URL)
import config


class DatabaseManager:
    """
    Gerenciador central do banco de dados.
    Implementa CRUD para todas as tabelas principais.
    """

    def __init__(self, db_path: str = None):
        """
        Inicializa o gerenciador de BD.
        
        Args:
            db_path: Caminho do arquivo SQLite. Se None, usa 'nexus_pesquisa.db' na raiz do projeto.
        """
        # Se o usuário passou um caminho explicitamente, respeitamos.
        # Caso contrário, usamos a DATABASE_URL de `config.py` (com fallback
        # para sqlite local). Isso permite alterar para outro SGBD via
        # variável de ambiente no futuro sem mudar o código.
        if db_path is None:
            database_url = getattr(config, 'DATABASE_URL', None)
            # Se for URL SQLite, extraímos o caminho do arquivo
            if database_url and config.is_sqlite_url(database_url):
                db_path = config.sqlite_path_from_url(database_url)
            else:
                # Fallback para o arquivo local na raiz do projeto
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_path = os.path.join(project_root, "nexus_pesquisa.db")

        self.db_path = db_path
        # Flag para indicar que por ora estamos usando SQLite; caso futuramente
        # DATABASE_URL aponte para outro SGBD, recomenda-se refatorar para
        # SQLAlchemy/driver apropriado.
        self._using_sqlite = True
        self.connection = None
        self._initialize_db()

    def _initialize_db(self):
        """Cria as tabelas se não existirem."""
        # As rotinas de criação atuais usam SQLite. Se no futuro migrarmos
        # para Postgres/MySQL, substitua esta rotina por uma criação via
        # SQLAlchemy/Alembic ou scripts SQL compatíveis com o novo SGBD.
        self.connect()
        cursor = self.connection.cursor()

        # Tabela de Variações de Afiliação
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affiliation_variations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                normalized_text TEXT NOT NULL,
                institution TEXT NOT NULL,
                platform TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de Artigos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT,
                doi TEXT,
                platform TEXT NOT NULL,
                publication_date TEXT,
                abstract TEXT,
                url TEXT,
                status TEXT DEFAULT 'NOVO',
                collected_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de Histórico de Buscas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT NOT NULL,
                platforms TEXT,
                date_start TEXT,
                date_end TEXT,
                results_count INTEGER DEFAULT 0,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de Histórico de Erros
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                search_term TEXT,
                article_title TEXT,
                article_doi TEXT,
                platform TEXT,
                error_reason TEXT,
                error_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()
        print(f"[OK] Banco de dados inicializado em: {self.db_path}")

    def connect(self):
        """Conecta ao banco de dados."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Retorna resultados como dicionários
        return self.connection

    def close(self):
        """Fecha a conexão com o banco."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager: entrada."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: saída."""
        self.close()

    # ==================== CRUD: AFFILIATION VARIATIONS ====================

    def create_affiliation_variation(self, variation: AffiliationVariation) -> int:
        """
        Cria uma nova variação de afiliação.
        
        Args:
            variation: Objeto AffiliationVariation com os dados.
            
        Returns:
            ID da variação criada.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO affiliation_variations 
            (original_text, normalized_text, institution, platform, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            variation.original_text,
            variation.normalized_text,
            variation.institution,
            variation.platform,
            variation.created_at or datetime.now(),
            variation.updated_at or datetime.now()
        ))
        self.connection.commit()
        print(f"[OK] Variacao de afiliacao criada: {variation.original_text}")
        return cursor.lastrowid

    def read_affiliation_variation(self, variation_id: int) -> Optional[AffiliationVariation]:
        """
        Lê uma variação de afiliação pelo ID.
        
        Args:
            variation_id: ID da variação.
            
        Returns:
            Objeto AffiliationVariation ou None se não encontrado.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM affiliation_variations WHERE id = ?", (variation_id,))
        row = cursor.fetchone()
        
        if row:
            return AffiliationVariation(
                id=row['id'],
                original_text=row['original_text'],
                normalized_text=row['normalized_text'],
                institution=row['institution'],
                platform=row['platform'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
        return None

    def read_all_affiliation_variations(self) -> List[AffiliationVariation]:
        """
        Lê todas as variações de afiliação.
        
        Returns:
            Lista de objetos AffiliationVariation.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM affiliation_variations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        variations = []
        for row in rows:
            variations.append(AffiliationVariation(
                id=row['id'],
                original_text=row['original_text'],
                normalized_text=row['normalized_text'],
                institution=row['institution'],
                platform=row['platform'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            ))
        return variations

    def read_affiliation_variations_by_institution(self, institution: str) -> List[AffiliationVariation]:
        """
        Lê variações de afiliação filtradas por instituição.
        
        Args:
            institution: Nome da instituição (ex: "HC-UFPE").
            
        Returns:
            Lista de AffiliationVariation.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM affiliation_variations WHERE institution = ? ORDER BY created_at DESC",
            (institution,)
        )
        rows = cursor.fetchall()
        
        variations = []
        for row in rows:
            variations.append(AffiliationVariation(
                id=row['id'],
                original_text=row['original_text'],
                normalized_text=row['normalized_text'],
                institution=row['institution'],
                platform=row['platform'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            ))
        return variations

    def update_affiliation_variation(self, variation: AffiliationVariation) -> bool:
        """
        Atualiza uma variação de afiliação.
        
        Args:
            variation: Objeto AffiliationVariation com ID e dados novos.
            
        Returns:
            True se atualizado, False se não encontrado.
        """
        cursor = self.connection.cursor()
        variation.updated_at = datetime.now()
        
        cursor.execute("""
            UPDATE affiliation_variations 
            SET original_text = ?, normalized_text = ?, institution = ?, platform = ?, updated_at = ?
            WHERE id = ?
        """, (
            variation.original_text,
            variation.normalized_text,
            variation.institution,
            variation.platform,
            variation.updated_at,
            variation.id
        ))
        self.connection.commit()
        
        if cursor.rowcount > 0:
            print(f"[OK] Variacao de afiliacao atualizada: {variation.original_text}")
            return True
        return False

    def delete_affiliation_variation(self, variation_id: int) -> bool:
        """
        Deleta uma variação de afiliação.
        
        Args:
            variation_id: ID da variação.
            
        Returns:
            True se deletado, False se não encontrado.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM affiliation_variations WHERE id = ?", (variation_id,))
        self.connection.commit()
        
        if cursor.rowcount > 0:
            print(f"[OK] Variacao de afiliacao deletada (ID: {variation_id})")
            return True
        return False

    # ==================== CRUD: ARTICLES ====================

    def create_article(self, article: Article) -> int:
        """
        Cria um novo artigo.
        
        Args:
            article: Objeto Article com os dados.
            
        Returns:
            ID do artigo criado.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO articles 
            (title, authors, doi, platform, publication_date, abstract, url, status, collected_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.title,
            article.authors,
            article.doi,
            article.platform,
            article.publication_date,
            article.abstract,
            article.url,
            article.status,
            article.collected_at or datetime.now(),
            article.created_at or datetime.now()
        ))
        self.connection.commit()
        print(f"[OK] Artigo criado: {article.title[:50]}...")
        return cursor.lastrowid

    def read_articles_by_status(self, status: str) -> List[Article]:
        """
        Lê artigos filtrados por status.
        
        Args:
            status: Status desejado (NOVO, VALIDADO, REJEITADO).
            
        Returns:
            Lista de Articles.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE status = ? ORDER BY created_at DESC", (status,))
        rows = cursor.fetchall()
        
        articles = []
        for row in rows:
            articles.append(Article(
                id=row['id'],
                title=row['title'],
                authors=row['authors'],
                doi=row['doi'],
                platform=row['platform'],
                publication_date=datetime.fromisoformat(row['publication_date']) if row['publication_date'] else None,
                abstract=row['abstract'],
                url=row['url'],
                status=row['status'],
                collected_at=datetime.fromisoformat(row['collected_at']) if row['collected_at'] else None,
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            ))
        return articles

    def read_article_by_platform_and_doi(self, platform: str, doi: str) -> Optional[Article]:
        """
        Procura um artigo pelo par (platform, doi).

        Retorna o objeto Article se encontrado, caso contrário None.
        """
        if not doi:
            return None
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE platform = ? AND doi = ? LIMIT 1", (platform, doi))
        row = cursor.fetchone()
        if not row:
            return None
        return Article(
            id=row['id'],
            title=row['title'],
            authors=row['authors'],
            doi=row['doi'],
            platform=row['platform'],
            publication_date=datetime.fromisoformat(row['publication_date']) if row['publication_date'] else None,
            abstract=row['abstract'],
            url=row['url'],
            status=row['status'],
            collected_at=datetime.fromisoformat(row['collected_at']) if row['collected_at'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def read_article_by_platform_and_url(self, platform: str, url: str) -> Optional[Article]:
        """
        Procura um artigo pelo par (platform, url).

        Retorna o objeto Article se encontrado, caso contrário None.
        """
        if not url:
            return None
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE platform = ? AND url = ? LIMIT 1", (platform, url))
        row = cursor.fetchone()
        if not row:
            return None
        return Article(
            id=row['id'],
            title=row['title'],
            authors=row['authors'],
            doi=row['doi'],
            platform=row['platform'],
            publication_date=datetime.fromisoformat(row['publication_date']) if row['publication_date'] else None,
            abstract=row['abstract'],
            url=row['url'],
            status=row['status'],
            collected_at=datetime.fromisoformat(row['collected_at']) if row['collected_at'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def update_article_status(self, article_id: int, new_status: str) -> bool:
        """
        Atualiza o status de um artigo.
        
        Args:
            article_id: ID do artigo.
            new_status: Novo status (NOVO, VALIDADO, REJEITADO).
            
        Returns:
            True se atualizado, False se não encontrado.
        """
        cursor = self.connection.cursor()
        cursor.execute("UPDATE articles SET status = ? WHERE id = ?", (new_status, article_id))
        self.connection.commit()
        
        if cursor.rowcount > 0:
            print(f"[OK] Status do artigo atualizado: {article_id} -> {new_status}")
            return True
        return False

    # ==================== CRUD: SEARCH HISTORY ====================

    def create_search_history(self, search: SearchHistory) -> int:
        """
        Registra uma nova busca no histórico.
        
        Args:
            search: Objeto SearchHistory com os dados.
            
        Returns:
            ID do registro criado.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO search_history 
            (search_term, platforms, date_start, date_end, results_count, search_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            search.search_term,
            search.platforms,
            search.date_start,
            search.date_end,
            search.results_count,
            search.search_date or datetime.now()
        ))
        self.connection.commit()
        print(f"[OK] Busca registrada no historico: '{search.search_term}'")
        return cursor.lastrowid

    def read_search_history(self, limit: int = 50) -> List[SearchHistory]:
        """
        Lê o histórico de buscas.
        
        Args:
            limit: Número máximo de registros (padrão 50).
            
        Returns:
            Lista de SearchHistory.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM search_history 
            ORDER BY search_date DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        searches = []
        for row in rows:
            searches.append(SearchHistory(
                id=row['id'],
                search_term=row['search_term'],
                platforms=row['platforms'],
                date_start=datetime.fromisoformat(row['date_start']) if row['date_start'] else None,
                date_end=datetime.fromisoformat(row['date_end']) if row['date_end'] else None,
                results_count=row['results_count'],
                search_date=datetime.fromisoformat(row['search_date']) if row['search_date'] else None
            ))
        return searches

    # ==================== CRUD: ERROR LOGS ====================

    def create_error_log(self, error: ErrorLog) -> int:
        """
        Registra um novo erro no log.
        
        Args:
            error: Objeto ErrorLog com os dados.
            
        Returns:
            ID do registro criado.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO error_logs 
            (error_type, search_term, article_title, article_doi, platform, error_reason, error_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            error.error_type,
            error.search_term,
            error.article_title,
            error.article_doi,
            error.platform,
            error.error_reason,
            error.error_date or datetime.now().isoformat(),
            error.created_at or datetime.now()
        ))
        self.connection.commit()
        print(f"[OK] Erro registrado no log: {error.error_type}")
        return cursor.lastrowid

    def read_error_logs(self, limit: int = 50) -> List[ErrorLog]:
        """
        Lê o histórico de erros.
        
        Args:
            limit: Número máximo de registros (padrão 50).
            
        Returns:
            Lista de ErrorLog.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM error_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        errors = []
        for row in rows:
            errors.append(ErrorLog(
                id=row['id'],
                error_type=row['error_type'],
                search_term=row['search_term'],
                article_title=row['article_title'],
                article_doi=row['article_doi'],
                platform=row['platform'],
                error_reason=row['error_reason'],
                error_date=datetime.fromisoformat(row['error_date']) if row['error_date'] else None,
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            ))
        return errors

    # ==================== UTILITÁRIOS ====================

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais do banco de dados.
        
        Returns:
            Dicionário com contagens de registros por tabela.
        """
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM affiliation_variations")
        aff_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM articles")
        articles_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM articles WHERE status = 'VALIDADO'")
        validated_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM search_history")
        searches_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM error_logs")
        errors_count = cursor.fetchone()['count']
        
        return {
            'affiliation_variations': aff_count,
            'articles_total': articles_count,
            'articles_validated': validated_count,
            'searches': searches_count,
            'errors': errors_count
        }

    def clear_database(self):
        """
        [AVISO] Limpa TODAS as tabelas. Use com cuidado!
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM affiliation_variations")
        cursor.execute("DELETE FROM articles")
        cursor.execute("DELETE FROM search_history")
        cursor.execute("DELETE FROM error_logs")
        self.connection.commit()
        print("[AVISO] Banco de dados limpo!")


# Função auxiliar para uso simples
def get_db(db_path: str = None) -> DatabaseManager:
    """
    Factory function para criar instância do DatabaseManager.
    
    Args:
        db_path: Caminho customizado do BD (opcional).
        
    Returns:
        Instância de DatabaseManager.
    """
    return DatabaseManager(db_path)
