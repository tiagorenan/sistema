from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QScrollArea, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, Signal

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"

# Dados simulados de artigos (Usados tanto aqui quanto em main_window)
SIMULATED_ARTICLES = [
    {
        "id": 1,
        "titulo": "Clinical and laboratory profiles with suspected dengue, chikungunya and Zika virus infections",
        "autores": "Marinho, P. E. M., Gantois, I. N., de Souza, W. C. R., et al.",
        "doi": "10.1177/03000605211048865",
        "publicacao": "2022-01",
        "link": "https://pubmed.ncbi.nlm.nih.gov/34719912/",
        "resumo": "O estudo objetivou analisar o perfil de utilização de antimicrobianos em um hospital universitário em Recife, Pernambuco. Foi realizado um estudo transversal, retrospectivo, com base em dados de prescrições de pacientes internados em 2015. Os dados foram coletados dos prontuários eletrônicos e analisados segundo a classificação ATC/DDD da OMS. O consumo total de antimicrobianos foi de 85,4 DDD/100 leitos-dia. Os beta-lactâmicos, incluindo penicilinas e cefalosporinas, foram a classe mais consumida. O ceftriaxona foi o antimicrobiano mais utilizado. A análise revelou um alto consumo de antimicrobianos de amplo espectro, indicando a necessidade de implementação de programas de gerenciamento para otimizar o uso desses medicamentos e conter a resistência bacteriana."
    },
    {
        "id": 2,
        "titulo": "Percepções e conhecimentos sobre o uso de medicamentos entre pacientes idosos",
        "autores": "Silva, A. C., Santos, R. F., Medeiros, J. P.",
        "doi": "10.1590/0104-1169.1111",
        "publicacao": "2023-05",
        "link": "https://www.scielo.br/j/rsp/a/2023/v1/",
        "resumo": "Este estudo qualitativo explorou as percepções e o nível de conhecimento de pacientes idosos sobre a polifarmácia e a adesão ao tratamento em um hospital-escola no Nordeste do Brasil. Os resultados apontam para a necessidade de intervenções educativas mais focadas."
    },
    {
        "id": 3,
        "titulo": "Impacto da telemedicina na redução de reinternações hospitalares",
        "autores": "Souza, M. G., Lima, E. B., Oliveira, T. R.",
        "doi": "10.4321/s1135-57272024000300004",
        "publicacao": "2024-11",
        "link": "https://www.google.com/search?q=telemedicina+hospitais",
        "resumo": "Uma revisão sistemática sobre o papel da telemedicina no acompanhamento pós-alta, com foco em hospitais universitários na região Nordeste. Dados preliminares sugerem uma redução de 15% nas taxas de reinternação em pacientes crônicos."
    }
]

# --- Widget Customizado para a Linha de Artigo (Expansível) ---

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
        
        title_label = QLabel(f'<b>{self.article_data["titulo"]}</b>')
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.setFont(QFont("Arial", 10))
        title_label.setWordWrap(True)
        header_hbox.addWidget(title_label, 1) 
        
        authors_label = QLabel(f'Autores: {self.article_data["autores"]}')
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

        add_detail_row(detail_layout, 0, "ID DOI", self.article_data["doi"])
        add_detail_row(detail_layout, 1, "Publicação", self.article_data["publicacao"])
        add_detail_row(detail_layout, 2, "Link", f'<a href="{self.article_data["link"]}">{self.article_data["link"]}</a>')
        
        resumo_label = QLabel('<b>Resumo:</b>')
        detail_layout.addWidget(resumo_label, 3, 0, 1, 2, Qt.AlignTop)
        resumo_text = QLabel(self.article_data["resumo"])
        resumo_text.setWordWrap(True)
        detail_layout.addWidget(resumo_text, 4, 0, 1, 2)
        
        data_pesquisa_label = QLabel('<i>Data da Pesquisa: 30-09-2025 (Simulado)</i>')
        data_pesquisa_label.setFont(QFont("Arial", 8))
        data_pesquisa_label.setStyleSheet("padding-top: 10px; border-top: 1px dashed #ccc;")
        detail_layout.addWidget(data_pesquisa_label, 5, 0, 1, 2, Qt.AlignRight)

        self.main_layout.addWidget(self.detail_widget)


    def mousePressEvent(self, event):
        """Sobrescreve o evento de clique para expandir/colapsar."""
        if self.header_widget.geometry().contains(event.pos()):
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
    def __init__(self, parent=None, articles=None):
        super().__init__(parent)
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Tela de Resultados')
        self.setGeometry(100, 100, 1000, 750) 
        
        self.parent_window = parent 
        self.articles = articles if articles is not None else SIMULATED_ARTICLES
        
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
        
        title_label = QLabel('Tela de Resultados')
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
        
        for item in self.article_list_items:
            item.deleteLater()
        self.article_list_items = []

        for article in self.articles:
            item = ArticleListItem(article)
            
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
        footer_hbox = QHBoxLayout()
        
        style = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 10px 20px; font-weight: bold; border-radius: 5px;"

        btn_add = QPushButton('ADICIONAR À BASE DE DADOS')
        btn_add.setStyleSheet(style)
        footer_hbox.addWidget(btn_add)
        
        btn_new_search = QPushButton('NOVA PESQUISA')
        btn_new_search.setStyleSheet(style)
        btn_new_search.clicked.connect(self.return_to_search) 
        footer_hbox.addWidget(btn_new_search)
        
        btn_error = QPushButton('Registro de Erros')
        btn_error.setStyleSheet(style)
        footer_hbox.addWidget(btn_error)

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