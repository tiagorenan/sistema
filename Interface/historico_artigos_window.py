from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QScrollArea, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont, QCursor, QPixmap
from PySide6.QtCore import Qt, Signal, QRect, QDate

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"

# ====================================================================
# WIDGET COPIADO/ADAPTADO: ArticleListItem para uso neste módulo
# ====================================================================

class ArticleListItem(QFrame):
    """
    Cópia/Adaptação do ArticleListItem da ResultsWindow,
    necessário para exibir os artigos do Histórico de forma expansível.
    """
    item_clicked = Signal(int)

    # CORREÇÃO: Removido search_date_str, pois não é necessário aqui
    def __init__(self, article_data, parent=None): 
        super().__init__(parent)
        self.article_data = article_data
        self.is_expanded = False
        self.article_id = article_data.get("id", 0)
        
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
        """Cria a linha que mostra Título, Autores e o ícone de expansão (Layout Estável)."""
        header_widget = QWidget()
        header_hbox = QHBoxLayout(header_widget)
        header_hbox.setContentsMargins(10, 8, 10, 8)
        
        # 1. Título do Artigo
        title_label = QLabel(f'<b>{self.article_data.get("titulo", "N/A")}</b>')
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.setFont(QFont("Arial", 10))
        title_label.setWordWrap(True)
        header_hbox.addWidget(title_label, 1) 
        
        # 2. Autores (Largura Fixa)
        authors_label = QLabel(f'Autores: {self.article_data.get("autores", "N/A")}')
        authors_label.setFixedWidth(200) 
        authors_label.setFont(QFont("Arial", 9))
        authors_label.setWordWrap(True)
        header_hbox.addWidget(authors_label)
        
        # 3. Ícone de Expansão
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
        
        # CORREÇÃO DA PUBLICAÇÃO: Assume que a chave 'publicacao' está formatada corretamente no DBManager.
        add_detail_row(detail_layout, 1, "Publicação", self.article_data.get("publicacao", "N/A"))
        
        add_detail_row(detail_layout, 2, "Link", f'<a href="{self.article_data.get("link", "#")}">{self.article_data.get("link", "N/A")}</a>')
        
        resumo_label = QLabel('<b>Resumo:</b>')
        detail_layout.addWidget(resumo_label, 3, 0, 1, 2, Qt.AlignTop)
        resumo_text = QLabel(self.article_data.get("resumo", "Resumo não disponível."))
        resumo_text.setWordWrap(True)
        detail_layout.addWidget(resumo_text, 4, 0, 1, 2)
        
        # --- CAMPO REMOVIDO: Data da Pesquisa (Não é necessário aqui) ---
        # data_pesquisa_label = QLabel(f'<i>Data da Pesquisa: {self.search_date_str}</i>')
        # data_pesquisa_label.setFont(QFont("Arial", 8))
        # data_pesquisa_label.setAlignment(Qt.AlignRight)
        # detail_layout.addWidget(data_pesquisa_label, 5, 0, 1, 2, Qt.AlignRight)

        self.main_layout.addWidget(self.detail_widget)

    def mousePressEvent(self, event):
        if self.header_widget.geometry().contains(event.pos()):
            self.item_clicked.emit(self.article_id) 
            self._toggle_expansion()
        else:
            super().mousePressEvent(event)

    def _handle_item_clicked(self, clicked_id):
        if clicked_id != self.article_id and self.is_expanded:
            self.collapse()

    def _toggle_expansion(self):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        self.detail_widget.setVisible(True)
        self.expand_icon.setText("▲")
        self.is_expanded = True
        
    def collapse(self):
        self.detail_widget.setVisible(False)
        self.expand_icon.setText("▼")
        self.is_expanded = False
        
# ====================================================================
# FIM DA CLASSE ARTICLELISTITEM ADAPTADA
# ====================================================================

class HistoricoArtigosWindow(QMainWindow):
    """
    Janela dedicada a visualizar os artigos de UMA consulta específica
    do histórico, mantendo o layout de lista expansível.
    """
    # CORREÇÃO: Removido search_date_str do __init__ da janela principal
    def __init__(self, parent=None, articles=None, query_term="Consulta Histórica"): 
        super().__init__(parent)
        
        self.query_term = query_term
        self.query_term_short = query_term[:80] + '...' if len(query_term) > 80 else query_term
        
        self.setWindowTitle(f'Nexus - Artigos da Consulta: {self.query_term_short}')
        self.setGeometry(150, 150, 1000, 750) 
        
        self.parent_window = parent 
        self.articles = articles if articles is not None else []
        # Removido self.search_date_str
        
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
        back_button.clicked.connect(self.return_to_parent) 
        header_hbox.addWidget(back_button, alignment=Qt.AlignLeft)
        
        # Título Dinâmico (usando a versão curta)
        title_label = QLabel(f'Artigos Validados da Consulta: {self.query_term_short}')
        font = QFont("Arial", 18)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        header_hbox.addWidget(title_label, 1) 
        
        # --- Logo HC-UFPE no Header ---
        hc_logo_label = QLabel()
        try:
            # Acessando o resource_path pela SearchWindow (pai do HistoryWindow)
            search_window_parent = self.parent_window.parent_search_window 
            hc_logo_pixmap = QPixmap(search_window_parent.resource_path("Interface/imagens/hc_logo.png")) 
            if not hc_logo_pixmap.isNull():
                scaled_hc_pixmap = hc_logo_pixmap.scaled(60, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                hc_logo_label.setPixmap(scaled_hc_pixmap)
                header_hbox.addWidget(hc_logo_label, alignment=Qt.AlignRight) 
        except Exception:
            pass 

        header_hbox.addItem(QSpacerItem(10, 30, QSizePolicy.Fixed, QSizePolicy.Fixed)) 

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

        results_scroll_area.setWidget(results_list_widget)
        
        content_hbox.addWidget(results_scroll_area, 3) 
        
        # 2. Painel de Estatísticas (Direita) - Layout ResultsWindow
        stats_frame = QFrame()
        stats_frame.setFixedWidth(250)
        stats_frame.setStyleSheet(f"background-color: {BRANCO_PADRAO}; border: 1px solid gray; padding: 10px; border-radius: 5px;")
        self._setup_stats_panel(stats_frame)
        content_hbox.addWidget(stats_frame, 1) 

        self.main_layout.addLayout(content_hbox, 1) 

    def populate_article_list(self):
        """Popula a lista de artigos usando ArticleListItem e gerenciando expansão."""
        
        # Limpar layout anterior
        while self.results_vbox.count() > 0:
            item = self.results_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.article_list_items = []
        
        if not self.articles:
            no_results_label = QLabel("Nenhum artigo validado encontrado nesta consulta.")
            no_results_label.setAlignment(Qt.AlignCenter)
            self.results_vbox.addWidget(no_results_label)
            self.results_vbox.addStretch(1)
            return

        for article in self.articles:
            # CORREÇÃO: Agora o __init__ do ArticleListItem não precisa de search_date_str
            item = ArticleListItem(article)
            
            # Gerenciamento de expansão (Colapsa outros itens)
            for existing_item in self.article_list_items:
                item.item_clicked.connect(existing_item._handle_item_clicked)
                existing_item.item_clicked.connect(item._handle_item_clicked)
            
            self.article_list_items.append(item)
            self.results_vbox.addWidget(item)
        
        self.results_vbox.addStretch(1)


    def _setup_stats_panel(self, frame):
        """
        Configura o painel de estatísticas, baseado nos artigos carregados.
        """
        stats_layout = QGridLayout(frame)
        
        title_label = QLabel('Número de Artigos por Plataf')
        font = QFont("Arial", 10)
        font.setBold(True)
        title_label.setFont(font)
        stats_layout.addWidget(title_label, 0, 0, 1, 2) 

        # --- Cálculo dinâmico ---
        platform_counts = {
            "Total:": len(self.articles),
            "PubMed:": 0,
            "Scielo:": 0,
            "Lilacs:": 0,
            "Capes Periódicos:": 0
        }
        
        for article in self.articles:
            publicacao = article.get("publicacao", "")
            platform_name = "Desconhecido"
            if "(" in publicacao and ")" in publicacao:
                platform_name = publicacao.split("(")[-1].rstrip(")")
            
            if platform_name in platform_counts:
                platform_counts[platform_name] += 1
            elif 'Capes' in platform_name:
                 platform_counts['Capes Periódicos'] += 1
        # ------------------------
        
        row = 1
        platform_labels = ["Total:", "PubMed:", "Scielo:", "Lilacs:", "Capes Periódicos:"]
        
        for label_text in platform_labels:
            count = platform_counts.get(label_text, platform_counts.get(label_text.rstrip(':'), 0))
            stats_layout.addWidget(QLabel(label_text), row, 0)
            input_field = QLineEdit(str(count))
            input_field.setReadOnly(True)
            input_field.setStyleSheet(f"background-color: {CINZA_FUNDO}; border: 1px solid gray; padding: 5px;")
            stats_layout.addWidget(input_field, row, 1)
            row += 1

        stats_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), row, 0) 

    def _setup_footer(self):
        footer_hbox = QHBoxLayout()
        
        btn_back_history = QPushButton('VOLTAR AO HISTÓRICO')
        style = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 10px 20px; font-weight: bold; border-radius: 5px;"
        btn_back_history.setStyleSheet(style)
        btn_back_history.clicked.connect(self.return_to_parent) 
        footer_hbox.addWidget(btn_back_history, alignment=Qt.AlignCenter)
        
        self.main_layout.addLayout(footer_hbox)
        
        # --- Rodapé Final ---
        final_footer_hbox = QHBoxLayout()
        copyright_label = QLabel('© EBSERH')
        copyright_label.setFont(QFont("Arial", 8))
        final_footer_hbox.addWidget(copyright_label, alignment=Qt.AlignLeft)
        final_footer_hbox.addStretch(1)
        
        self.main_layout.addLayout(final_footer_hbox)

    def return_to_parent(self):
        """Fecha esta janela e exibe a janela HistoryWindow (Parent)."""
        self.close()
        if self.parent_window:
            self.parent_window.show()