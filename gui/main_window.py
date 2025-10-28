from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QSpacerItem, QSizePolicy, QButtonGroup
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QDate, QTime

# Importações de outras janelas e dados simulados
from gui.results_window import ResultsWindow, SIMULATED_ARTICLES 
from gui.config_window import ConfigWindow, DEFAULT_CONFIG # Importa ConfigWindow e o estado padrão

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"  
CINZA_FUNDO = "#f7f7f7" 
BRANCO_PADRAO = "white"

class SearchWindow(QMainWindow):
    """
    Janela principal da aplicação (Tela de Busca).
    Gerencia a seleção de filtros e a navegação para a tela de resultados.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Tela de Busca')
        self.setGeometry(100, 100, 800, 600)
        
        self.config_window = None 
        self.results_window = None 
        
        # Estado inicial (carrega do DEFAULT_CONFIG, que será atualizado pela ConfigWindow)
        self.default_search_config = DEFAULT_CONFIG.copy()
        self.current_search_scope = 'Tema'          
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self._setup_header()
        self._setup_content()
        self._setup_footer()
        
        # Aplica a configuração inicial e atualiza a UI
        self.apply_default_config(self.default_search_config, initial=True)
        self._update_stats_display()

    def _setup_header(self):
        header_hbox = QHBoxLayout()
        
        voltar_button = QPushButton('←')
        voltar_button.setFixedSize(30, 30)
        voltar_button.setStyleSheet("background-color: white; border: none; font-size: 16px;")
        voltar_button.clicked.connect(self.close) 
        header_hbox.addWidget(voltar_button, alignment=Qt.AlignLeft)
        
        header_label = QLabel('Nexus Pesquisa HC-UFPE')
        font = QFont("Arial", 14)
        font.setBold(True)
        header_label.setFont(font)
        header_label.setAlignment(Qt.AlignCenter) 
        header_hbox.addWidget(header_label, 1)
        
        header_hbox.addItem(QSpacerItem(30, 30, QSizePolicy.Fixed, QSizePolicy.Fixed)) 

        self.main_layout.addLayout(header_hbox)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        self.main_layout.addWidget(separator)


    def _setup_content(self):
        content_hbox = QHBoxLayout()
        
        # Coluna 1: Filtros (Esquerda)
        self.filtro_frame = QFrame()
        self.filtro_layout = QVBoxLayout(self.filtro_frame)
        self._setup_filters()
        content_hbox.addWidget(self.filtro_frame, 2) 

        # Coluna 2: Estatísticas (Direita)
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
        
        # 1. Banco de Dados
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
        self.date_start_input = QLineEdit()
        self.date_start_input.setFixedWidth(80) 
        self.date_start_input.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        self.date_hbox.addWidget(self.date_start_input)
        
        self.date_hbox.addWidget(QLabel('Até'))
        self.date_end_input = QLineEdit()
        self.date_end_input.setFixedWidth(80) 
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
        
        # 4. Editar Padrão de Busca
        self.filtro_layout.addStretch(1) 

        edit_button = QPushButton('✎ Editar Padrão de Busca')
        edit_button.setStyleSheet("padding: 8px; margin-top: 15px; border: 1px solid #ddd; background-color: #f0f0f0; border-radius: 4px;")
        edit_button.clicked.connect(self.open_config_window)
        self.filtro_layout.addWidget(edit_button)


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
        """Atualiza a exibição das estatísticas na lateral (simulação)."""
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
        footer_label = QLabel('© EBSERH')
        footer_label.setFont(QFont("Arial", 8))
        footer_label.setAlignment(Qt.AlignRight)
        self.main_layout.addWidget(footer_label)

    # ------------------------------------------------------------------
    # --- MÉTODOS DE INTERAÇÃO E CONFIGURAÇÃO ---
    # ------------------------------------------------------------------

    def _get_platform_style(self, is_selected):
        """Retorna o estilo para os botões de plataforma."""
        base = "border: 1px solid {AZUL_NEXUS}; padding: 5px 10px; border-radius: 15px;".format(AZUL_NEXUS=AZUL_NEXUS)
        if is_selected:
            return f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; {base}"
        else:
            return f"background-color: {BRANCO_PADRAO}; color: {AZUL_NEXUS}; {base}"

    def _get_scope_style(self, is_selected):
        """Retorna o estilo para os botões de escopo."""
        base = "border: none; padding: 5px 10px; border-radius: 15px;"
        if is_selected:
            return f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; {base}"
        else:
            return f"background-color: {BRANCO_PADRAO}; color: {AZUL_NEXUS}; {base}"


    def _toggle_platform_selection(self):
        """Alterna a seleção da plataforma (Múltipla Seleção)."""
        button = self.sender()
        platform = button.property('platform')
        
        # Se for clicado, remove a seleção manual e usa os dados do campo (melhor UX)
        if platform in self.default_search_config['platforms']:
            self.default_search_config['platforms'].remove(platform)
        else:
            self.default_search_config['platforms'].append(platform)
            
        button.setStyleSheet(self._get_platform_style(platform in self.default_search_config['platforms']))


    def _select_search_scope(self):
        """Seleciona o escopo de busca (Seleção Única)."""
        button = self.sender()
        new_scope = button.property('scope')
        
        # Resetar o estilo do botão anterior
        if self.current_search_scope and self.current_search_scope in self.scope_buttons:
            old_button = self.scope_buttons[self.current_search_scope]
            old_button.setStyleSheet(self._get_scope_style(False))

        # Aplicar novo estilo ao botão selecionado
        button.setStyleSheet(self._get_scope_style(True))
        self.current_search_scope = new_scope
        
    def apply_default_config(self, config_data, initial=False):
        """Aplica a configuração padrão salva da ConfigWindow na tela de busca."""
        self.default_search_config = config_data.copy()
        
        # 1. Atualiza as Datas
        self.date_start_input.setText(self.default_search_config['date_start'])
        self.date_end_input.setText(self.default_search_config['date_end'])

        # 2. Atualiza os Botões de Plataforma
        for platform, btn in self.platform_buttons.items():
            is_selected = platform in self.default_search_config['platforms']
            btn.setStyleSheet(self._get_platform_style(is_selected))
            
        # 3. Atualiza o Escopo
        if initial and self.current_search_scope in self.scope_buttons:
            self.scope_buttons[self.current_search_scope].setStyleSheet(self._get_scope_style(True))


    # --- Métodos de Ação e Navegação ---
    
    def iniciar_busca(self):
        """
        Coleta os dados do frontend (Termo manual ou Padrão) e abre a tela de resultados.
        """
        search_term_manual = self.search_term_input.text().strip()
        
        if search_term_manual:
            # Se houver um termo manual, a busca é customizada
            term_used = search_term_manual
            platforms_used = self.default_search_config['platforms']
            
        else:
            # Se não houver termo manual, usa os termos padrão da configuração para 'Atualizar o banco'
            term_used = "Padrão: " + ", ".join(self.default_search_config['search_terms'][:3]) + "..."
            platforms_used = self.default_search_config['platforms']
            
            # Aqui, na busca real, você usaria o self.default_search_config['search_terms'] completo
            
        print(f"Iniciando busca: Termo='{term_used}' | Plataformas: {platforms_used}")
        
        # Simulação da chamada do backend
        articles = SIMULATED_ARTICLES 

        self.open_results_window(articles)

    def open_results_window(self, articles):
        """Abre a janela de Resultados e esconde a janela atual."""
        self.results_window = ResultsWindow(parent=self, articles=articles) 
        self.hide() 
        self.results_window.show()

    def open_config_window(self):
        """Abre a janela de Configuração."""
        if not self.config_window:
            # Passa a configuração atual para a janela de configuração
            self.config_window = ConfigWindow(parent=self)
            self.config_window.current_config = self.default_search_config.copy()
        
        # Garante que a ConfigWindow reflita o estado atual ao abrir
        self.config_window.date_start_input.setText(self.default_search_config['date_start'])
        self.config_window.date_end_input.setText(self.default_search_config['date_end'])
        self.config_window.populate_search_terms()
        self.config_window.show()