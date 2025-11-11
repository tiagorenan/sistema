"""
Queries SQL predefinidas para o NEXUS Pesquisa.
Centraliza todas as consultas complexas do banco de dados.
"""


class SearchQueries:
    """
    Classe com todas as queries SQL predefinidas.
    Use como referência ou execute diretamente via cursor.
    """

    # ==================== AFFILIATION VARIATIONS ====================

    AFFILIATION_SEARCH_BY_TEXT = """
    SELECT * FROM affiliation_variations 
    WHERE original_text LIKE ? OR normalized_text LIKE ?
    ORDER BY created_at DESC
    """

    AFFILIATION_COUNT_BY_INSTITUTION = """
    SELECT institution, COUNT(*) as count 
    FROM affiliation_variations 
    GROUP BY institution 
    ORDER BY count DESC
    """

    AFFILIATION_BY_PLATFORM = """
    SELECT * FROM affiliation_variations 
    WHERE platform = ?
    ORDER BY created_at DESC
    """

    # ==================== ARTICLES ====================

    ARTICLES_BY_PLATFORM_AND_DATE = """
    SELECT * FROM articles 
    WHERE platform = ? 
    AND publication_date BETWEEN ? AND ?
    ORDER BY publication_date DESC
    """

    ARTICLES_COUNT_BY_STATUS = """
    SELECT status, COUNT(*) as count 
    FROM articles 
    GROUP BY status
    """

    ARTICLES_SEARCH_BY_TITLE = """
    SELECT * FROM articles 
    WHERE title LIKE ? OR abstract LIKE ?
    ORDER BY created_at DESC
    """

    ARTICLES_BY_DOI = """
    SELECT * FROM articles 
    WHERE doi = ? 
    LIMIT 1
    """

    ARTICLES_DUPLICATES = """
    SELECT title, COUNT(*) as duplicates 
    FROM articles 
    GROUP BY title 
    HAVING duplicates > 1 
    ORDER BY duplicates DESC
    """

    # ==================== SEARCH HISTORY ====================

    SEARCH_HISTORY_BY_DATE_RANGE = """
    SELECT * FROM search_history 
    WHERE search_date BETWEEN ? AND ?
    ORDER BY search_date DESC
    """

    SEARCH_HISTORY_BY_TERM = """
    SELECT * FROM search_history 
    WHERE search_term LIKE ?
    ORDER BY search_date DESC
    """

    SEARCH_STATS_BY_PLATFORM = """
    SELECT platforms, COUNT(*) as total, AVG(results_count) as avg_results 
    FROM search_history 
    GROUP BY platforms 
    ORDER BY total DESC
    """

    MOST_USED_SEARCH_TERMS = """
    SELECT search_term, COUNT(*) as usage_count 
    FROM search_history 
    GROUP BY search_term 
    ORDER BY usage_count DESC 
    LIMIT 10
    """

    # ==================== ERROR LOGS ====================

    ERROR_LOGS_BY_TYPE = """
    SELECT error_type, COUNT(*) as count 
    FROM error_logs 
    GROUP BY error_type 
    ORDER BY count DESC
    """

    ERROR_LOGS_BY_DATE_RANGE = """
    SELECT * FROM error_logs 
    WHERE created_at BETWEEN ? AND ?
    ORDER BY created_at DESC
    """

    ERROR_LOGS_BY_SEARCH_TERM = """
    SELECT * FROM error_logs 
    WHERE search_term LIKE ?
    ORDER BY created_at DESC
    """

    ERROR_LOGS_BY_PLATFORM = """
    SELECT * FROM error_logs 
    WHERE platform = ?
    ORDER BY created_at DESC
    """

    # ==================== STATISTICS ====================

    TOTAL_ARTICLES_BY_PLATFORM = """
    SELECT platform, COUNT(*) as total 
    FROM articles 
    GROUP BY platform 
    ORDER BY total DESC
    """

    VALIDATION_RATE = """
    SELECT 
        COUNT(CASE WHEN status = 'VALIDADO' THEN 1 END) * 100.0 / COUNT(*) as validation_rate,
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'VALIDADO' THEN 1 END) as validated,
        COUNT(CASE WHEN status = 'REJEITADO' THEN 1 END) as rejected
    FROM articles
    """

    ARTICLES_BY_DATE_AND_STATUS = """
    SELECT DATE(created_at) as date, status, COUNT(*) as count 
    FROM articles 
    GROUP BY DATE(created_at), status 
    ORDER BY date DESC
    """

    DATABASE_STATS = """
    SELECT 
        (SELECT COUNT(*) FROM affiliation_variations) as affiliations,
        (SELECT COUNT(*) FROM articles) as articles,
        (SELECT COUNT(*) FROM articles WHERE status = 'VALIDADO') as validated_articles,
        (SELECT COUNT(*) FROM search_history) as searches,
        (SELECT COUNT(*) FROM error_logs) as errors
    """

    # ==================== MAINTENANCE ====================

    DELETE_OLD_SEARCH_HISTORY = """
    DELETE FROM search_history 
    WHERE search_date < datetime('now', '-90 days')
    """

    DELETE_OLD_ERROR_LOGS = """
    DELETE FROM error_logs 
    WHERE created_at < datetime('now', '-180 days')
    """


class QueryBuilder:
    """
    Helper class para construir queries dinamicamente.
    Útil para filtros complexos e dinâmicos.
    """

    @staticmethod
    def build_articles_filter(platform=None, status=None, date_start=None, date_end=None) -> tuple:
        """
        Constrói query dinâmica para filtrar artigos.
        
        Args:
            platform: Plataforma (ex: "PubMed")
            status: Status (ex: "VALIDADO")
            date_start: Data inicial
            date_end: Data final
            
        Returns:
            Tupla (query, params)
        """
        query = "SELECT * FROM articles WHERE 1=1"
        params = []

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        if status:
            query += " AND status = ?"
            params.append(status)

        if date_start:
            query += " AND created_at >= ?"
            params.append(date_start)

        if date_end:
            query += " AND created_at <= ?"
            params.append(date_end)

        query += " ORDER BY created_at DESC"
        return query, params

    @staticmethod
    def build_error_logs_filter(error_type=None, platform=None, date_start=None, date_end=None) -> tuple:
        """
        Constrói query dinâmica para filtrar erros.
        
        Args:
            error_type: Tipo de erro
            platform: Plataforma
            date_start: Data inicial
            date_end: Data final
            
        Returns:
            Tupla (query, params)
        """
        query = "SELECT * FROM error_logs WHERE 1=1"
        params = []

        if error_type:
            query += " AND error_type = ?"
            params.append(error_type)

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        if date_start:
            query += " AND created_at >= ?"
            params.append(date_start)

        if date_end:
            query += " AND created_at <= ?"
            params.append(date_end)

        query += " ORDER BY created_at DESC"
        return query, params


# Exemplo de uso:
# from database.queries import SearchQueries, QueryBuilder
# query = SearchQueries.TOTAL_ARTICLES_BY_PLATFORM
# query, params = QueryBuilder.build_articles_filter(platform="PubMed", status="VALIDADO")
