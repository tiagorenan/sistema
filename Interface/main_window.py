import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QSpacerItem, QSizePolicy, QButtonGroup, QDateEdit
)
from PySide6.QtGui import QFont, QIcon, QPixmap 
from PySide6.QtCore import Qt, QEvent, QRect, QDate

# Importações de outras janelas e dados simulados
from Interface.results_window import ResultsWindow, SIMULATED_VALIDATED_ARTICLES 
from Interface.config_window import ConfigWindow, DEFAULT_CONFIG 
from Interface.log_windows import ErrorLogWindow 
from Interface.historico_window import HistoryWindow 

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"

class SearchWindow(QMainWindow):
    """
    Janela principal da aplicação (Tela de Busca).
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Tela de Busca')
        self.setGeometry(100, 100, 800, 600)
        
        # --- Definir o Ícone da Janela (Logo Nexus) ---
        try:
            icon_path = "Interface/imagens/logo_azul.png" 
            self.setWindowIcon(QIcon(icon_path))
            print(f"Ícone da janela (Nexus) carregado de: {icon_path}")
        except Exception as e:
            print(f"Erro ao carregar o ícone da janela (Nexus): {e}")
        
        self.config_window = None 
        self.results_window = None 
        self.log_window = None 
        self.history_window = None 
        self.is_menu_open = False
        
        self.default_search_config = DEFAULT_CONFIG.copy()
        self.current_search_scope = 'Tema'      
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Chamadas de setup
        self._setup_header()
        self._setup_content()
        self._setup_footer() # A logo do HC-UFPE será configurada aqui
        
        self._setup_sidebar() 
        
        self.installEventFilter(self)
        self.apply_default_config(self.default_search_config, initial=True)
        self._update_stats_display()

    # --- MÉTODOS DE CONTROLE DE MENU (Movidos para o topo para evitar Attribute Error) ---
    def toggle_menu(self):
        """Método para abrir/fechar o menu lateral."""
        self.is_menu_open = not self.is_menu_open
        if self.is_menu_open:
            self.menu_sidebar.setGeometry(0, 0, self.menu_sidebar.width(), self.height())
            self.menu_sidebar.show()
            self.menu_button.setText('✕') 
        else:
            self.menu_sidebar.hide()
            self.menu_button.setText('☰') 
            
    def open_history_window_and_close_menu(self):
        self.open_history_window()
        self.toggle_menu()

    def open_log_window_and_close_menu(self):
        self.open_log_window()
        self.toggle_menu() 

    def open_config_window_and_close_menu(self):
        self.open_config_window()
        self.toggle_menu()
    # ------------------------------------------------------------------------------------

    # --- Filtro de Eventos e Redimensionamento ---
    def eventFilter(self, source, event):
        if self.is_menu_open and event.type() == QEvent.MouseButtonPress:
            menu_rect = self.menu_sidebar.geometry()
            global_menu_rect = QRect(self.mapToGlobal(menu_rect.topLeft()), menu_rect.size())
            if not global_menu_rect.contains(event.globalPos()):
                self.toggle_menu()
        return super().eventFilter(source, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.menu_sidebar:
            self.menu_sidebar.setGeometry(0, 0, self.menu_sidebar.width(), self.height())
    
    # --- Configuração do Menu Lateral ---
    def _setup_sidebar(self):
        self.menu_sidebar = QWidget(self.central_widget)
        self.menu_sidebar.setStyleSheet("background-color: #2c3e50; color: white; border-right: 2px solid #34495e;")
        self.menu_sidebar.setFixedWidth(250)
        
        menu_layout = QVBoxLayout(self.menu_sidebar)
        menu_layout.setContentsMargins(0, 60, 0, 0)
        menu_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        button_style = "QPushButton { text-align: left; padding: 15px 20px; border: none; color: white; background-color: transparent; font-size: 11pt; }" \
                            "QPushButton:hover { background-color: #34495e; }"
        
        btn_historico = QPushButton('Histórico de Pesquisa')
        btn_historico.setStyleSheet(button_style)
        btn_historico.clicked.connect(self.open_history_window_and_close_menu) 
        menu_layout.addWidget(btn_historico)
        
        btn_erros = QPushButton('Histórico de Erros')
        btn_erros.setStyleSheet(button_style)
        btn_erros.clicked.connect(self.open_log_window_and_close_menu) 
        menu_layout.addWidget(btn_erros)

        btn_config = QPushButton('Editar Padrão de Busca')
        btn_config.setStyleSheet(button_style)
        btn_config.clicked.connect(self.open_config_window_and_close_menu) 
        menu_layout.addWidget(btn_config)
        
        menu_layout.addStretch(1)

        self.menu_sidebar.setGeometry(0, 0, 250, self.height())
        self.menu_sidebar.hide()
        self.menu_sidebar.raise_()

    def _setup_header(self):
        header_hbox = QHBoxLayout()
        self.menu_button = QPushButton('☰')
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.setStyleSheet("background-color: white; border: none; font-size: 16px; font-weight: bold;")
        self.menu_button.clicked.connect(self.toggle_menu) 
        header_hbox.addWidget(self.menu_button, alignment=Qt.AlignLeft)
        
        # Opcional: Adicionar a logo do Nexus (menor) ao lado do título da aplicação no cabeçalho
        nexus_logo_header_label = QLabel()
        nexus_logo_pixmap_small = QPixmap("Interface/imagens/logo_azul.png")
        if not nexus_logo_pixmap_small.isNull():
            scaled_nexus_pixmap_small = nexus_logo_pixmap_small.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            nexus_logo_header_label.setPixmap(scaled_nexus_pixmap_small)
            header_hbox.addWidget(nexus_logo_header_label, alignment=Qt.AlignLeft) 
        else:
             print("Não foi possível carregar a logo do Nexus para o cabeçalho.")
        
        header_label = QLabel('Nexus Pesquisa HC-UFPE')
        font = QFont("Arial", 14)
        font.setBold(True)
        header_label.setFont(font)
        header_label.setAlignment(Qt.AlignCenter) 
        header_hbox.addWidget(header_label, 1) 
        
        spacer = QWidget()
        spacer.setFixedSize(30, 30) 
        header_hbox.addWidget(spacer, alignment=Qt.AlignRight)
        
        header_hbox.setSpacing(10) 

        self.main_layout.addLayout(header_hbox)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        self.main_layout.addWidget(separator)

    # --- Configuração de Conteúdo e Filtros ---
    def _setup_content(self):
        content_hbox = QHBoxLayout()
        self.filtro_frame = QFrame()
        self.filtro_layout = QVBoxLayout(self.filtro_frame)
        self._setup_filters()
        content_hbox.addWidget(self.filtro_frame, 2) 
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet(f"background-color: {BRANCO_PADRAO}; border: 1px solid gray; padding: 10px; border-radius: 5px;")
        self.stats_layout = QGridLayout(self.stats_frame)
        self._setup_stats()
        content_hbox.addWidget(self.stats_frame, 1) 
        self.main_layout.addLayout(content_hbox)

    def _setup_filters(self):
        title_label = QLabel('Selecione os Filtros')
        font = QFont("Arial", 12)
        font.setBold(True)
        title_label.setFont(font)
        self.filtro_layout.addWidget(title_label)
        self.filtro_layout.addWidget(QLabel('Banco de dados'))
        self.db_hbox = QHBoxLayout()
        self.platform_buttons = {}
        platforms = ['Scielo', 'PubMed', 'Lilacs', 'Capes Periódicos']
        for platform in platforms:
            btn = QPushButton(platform)
            btn.setProperty('platform', platform)
            btn.clicked.connect(self._toggle_platform_selection)
            self.platform_buttons[platform] = btn
            self.db_hbox.addWidget(btn)
        self.db_hbox.addStretch(1) 
        self.filtro_layout.addLayout(self.db_hbox)
        
        # 2. Período de Busca
        self.filtro_layout.addWidget(QLabel('Período de busca')) 
        
        self.date_hbox = QHBoxLayout()
        self.date_hbox.addWidget(QLabel('A partir de'))
        self.date_start_input = QDateEdit(self)
        self.date_start_input.setDisplayFormat("dd/MM/yyyy")
        self.date_start_input.setCalendarPopup(True) 
        self.date_start_input.setFixedWidth(120) 
        self.date_start_input.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        self.date_hbox.addWidget(self.date_start_input)
        self.date_hbox.addWidget(QLabel('Até'))
        self.date_end_input = QDateEdit(self)
        self.date_end_input.setDisplayFormat("dd/MM/yyyy")
        self.date_end_input.setCalendarPopup(True) 
        self.date_end_input.setFixedWidth(120) 
        self.date_end_input.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        self.date_hbox.addWidget(self.date_end_input)
        self.date_hbox.addStretch(1)
        self.filtro_layout.addLayout(self.date_hbox)
        
        # 3. Busca Personalizada
        self.filtro_layout.addWidget(QLabel('Busca Personalizada'))
        search_field_hbox = QHBoxLayout()
        self.search_term_input = QLineEdit()
        self.search_term_input.setPlaceholderText("Buscar artigos")
        self.search_term_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        search_field_hbox.addWidget(self.search_term_input)
        search_button = QPushButton('PESQUISAR')
        search_button.setStyleSheet(f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        search_button.clicked.connect(self.iniciar_busca)
        search_field_hbox.addWidget(search_button)
        self.filtro_layout.addLayout(search_field_hbox)
        
        # Botões de Escopo
        scope_hbox = QHBoxLayout()
        self.scope_group = QButtonGroup(self) 
        scopes = ['Autor', 'Título', 'Tema']
        self.scope_buttons = {}
        for scope in scopes:
            btn = QPushButton(scope)
            btn.setProperty('scope', scope)
            self.scope_buttons[scope] = btn
            btn.clicked.connect(self._select_search_scope)
            self.scope_group.addButton(btn)
            scope_hbox.addWidget(btn)
        scope_hbox.addStretch(1)
        self.filtro_layout.addLayout(scope_hbox)
        self.filtro_layout.addStretch(1)
        
    def _setup_stats(self):
        title_label = QLabel('Número de Artigos por Plataforma')
        font = QFont("Arial", 10)
        font.setBold(True)
        title_label.setFont(font)
        self.stats_layout.addWidget(title_label, 0, 0, 1, 2) 
        self.stats_layout.addWidget(QLabel('Total:'), 1, 0)
        self.total_input = QLineEdit("0")
        self.total_input.setReadOnly(True)
        self.total_input.setStyleSheet(f"background-color: {CINZA_FUNDO}; border: 1px solid gray; padding: 5px;")
        self.stats_layout.addWidget(self.total_input, 1, 1)
        platforms = ['PubMed', 'Scielo', 'Lilacs', 'Capes Periódicos']
        self.platform_stat_inputs = {}
        for i, platform in enumerate(platforms, 2): 
            self.stats_layout.addWidget(QLabel(f'{platform}:'), i, 0)
            input_field = QLineEdit("0")
            input_field.setReadOnly(True)
            input_field.setStyleSheet(f"background-color: {CINZA_FUNDO}; border: 1px solid gray; padding: 5px;")
            self.stats_layout.addWidget(input_field, i, 1)
            self.platform_stat_inputs[platform] = input_field
        self.stats_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), len(platforms) + 2, 0) 

    def _update_stats_display(self):
        total = 500
        stats = {
            'PubMed': 250,
            'Scielo': 150,
            'Lilacs': 75,
            'Capes Periódicos': 25
        }
        self.total_input.setText(str(total))
        for platform, count in stats.items():
            if platform in self.platform_stat_inputs:
                self.platform_stat_inputs[platform].setText(str(count))

    def _setup_footer(self):
        footer_hbox = QHBoxLayout() 

        # Adicionar o "© EBSERH" à esquerda no rodapé
        ebserh_label = QLabel('© EBSERH')
        ebserh_label.setFont(QFont("Arial", 8))
        footer_hbox.addWidget(ebserh_label, alignment=Qt.AlignLeft) 

        # Espaçador para empurrar a logo do HC-UFPE para a direita
        footer_hbox.addStretch(1) 

        # --- NOVO: Logo do Hospital (HC-UFPE) no rodapé, AGORA MAIOR e à DIREITA ---
        hc_logo_label = QLabel()
        hc_logo_pixmap = QPixmap("Interface/imagens/hc_logo.png") # Caminho atualizado para .png
        if not hc_logo_pixmap.isNull():
            # Redimensionar para um tamanho maior, ajuste conforme necessário
            scaled_hc_pixmap = hc_logo_pixmap.scaled(150, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Exemplo: 150 largura, 45 altura
            hc_logo_label.setPixmap(scaled_hc_pixmap)
            # Adicionar à direita no rodapé
            footer_hbox.addWidget(hc_logo_label, alignment=Qt.AlignRight) 
            print(f"Logo do HC-UFPE (PNG, maior) carregada de: Interface/imagens/hc_logo.png")
        else:
            print("Não foi possível carregar a logo do HC-UFPE (PNG) para o rodapé.")
        
        self.main_layout.addLayout(footer_hbox) 

    # --- MÉTODOS DE INTERAÇÃO E CONFIGURAÇÃO (Mantidos) ---
    def _get_platform_style(self, is_selected):
        base = "border: 1px solid {AZUL_NEXUS}; padding: 5px 10px; border-radius: 15px;".format(AZUL_NEXUS=AZUL_NEXUS)
        if is_selected:
            return f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; {base}"
        else:
            return f"background-color: {BRANCO_PADRAO}; color: {AZUL_NEXUS}; {base}"

    def _get_scope_style(self, is_selected):
        base = "border: none; padding: 5px 10px; border-radius: 15px;"
        if is_selected:
            return f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; {base}"
        else:
            return f"background-color: {BRANCO_PADRAO}; color: {AZUL_NEXUS}; {base}"

    def _toggle_platform_selection(self):
        button = self.sender()
        platform = button.property('platform')
        if platform in self.default_search_config['platforms']:
            self.default_search_config['platforms'].remove(platform)
        else:
            self.default_search_config['platforms'].append(platform)
        button.setStyleSheet(self._get_platform_style(platform in self.default_search_config['platforms']))

    def _select_search_scope(self):
        button = self.sender()
        new_scope = button.property('scope')
        if self.current_search_scope and self.current_search_scope in self.scope_buttons:
            old_button = self.scope_buttons[self.current_search_scope]
            old_button.setStyleSheet(self._get_scope_style(False))
        button.setStyleSheet(self._get_scope_style(True))
        self.current_search_scope = new_scope
        
    def apply_default_config(self, config_data, initial=False):
        self.default_search_config = config_data.copy()
        
        # 1. Atualiza as Datas (USANDO QDate)
        date_start = QDate.fromString(self.default_search_config['date_start'], "dd/MM/yyyy")
        if date_start.isValid():
            self.date_start_input.setDate(date_start)
        else:
            self.date_start_input.setDate(QDate.currentDate())
            
        date_end = QDate.fromString(self.default_search_config['date_end'], "dd/MM/yyyy")
        if date_end.isValid():
            self.date_end_input.setDate(date_end)
        else:
            self.date_end_input.setDate(QDate.currentDate())

        # 2. Atualiza os Botões de Plataforma
        for platform, btn in self.platform_buttons.items():
            is_selected = platform in self.default_search_config['platforms']
            btn.setStyleSheet(self._get_platform_style(is_selected))
            
        # 3. Atualiza o Escopo
        if initial and self.current_search_scope in self.scope_buttons:
            self.scope_buttons[self.current_search_scope].setStyleSheet(self._get_scope_style(True))

    # --- Métodos de Ação e Navegação ---
    
    def iniciar_busca(self):
        search_term_manual = self.search_term_input.text().strip()
        self.default_search_config['date_start'] = self.date_start_input.date().toString("dd/MM/yyyy")
        self.default_search_config['date_end'] = self.date_end_input.date().toString("dd/MM/yyyy")
        
        if search_term_manual:
            term_used = search_term_manual
            platforms_used = self.default_search_config['platforms']
        else:
            term_used = "Padrão: " + ", ".join(self.default_search_config['search_terms'][:3]) + "..."
            platforms_used = self.default_search_config['platforms']
            
        print(f"Iniciando busca: Termo='{term_used}' | Plataformas: {platforms_used}")
        print(f"Período: {self.default_search_config['date_start']} a {self.default_search_config['date_end']}")
        
        articles = SIMULATED_VALIDATED_ARTICLES 
        self.open_results_window(articles)

    def open_results_window(self, articles):
        """Abre a janela de Resultados e esconde a janela atual."""
        if not self.results_window:
            self.results_window = ResultsWindow(parent=self, articles=articles)
        else:
            self.results_window.articles = articles
            self.results_window.populate_article_list()
            
        self.hide() 
        self.results_window.show()

    def open_history_window(self):
        """Abre a janela de Histórico Geral."""
        if not self.history_window:
            self.history_window = HistoryWindow(parent=self) 
        self.history_window.show()
        self.hide()
        
    def open_config_window(self):
        """Abre a janela de Configuração."""
        if not self.config_window:
            self.config_window = ConfigWindow(parent=self)
            self.config_window.current_config = self.default_search_config.copy()
        
        # Chamamos os MÉTODOS set_date na ConfigWindow para atualizar seus QDateEdit
        self.config_window.set_start_date(self.date_start_input.date())
        self.config_window.set_end_date(self.date_end_input.date())

        self.config_window.populate_search_terms()
        self.config_window.show()
        
    def open_log_window(self):
        """Cria e mostra a janela de Histórico GERAL de Erros."""
        if self.log_window is None:
            self.log_window = ErrorLogWindow(parent=self) 
            self.log_window.setWindowTitle("Nexus - Histórico de Erros de Execução")
            self.log_window.title_label.setText('Histórico de Erros e Falhas')
            self.log_window.destroyed.connect(self._reset_log_window)
            self.log_window.log_list_items = [] 
            
        self.log_window.show()
        self.hide() 

    def _reset_log_window(self):
        """Reseta a referência da janela de log quando ela é fechada."""
        self.log_window = None

    # --- NOVO MÉTODO DELEGADO: Conecta Histórico a Resultados ---
    def open_results_for_history(self, articles):
        """
        Recebe a lista de artigos históricos da HistoryWindow e os exibe 
        na ResultsWindow (o método HistoryWindow chama este método).
        """
        self.open_results_window(articles)
        
    # --- NOVOS MÉTODOS DE MANIPULAÇÃO DE DADOS (Conectados pelo LogListItem) ---
    def add_search_term_from_log(self, term):
        if term and term.strip() not in self.default_search_config['search_terms']:
            cleaned_term = term.strip()
            self.default_search_config['search_terms'].append(cleaned_term)
            print(f"✅ Termo '{cleaned_term}' adicionado à configuração de busca.")
            if self.config_window and self.config_window.isVisible():
                self.config_window.add_search_term_external(cleaned_term) 
                
    def mark_article_valid_from_log(self, article_data):
        print(f"✅ Artigo ID {article_data['id']} ('{article_data['titulo']}') marcado como válido e movido.")

# Bloco de execução principal para teste (se este for seu arquivo main_window.py)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchWindow() # Instancia sua janela principal
    window.show()
    sys.exit(app.exec())