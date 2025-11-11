"""
Modelos de dados para o NEXUS Pesquisa.
Define as estruturas das tabelas principais do banco de dados.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AffiliationVariation:
    """
    Modelo para variações de afiliação (HC, UFPE, etc).
    Representa diferentes formas de escrita do mesmo hospital/instituição.
    """
    id: Optional[int] = None
    original_text: str = ""  # Texto original encontrado (ex: "HC*EBSERH")
    normalized_text: str = ""  # Texto normalizado (ex: "Hospital das Clínicas - EBSERH")
    institution: str = ""  # Instituição normalizada (ex: "HC-UFPE")
    platform: str = ""  # Plataforma de origem (Scielo, PubMed, etc)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __repr__(self):
        return f"AffiliationVariation(id={self.id}, original='{self.original_text}', normalized='{self.normalized_text}')"


@dataclass
class Article:
    """
    Modelo para artigos coletados nas plataformas.
    """
    id: Optional[int] = None
    title: str = ""
    authors: str = ""
    doi: str = ""
    platform: str = ""  # Scielo, PubMed, Lilacs, Capes
    publication_date: Optional[datetime] = None
    abstract: str = ""
    url: str = ""
    status: str = "NOVO"  # NOVO, VALIDADO, REJEITADO
    collected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class SearchHistory:
    """
    Modelo para registro de histórico de buscas realizadas.
    """
    id: Optional[int] = None
    search_term: str = ""
    platforms: str = ""  # JSON com plataformas (Scielo,PubMed,Lilacs)
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    results_count: int = 0
    search_date: Optional[datetime] = None


@dataclass
class ErrorLog:
    """
    Modelo para registro de erros e falhas durante a execução.
    """
    id: Optional[int] = None
    error_type: str = ""  # Rejeição de Conteúdo, Erro de Conexão, etc
    search_term: str = ""
    article_title: str = ""
    article_doi: str = ""
    platform: str = ""
    error_reason: str = ""  # Explicação do erro
    error_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
