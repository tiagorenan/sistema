"""
Gerenciador de Banco de Dados para NEXUS Pesquisa.
Responsável por todas as operações CRUD com o banco de dados SQLite.
"""

import sqlite3
import os
from datetime import datetime, date # Importado 'date' para tipagem, 'datetime' para parse
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
        """
        if db_path is None:
            database_url = getattr(config, 'DATABASE_URL', None)
            if database_url and config.is_sqlite_url(database_url):
                db_path = config.sqlite_path_from_url(database_url)
            else:
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_path = os.path.join(project_root, "nexus_pesquisa.db")

        self.db_path = db_path
        self._using_sqlite = True
        self.connection = None
        self._initialize_db()

    def _initialize_db(self):
        """Cria as tabelas se não existirem."""
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
                search_date TEXT
            )
        """)
        # NOTA: O campo search_date foi alterado para TEXT para refletir o formato
        # usado no INSERT e evitar conflitos.

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
        """Cria uma nova variação de afiliação."""
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
            variation.created_at or datetime.now().isoformat(),
            variation.updated_at or datetime.now().isoformat()
        ))
        self.connection.commit()
        print(f"[OK] Variacao de afiliacao criada: {variation.original_text}")
        return cursor.lastrowid

    def read_affiliation_variation(self, variation_id: int) -> Optional[AffiliationVariation]:
        """Lê uma variação de afiliação pelo ID."""
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
        """Lê todas as variações de afiliação."""
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
        """Lê variações de afiliação filtradas por instituição."""
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
        """Atualiza uma variação de afiliação."""
        cursor = self.connection.cursor()
        variation.updated_at = datetime.now().isoformat()
        
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
        """Deleta uma variação de afiliação."""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM affiliation_variations WHERE id = ?", (variation_id,))
        self.connection.commit()
        
        if cursor.rowcount > 0:
            print(f"[OK] Variacao de afiliacao deletada (ID: {variation_id})")
            return True
        return False

    # ==================== CRUD: ARTICLES ====================

    def create_article(self, article: Article) -> int:
        """Cria um novo artigo."""
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
            article.collected_at or datetime.now().isoformat(),
            article.created_at or datetime.now().isoformat()
        ))
        self.connection.commit()
        print(f"[OK] Artigo criado: {article.title[:50]}...")
        return cursor.lastrowid

    def read_articles_by_status(self, status: str) -> List[dict]: # Mudança no tipo de retorno para dict
        """
        Lê artigos filtrados por status e os mapeia para uma lista de dicionários
        com chaves em Português para a UI.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE status = ? ORDER BY created_at DESC", (status,))
        rows = cursor.fetchall()
        
        def safe_iso_parse(dt_str):
            # Função auxiliar (pode estar definida globalmente no db_manager)
            return datetime.fromisoformat(dt_str) if dt_str else None
        
        articles_data = [] # Lista para armazenar dicionários
        
        for row in rows:
            # CORREÇÃO: Mapeia o objeto de banco de dados (row) diretamente para o dicionário da UI (Português)
            articles_data.append({
                'id': row['id'], 
                'titulo': row['title'],
                'autores': row['authors'] or 'N/A',
                'doi': row['doi'] or 'N/A',
                # Concatena a data de publicação e a plataforma
                'publicacao': f"{row['publication_date']} ({row['platform']})", 
                'resumo': row['abstract'] or 'Resumo indisponível.',
                'link': row['url'] or '#',
                'status': row['status']
            })
        return articles_data # Retorna a lista de dicionários!

    def read_article_by_platform_and_doi(self, platform: str, doi: str) -> Optional[Article]:
        """Procura um artigo pelo par (platform, doi)."""
        if not doi:
            return None
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE platform = ? AND doi = ? LIMIT 1", (platform, doi))
        row = cursor.fetchone()
        if not row:
            return None
            
        def safe_iso_parse(dt_str):
            return datetime.fromisoformat(dt_str) if dt_str else None
            
        return Article(
            id=row['id'],
            title=row['title'],
            authors=row['authors'],
            doi=row['doi'],
            platform=row['platform'],
            publication_date=row['publication_date'],
            abstract=row['abstract'],
            url=row['url'],
            status=row['status'],
            collected_at=safe_iso_parse(row['collected_at']),
            created_at=safe_iso_parse(row['created_at'])
        )

    def read_article_by_platform_and_url(self, platform: str, url: str) -> Optional[Article]:
        """Procura um artigo pelo par (platform, url)."""
        if not url:
            return None
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE platform = ? AND url = ? LIMIT 1", (platform, url))
        row = cursor.fetchone()
        if not row:
            return None
            
        def safe_iso_parse(dt_str):
            return datetime.fromisoformat(dt_str) if dt_str else None
            
        return Article(
            id=row['id'],
            title=row['title'],
            authors=row['authors'],
            doi=row['doi'],
            platform=row['platform'],
            publication_date=row['publication_date'],
            abstract=row['abstract'],
            url=row['url'],
            status=row['status'],
            collected_at=safe_iso_parse(row['collected_at']),
            created_at=safe_iso_parse(row['created_at'])
        )

    def update_article_status(self, article_id: int, new_status: str) -> bool:
        """Atualiza o status de um artigo."""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE articles SET status = ? WHERE id = ?", (new_status, article_id))
        self.connection.commit()
        
        if cursor.rowcount > 0:
            print(f"[OK] Status do artigo atualizado: {article_id} -> {new_status}")
            return True
        return False

    # ==================== CRUD: SEARCH HISTORY ====================

    def create_search_history(self, search: SearchHistory) -> int:
        """Registra uma nova busca no histórico."""
        cursor = self.connection.cursor()
        # Converte a data da busca para string no formato correto para SQLite (ISO)
        search_date_str = search.search_date.isoformat() if isinstance(search.search_date, datetime) else datetime.now().isoformat()
        
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
            search_date_str # Salvando em formato ISO para consistência
        ))
        self.connection.commit()
        print(f"[OK] Busca registrada no historico: '{search.search_term}'")
        return cursor.lastrowid

    def read_search_history(self, limit: int = 50) -> List[SearchHistory]:
        """
        Lê o histórico de buscas.
        
        CORREÇÃO: Implementa o parse manual para o formato DD/MM/YYYY, 
        que causava o erro Invalid isoformat string.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM search_history 
            ORDER BY search_date DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        def parse_date_safely(date_str):
            if date_str:
                if isinstance(date_str, datetime):
                    return date_str # Já é um objeto datetime
                
                # 1. Tenta parsear o formato DD/MM/YYYY (Formato problemático do seu DB)
                try:
                    return datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    # 2. Tenta parsear o formato ISO 8601 (Formato esperado do Python)
                    try:
                        return datetime.fromisoformat(date_str)
                    except ValueError:
                        # 3. Falha e retorna None
                        return None
            return None

        searches = []
        for row in rows:
            searches.append(SearchHistory(
                id=row['id'],
                search_term=row['search_term'],
                platforms=row['platforms'],
                # Aplica o parse em todos os campos de data
                date_start=parse_date_safely(row['date_start']),
                date_end=parse_date_safely(row['date_end']),
                results_count=row['results_count'],
                search_date=parse_date_safely(row['search_date'])
            ))
        return searches

    def read_articles_for_search(self, search_id: int) -> List[Article]:
        """
        Lê todos os artigos validados (VALIDADO) como fallback para
        uma consulta de histórico específica, já que o esquema do DB não tem 'search_id'
        na tabela 'articles'.
        """
        return self.read_articles_by_status('VALIDADO')
    
    # ==================== CRUD: ERROR LOGS ====================

    def create_error_log(self, error: ErrorLog) -> int:
        """Registra um novo erro no log."""
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
            error.error_date.isoformat() if isinstance(error.error_date, (datetime, date)) else None,
            error.created_at.isoformat() if isinstance(error.created_at, (datetime, date)) else datetime.now().isoformat()
        ))
        self.connection.commit()
        print(f"[OK] Erro registrado no log: {error.error_type}")
        return cursor.lastrowid

    def read_error_logs(self, limit: int = 50) -> List[ErrorLog]:
        """Lê o histórico de erros."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM error_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        def safe_iso_parse(dt_str):
            return datetime.fromisoformat(dt_str) if dt_str else None
            
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
                error_date=safe_iso_parse(row['error_date']),
                created_at=safe_iso_parse(row['created_at'])
            ))
        return errors

    # ==================== UTILITÁRIOS ====================

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do banco de dados."""
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
        """[AVISO] Limpa TODAS as tabelas. Use com cuidado!"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM affiliation_variations")
        cursor.execute("DELETE FROM articles")
        cursor.execute("DELETE FROM search_history")
        cursor.execute("DELETE FROM error_logs")
        self.connection.commit()
        print("[AVISO] Banco de dados limpo!")


# Função auxiliar para uso simples
def get_db(db_path: str = None) -> DatabaseManager:
    """Factory function para criar instância do DatabaseManager."""
    return DatabaseManager(db_path)