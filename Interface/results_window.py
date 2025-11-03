from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QScrollArea, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, Signal
import time # Necessário para o SIMULATED_SEARCH_ERRORS

# IMPORTAÇÃO DA JANELA DE LOG: Necessário para a funcionalidade de log de erros
# Assumindo que log_windows.py está no mesmo pacote/pasta (Interface)
from .log_windows import ErrorLogWindow 

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"
VERMELHO_ERRO = "#c53929" # Adicionado para o botão de erro

# ⚠️ DADOS SIMULADOS CORRIGIDOS E SEPARADOS (para evitar conflito com main_window)
# Artigos VALIDADOS (serão exibidos na ResultsWindow)
SIMULATED_VALIDATED_ARTICLES = [
    {
        "id": 1,
        "titulo": "Clinical and laboratory profiles with suspected dengue, chikungunya and Zika virus infections",
        "autores": "Marinho, P. E. M., Gantois, I. N., de Souza, W. C. R., et al.",
        "doi": "10.1177/03000605211048865",
        "publicacao": "2022-01 (PubMed)", # Ajustado para mostrar a plataforma
        "link": "https://pubmed.ncbi.nlm.nih.gov/34719912/",
        "resumo": "O estudo objetivou analisar o perfil de utilização de antimicrobianos em um hospital universitário em Recife, Pernambuco...",
        "status": "VALIDADO" 
    },
    {
        "id": 2,
        "titulo": "Percepções e conhecimentos sobre o uso de medicamentos entre pacientes idosos",
        "autores": "Silva, A. C., Santos, R. F., Medeiros, J. P.",
        "doi": "10.1590/0104-1169.1111",
        "publicacao": "2023-05 (Scielo)",
        "link": "https://www.scielo.br/j/rsp/a/2023/v1/",
        "resumo": "Este estudo qualitativo explorou as percepções e o nível de conhecimento de pacientes idosos sobre a polifarmácia...",
        "status": "VALIDADO" 
    },
    {
        "id": 3,
        "titulo": "Impacto da telemedicina na redução de reinternações hospitalares",
        "autores": "Souza, M. G., Lima, E. B., Oliveira, T. R.",
        "doi": "10.4321/s1135-57272024000300004",
        "publicacao": "2024-11 (PubMed)",
        "link": "https://www.google.com/search?q=telemedicina+hospitais",
        "resumo": "Uma revisão sistemática sobre o papel da telemedicina no acompanhamento pós-alta, com foco em hospitais universitários na região Nordeste...",
        "status": "VALIDADO" 
    }
]

# Dados Simulados de Erros ENCONTRADOS NESTA CONSULTA (Registro de Erros)
SIMULATED_SEARCH_ERRORS = [
    {
        "id": 201,
        "titulo": "Falha de Autenticação na API",
        "autores": "Módulo de Busca LILACS",
        "doi": "N/A",
        "publicacao": time.strftime("%Y-%m-%d %H:%M:%S"),
        "link": "https://lilacs.bvsalud.org/",
        "resumo": "As credenciais de acesso para a busca LILACS falharam. Status 401. Nenhum artigo foi retornado desta plataforma.",
        "tipo_erro": "Autenticação",
        "acao_sugerida": "Verificar chaves de API e tentar novamente.",
        "status": "ERRO"
    },
    {
        "id": 202,
        "titulo": "Artigo Rejeitado por Relevância",
        "autores": "Módulo de Validação",
        "doi": "10.1002/ajh.25622",
        "publicacao": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 300)),
        "link": "https://onlinelibrary.wiley.com/doi/abs/10.1002/ajh.25622",
        "resumo": "O artigo sobre 'Hipertensão em adultos' foi rejeitado pois nenhuma variação de afiliação do HC-UFPE foi encontrada, e o tema não é prioritário para coleta.",
        "tipo_erro": "Filtro/Rejeição de Conteúdo",
        "acao_sugerida": "Revisão manual se houver suspeita de falso negativo.",
        "status": "REJEITADO"
    }
]

# --- Widget Customizado para a Linha de Artigo (Expansível) ---
# Esta classe deve ser importada de log_windows se você mantiver a estrutura do rascunho
# Por agora, estou a mantendo aqui para que o código seja self-contained, 
# mas *remova-a* se ela já existir em log_windows.py e você usá-la de lá!
class ArticleListItem(QFrame):
    """Representa um item na lista de artigos que pode ser expandido."""
    
    item_clicked = Signal(int)

    def __init__(self, article_data, parent=None):
        super().__init__(parent)
        self.article_data = article_data
        self.is_expanded = False
        self.article_id = article_data["id"]
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; margin-bottom: 5px; background-color: white;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_header_row()
        self._setup_detail_content()
        
        self.detail_widget.setVisible(False)
        
    def _setup_header_row(self):
        """Cria a linha que mostra Título, Autores e o ícone de expansão."""
        header_widget = QWidget()
        header_hbox = QHBoxLayout(header_widget)
        header_hbox.setContentsMargins(10, 8, 10, 8)
        
        # Certifique-se de que a chave 'titulo' existe
        title_label = QLabel(f'<b>{self.article_data.get("titulo", "N/A")}</b>')
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.setFont(QFont("Arial", 10))
        title_label.setWordWrap(True)
        header_hbox.addWidget(title_label, 1) 
        
        authors_label = QLabel(f'Autores: {self.article_data.get("autores", "N/A")}')
        authors_label.setFixedWidth(250)
        authors_label.setFont(QFont("Arial", 9))
        header_hbox.addWidget(authors_label)
        
        self.expand_icon = QLabel("▼")
        self.expand_icon.setFixedWidth(20)
        header_hbox.addWidget(self.expand_icon)
        
        self.main_layout.addWidget(header_widget)
        
        self.header_widget = header_widget

    def _setup_detail_content(self):
        """Cria o widget com os detalhes (Resumo, DOI, Link) que será expandido."""
        self.detail_widget = QFrame()
        self.detail_widget.setStyleSheet(f"background-color: {CINZA_FUNDO}; padding: 10px; border-top: 1px solid #ccc; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px;")
        detail_layout = QGridLayout(self.detail_widget)
        detail_layout.setSpacing(5)
        
        def add_detail_row(layout, row, label_text, value_text):
            label = QLabel(f'<b>{label_text}:</b>')
            label.setFixedWidth(100)
            value = QLabel(value_text)
            value.setOpenExternalLinks(True) 
            value.setWordWrap(True)
            layout.addWidget(label, row, 0, Qt.AlignTop)
            layout.addWidget(value, row, 1)

        add_detail_row(detail_layout, 0, "ID DOI", self.article_data.get("doi", "N/A"))
        add_detail_row(detail_layout, 1, "Publicação", self.article_data.get("publicacao", "N/A"))
        
        # Adiciona o Link como um hyperlink
        link_value = f'<a href="{self.article_data.get("link", "#")}" style="color: {AZUL_NEXUS};">{self.article_data.get("link", "N/A")}</a>'
        add_detail_row(detail_layout, 2, "Link", link_value)
        
        resumo_label = QLabel('<b>Resumo:</b>')
        detail_layout.addWidget(resumo_label, 3, 0, 1, 2, Qt.AlignTop)
        resumo_text = QLabel(self.article_data.get("resumo", "Resumo não disponível."))
        resumo_text.setWordWrap(True)
        detail_layout.addWidget(resumo_text, 4, 0, 1, 2)
        
        # O rodapé de Data da Pesquisa (simulado)
        data_pesquisa_label = QLabel('<i>Data da Pesquisa: 30-09-2025 (Simulado)</i>')
        data_pesquisa_label.setFont(QFont("Arial", 8))
        data_pesquisa_label.setStyleSheet("padding-top: 10px; border-top: 1px dashed #ccc;")
        detail_layout.addWidget(data_pesquisa_label, 5, 0, 1, 2, Qt.AlignRight)

        self.main_layout.addWidget(self.detail_widget)

    def mousePressEvent(self, event):
        """Sobrescreve o evento de clique para expandir/colapsar."""
        if self.header_widget.geometry().contains(event.pos()):
            # Emite o ID para que a ResultsWindow possa colapsar os outros
            self.item_clicked.emit(self.article_id) 
            self._toggle_expansion()
        else:
            super().mousePressEvent(event)

    def _handle_item_clicked(self, clicked_id):
        """Recebe o sinal do clique. Colapsa se outro item foi clicado."""
        if clicked_id != self.article_id and self.is_expanded:
            self.collapse()

    def _toggle_expansion(self):
        """Alterna o estado de expansão."""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Expande o widget de detalhes."""
        self.detail_widget.setVisible(True)
        self.expand_icon.setText("▲")
        self.is_expanded = True
        
    def collapse(self):
        """Colapsa o widget de detalhes."""
        self.detail_widget.setVisible(False)
        self.expand_icon.setText("▼")
        self.is_expanded = False


# --- Janela Principal de Resultados ---

class ResultsWindow(QMainWindow):
    # Usa a lista SIMULATED_VALIDATED_ARTICLES do topo
    def __init__(self, parent=None, articles=None, search_errors=None):
        super().__init__(parent)
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Tela de Resultados')
        self.setGeometry(100, 100, 1000, 750) 
        
        self.parent_window = parent 
        self.articles = articles if articles is not None else SIMULATED_VALIDATED_ARTICLES
        
        # NOVO: Inicializa os erros da consulta atual
        self.current_search_errors = search_errors if search_errors is not None else SIMULATED_SEARCH_ERRORS
        self.current_log_window = None # Referência para a janela de Log de Erros
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.article_list_items = []

        self._setup_header()
        self._setup_content()
        self._setup_footer()

    def _setup_header(self):
        header_hbox = QHBoxLayout()
        
        back_button = QPushButton('←')
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet(f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; border-radius: 15px; font-weight: bold;")
        back_button.clicked.connect(self.return_to_search)
        header_hbox.addWidget(back_button, alignment=Qt.AlignLeft)
        
        title_label = QLabel('Resultados da Pesquisa (Apenas Validados)') # Título ajustado para ser mais claro
        font = QFont("Arial", 18)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        header_hbox.addWidget(title_label, 1) 
        
        header_hbox.addItem(QSpacerItem(30, 30, QSizePolicy.Fixed, QSizePolicy.Fixed)) 

        self.main_layout.addLayout(header_hbox)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        self.main_layout.addWidget(separator)

    def _setup_content(self):
        content_hbox = QHBoxLayout()
        
        # 1. Área de Rolagem para Artigos (Esquerda)
        results_scroll_area = QScrollArea()
        results_scroll_area.setWidgetResizable(True)
        
        results_list_widget = QWidget()
        results_list_widget.setStyleSheet(f"background-color: {CINZA_FUNDO};")
        self.results_vbox = QVBoxLayout(results_list_widget)
        self.results_vbox.setSpacing(5) 
        self.results_vbox.setContentsMargins(10, 10, 10, 10)
        
        self.populate_article_list()

        self.results_vbox.addStretch(1) 
        results_scroll_area.setWidget(results_list_widget)
        
        content_hbox.addWidget(results_scroll_area, 3) 
        
        # 2. Painel de Estatísticas (Direita)
        stats_frame = QFrame()
        stats_frame.setFixedWidth(250)
        stats_frame.setStyleSheet(f"background-color: {BRANCO_PADRAO}; border: 1px solid gray; padding: 10px; border-radius: 5px;")
        self._setup_stats_panel(stats_frame)
        content_hbox.addWidget(stats_frame, 1) 

        self.main_layout.addLayout(content_hbox, 1) 

    def populate_article_list(self):
        """Popula a lista de artigos e conecta os sinais de expansão/colapso."""
        
        # Limpar lista anterior (garante que não haja widgets duplicados)
        while self.results_vbox.count() > 0:
            item = self.results_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.article_list_items = []
        
        if not self.articles:
            no_results_label = QLabel("Nenhum artigo validado encontrado.")
            no_results_label.setAlignment(Qt.AlignCenter)
            no_results_label.setFont(QFont("Arial", 12))
            no_results_label.setStyleSheet("color: gray; padding: 20px;")
            self.results_vbox.addWidget(no_results_label)
            return

        for article in self.articles:
            item = ArticleListItem(article)
            
            # Conecta o sinal de clique a todos os outros itens para colapsá-los
            for existing_item in self.article_list_items:
                item.item_clicked.connect(existing_item._handle_item_clicked)
                existing_item.item_clicked.connect(item._handle_item_clicked)
            
            self.article_list_items.append(item)
            self.results_vbox.addWidget(item)
        
        pagination_label = QLabel("<div align='center'><a href='#' style='color: #3b5998; font-weight: bold;'>1</a> <span style='color: gray;'>2 3 ...</span></div>")
        self.results_vbox.addWidget(pagination_label, alignment=Qt.AlignCenter)


    def _setup_stats_panel(self, frame):
        """Configura o painel de estatísticas."""
        stats_layout = QGridLayout(frame)
        
        title_label = QLabel('Número de Artigos por Plataforma')
        font = QFont("Arial", 10)
        font.setBold(True)
        title_label.setFont(font)
        stats_layout.addWidget(title_label, 0, 0, 1, 2) 

        # Os dados de estatísticas agora refletem os SIMULATED_VALIDATED_ARTICLES
        stats_data = {
            "Total:": len(self.articles),
            "PubMed:": 2,
            "Scielo:": 1,
            "Lilacs:": 0,
            "Capes Periódicos:": 0
        }

        row = 1
        for label, count in stats_data.items():
            stats_layout.addWidget(QLabel(label), row, 0)
            input_field = QLineEdit(str(count))
            input_field.setReadOnly(True)
            input_field.setStyleSheet(f"background-color: {CINZA_FUNDO}; border: 1px solid gray; padding: 5px;")
            stats_layout.addWidget(input_field, row, 1)
            row += 1

        stats_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), row, 0) 
        
    def _setup_footer(self):
        """Configura o rodapé com os botões de ação e o botão de Registro de Erros."""
        footer_hbox = QHBoxLayout()
        
        style_primary = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 10px 20px; font-weight: bold; border-radius: 5px;"
        style_danger = f"background-color: {VERMELHO_ERRO}; color: {BRANCO_PADRAO}; padding: 10px 20px; font-weight: bold; border-radius: 5px;"

        btn_new_search = QPushButton('NOVA PESQUISA')
        btn_new_search.setStyleSheet(style_primary)
        btn_new_search.clicked.connect(self.return_to_search) 
        footer_hbox.addWidget(btn_new_search, 0, Qt.AlignLeft) 

        btn_add = QPushButton('ADICIONAR À BASE DE DADOS')
        btn_add.setStyleSheet(style_primary)
        footer_hbox.addWidget(btn_add)
        
        # LIGAÇÃO CORRIGIDA: Botão de Registro de Erros com a contagem da consulta atual
        btn_log = QPushButton(f'Registro de Erros ({len(self.current_search_errors)})')
        btn_log.setStyleSheet(style_danger)
        btn_log.clicked.connect(self.open_current_error_log)
        footer_hbox.addWidget(btn_log, 0, Qt.AlignRight)

        self.main_layout.addLayout(footer_hbox)
        
        copyright_label = QLabel('© EBSERH')
        copyright_label.setFont(QFont("Arial", 8))
        copyright_label.setAlignment(Qt.AlignRight)
        self.main_layout.addWidget(copyright_label)

    # --- Método de Navegação de Volta ---
    def return_to_search(self):
        """Fecha esta janela e exibe a janela pai (SearchWindow)."""
        self.close()
        if self.parent_window:
            self.parent_window.show()

    # --- LIGAÇÃO CORRIGIDA: Método para abrir o Registro de Erros da CONSULTA ATUAL ---
    def open_current_error_log(self):
        """
        Abre a janela de Registro de Erros focada apenas nos erros encontrados
        durante a busca atual (self.current_search_errors).
        """
        # Garante que apenas uma instância da janela de log de resultados esteja aberta
        if self.current_log_window is None:
            # Passa APENAS os erros da consulta atual
            self.current_log_window = ErrorLogWindow(parent=self, errors=self.current_search_errors)
            # Define o título correto para o Registro da Consulta Atual
            self.current_log_window.setWindowTitle("Nexus - Registro de Erros da Consulta Atual")
            self.current_log_window.title_label.setText("Registro de Erros da Consulta Atual")
            self.current_log_window.destroyed.connect(self._reset_current_log_window)
        
        self.current_log_window.show()
        self.hide() # Esconde a janela de resultados para focar no log

    def _reset_current_log_window(self):
        """Reseta a referência da janela de log de resultados quando ela é fechada."""
        self.current_log_window = None