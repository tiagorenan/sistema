import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QSpacerItem, QSizePolicy, QButtonGroup
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QEvent, QRect # Importa QEvent e QRect

# Importações de outras janelas e dados simulados (Usando 'Interface' em vez de 'gui')
from Interface.results_window import ResultsWindow, SIMULATED_VALIDATED_ARTICLES 
from Interface.config_window import ConfigWindow, DEFAULT_CONFIG # Assumindo a existência deste arquivo
from .log_windows import ErrorLogWindow 

# --- Definições de Cores (Linhas limpas de caracteres especiais) ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"

class SearchWindow(QMainWindow):
    """
    Janela principal da aplicação (Tela de Busca).
    Gerencia a seleção de filtros e a navegação para a tela de resultados e log.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Tela de Busca')
        self.setGeometry(100, 100, 800, 600)
        
        self.config_window = None 
        self.results_window = None 
        self.log_window = None # Referência para a janela de Histórico de Erros
        self.is_menu_open = False
        
        # Estado inicial
        self.default_search_config = DEFAULT_CONFIG.copy()
        self.current_search_scope = 'Tema'      
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Chamadas de setup
        self._setup_header()
        self._setup_content()
        self._setup_footer()
        
        self._setup_sidebar() 
        
        # Instala o filtro de eventos para detectar cliques fora do menu
        self.installEventFilter(self)
        
        # Aplica a configuração inicial e atualiza a UI
        self.apply_default_config(self.default_search_config, initial=True)
        self._update_stats_display()

    # --- NOVO: Filtro de Eventos ---
    def eventFilter(self, source, event):
        """Filtra eventos de clique para fechar o menu lateral se o clique for fora dele."""
        if self.is_menu_open and event.type() == QEvent.MouseButtonPress:
            menu_rect = self.menu_sidebar.geometry()
            global_menu_rect = QRect(self.mapToGlobal(menu_rect.topLeft()), menu_rect.size())
            
            if not global_menu_rect.contains(event.globalPos()):
                self.toggle_menu()
        return super().eventFilter(source, event)

    def resizeEvent(self, event):
        """Redimensiona o menu lateral junto com a janela principal."""
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
        btn_historico.clicked.connect(lambda: print("Abrir Histórico de Pesquisa (A ser implementado)"))
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

    # --- Método para Abrir/Fechar o Menu ---
    def toggle_menu(self):
        self.is_menu_open = not self.is_menu_open
        if self.is_menu_open:
            self.menu_sidebar.setGeometry(0, 0, self.menu_sidebar.width(), self.height())
            self.menu_sidebar.show()
            self.menu_button.setText('✕') 
        else:
            self.menu_sidebar.hide()
            self.menu_button.setText('☰') 

    def _setup_header(self):
        header_hbox = QHBoxLayout()
        
        self.menu_button = QPushButton('☰')
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.setStyleSheet("background-color: white; border: none; font-size: 16px; font-weight: bold;")
        self.menu_button.clicked.connect(self.toggle_menu) 
        header_hbox.addWidget(self.menu_button, alignment=Qt.AlignLeft)
        
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

    # --- DEFINIÇÃO DO MÉTODO FALTANTE ---
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

    # --- MÉTODOS DE INTERAÇÃO E CONFIGURAÇÃO ---

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
        
        if platform in self.default_search_config['platforms']:
            self.default_search_config['platforms'].remove(platform)
        else:
            self.default_search_config['platforms'].append(platform)
            
        button.setStyleSheet(self._get_platform_style(platform in self.default_search_config['platforms']))


    def _select_search_scope(self):
        """Seleciona o escopo de busca (Seleção Única)."""
        button = self.sender()
        new_scope = button.property('scope')
        
        if self.current_search_scope and self.current_search_scope in self.scope_buttons:
            old_button = self.scope_buttons[self.current_search_scope]
            old_button.setStyleSheet(self._get_scope_style(False))

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
            term_used = search_term_manual
            platforms_used = self.default_search_config['platforms']
            
        else:
            term_used = "Padrão: " + ", ".join(self.default_search_config['search_terms'][:3]) + "..."
            platforms_used = self.default_search_config['platforms']
            
        print(f"Iniciando busca: Termo='{term_used}' | Plataformas: {platforms_used}")
        
        # Simulação da chamada do backend, usando a variável com nome corrigido
        articles = SIMULATED_VALIDATED_ARTICLES 

        self.open_results_window(articles)

    def open_results_window(self, articles):
        """Abre a janela de Resultados e esconde a janela atual."""
        # Nota: Idealmente, aqui você passaria também os erros da busca atual, se houver
        self.results_window = ResultsWindow(parent=self, articles=articles) 
        self.hide() 
        self.results_window.show()

    # --- Wrappers para fechar o menu ao abrir uma nova janela ---
    def open_log_window_and_close_menu(self):
        """Abre a janela de Histórico de Erros e fecha o menu."""
        self.open_log_window()
        self.toggle_menu() 

    def open_config_window_and_close_menu(self):
        """Abre a janela de Configuração e fecha o menu."""
        self.open_config_window()
        self.toggle_menu()

    def open_config_window(self):
        """Abre a janela de Configuração."""
        if not self.config_window:
            self.config_window = ConfigWindow(parent=self)
            self.config_window.current_config = self.default_search_config.copy()
        
        self.config_window.date_start_input.setText(self.default_search_config['date_start'])
        self.config_window.date_end_input.setText(self.default_search_config['date_end'])
        self.config_window.populate_search_terms()
        self.config_window.show()

    # Método de navegação para a Janela de Log (Histórico Geral)
    def open_log_window(self):
        """Cria e mostra a janela de Histórico GERAL de Erros."""
        
        if self.log_window is None:
            # Não passa 'errors' para que ele use a lista padrão SIMULATED_FULL_ERRORS
            self.log_window = ErrorLogWindow(parent=self) 
            # Define o título correto para Histórico Geral
            self.log_window.setWindowTitle("Nexus - Histórico de Erros de Execução")
            self.log_window.title_label.setText('Histórico de Erros e Falhas')
            # Conecta os novos sinais da janela de Log ao SearchWindow
            self.log_window.destroyed.connect(self._reset_log_window)
            
            # Conexão dos novos sinais (mesmo que o log seja geral, a funcionalidade é a mesma)
            self.log_window.log_list_items = [] # Garante que a lista não é nula
            # Esta conexão deve ser feita na inicialização dos itens, mas a conexão geral no nível da janela funciona:
            # self.log_window.add_term_to_config.connect(self.add_search_term_from_log)
            # self.log_window.mark_as_valid.connect(self.mark_article_valid_from_log)
        
        self.log_window.show()
        self.hide() 

    def _reset_log_window(self):
        """Reseta a referência da janela de log quando ela é fechada."""
        self.log_window = None

    # --- NOVOS MÉTODOS DE MANIPULAÇÃO DE DADOS (Conectados pelo LogListItem) ---

    def add_search_term_from_log(self, term):
        """
        Recebe um novo termo do LogListItem (Registro de Erros) e o adiciona
        ao padrão de busca atual (default_search_config).
        """
        if term and term.strip() not in self.default_search_config['search_terms']:
            cleaned_term = term.strip()
            self.default_search_config['search_terms'].append(cleaned_term)
            print(f"✅ Termo '{cleaned_term}' adicionado à configuração de busca.")
            
            # Se a janela de Configuração estiver aberta, atualiza a lista visualmente
            if self.config_window and self.config_window.isVisible():
                self.config_window.populate_search_terms()
                
    def mark_article_valid_from_log(self, article_data):
        """
        Recebe um artigo rejeitado do LogListItem (Registro de Erros) e simula
        sua movimentação para a lista de artigos validados.
        """
        # Simulação: Na prática, você moveria este artigo de uma lista de 'Rejeitados'
        # ou 'Com Erro' para a lista de 'Validados'. Aqui, apenas simulamos a ação.
        
        print(f"✅ Artigo ID {article_data['id']} ('{article_data['titulo']}') marcado como válido e movido.")
        # Lógica real: Adicionar à base de dados de artigos validados.

# Se precisar de um bloco 'if __name__ == "__main__":' para testar, você precisará dos 
# outros arquivos (results_window, config_window, log_windows) e do PySide6.