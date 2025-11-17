import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QSpacerItem, QSizePolicy, QButtonGroup, QDateEdit, QMessageBox
)
from PySide6.QtGui import QFont, QIcon, QPixmap 
from PySide6.QtCore import Qt, QEvent, QRect, QDate

# Importações de outras janelas e dados simulados
# Assumindo que estas importações estão corretas de acordo com a sua estrutura de pastas
from Interface.results_window import ResultsWindow
from Interface.config_window import ConfigWindow, DEFAULT_CONFIG 
from Interface.log_windows import ErrorLogWindow 
from Interface.historico_window import HistoryWindow 

# Importações para busca com termos padrão
from processing.search_helper import get_search_terms_for_affiliation, format_search_query_for_pubmed
from database.db_manager import DatabaseManager 
from database.models import SearchHistory


import sys
import os

# --- FUNÇÃO DE AJUSTE DE CAMINHO PARA PYINSTALLER ---
def resource_path(relative_path):
    """Obtém o caminho absoluto para recursos, para funcionar no modo dev e no executável."""
    try:
        # PyInstaller cria um caminho temporário (_MEIPASS) e coloca os recursos lá
        base_path = sys._MEIPASS
    except Exception:
        # Modo normal (quando não é executável)
        # Se SearchWindow.py estiver em 'Interface', ajustamos o caminho base
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 

    # Se estiver em 'Interface', o path relativo precisa ser ajustado:
    # Se relative_path for 'Interface/imagens/logo.png', o join será:
    # /sistema/Interface/imagens/logo.png
    return os.path.join(base_path, relative_path)
# ---------------------------------------------------

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
        
        # --- CORREÇÃO DE ATRIBUTO PARA ResultsWindow ---
        # Torna a função resource_path acessível via self.resource_path
        self.resource_path = resource_path 
        # ---------------------------------------------
        
        # --- Definir o Ícone da Janela (Logo Nexus) ---
        try:
            # O path relativo a resource_path base é 'Interface/imagens/...'
            icon_path = resource_path("Interface/imagens/logo_azul.png")
            self.setWindowIcon(QIcon(icon_path))
            print(f"Ícone da janela (Nexus) carregado de: {icon_path}")
        except Exception as e:
            print(f"Erro ao carregar o ícone da janela (Nexus): {e}")
        
        self.config_window = None 
        self.results_window = None 
        self.log_window = None 
        self.history_window = None 
        self.is_menu_open = False
        
        # --- INTEGRAÇÃO COM BANCO DE DADOS ---
        try:
            self.db_manager = DatabaseManager()
            print("[OK] DatabaseManager inicializado na SearchWindow")
        except Exception as e:
            print(f"[AVISO] Erro ao inicializar DatabaseManager: {e}")
            self.db_manager = None
        
        self.default_search_config = DEFAULT_CONFIG.copy()
        self.current_search_scope = 'Tema'
        # CORREÇÃO DE SINTAXE (LINHA 88)
        self.current_search_id = None # ID da busca atual no BD
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Chamadas de setup
        self._setup_header()
        self._setup_content()
        self._setup_footer()
        
        self._setup_sidebar() 
        
        self.installEventFilter(self)
        self.apply_default_config(self.default_search_config, initial=True)
        # self._update_stats_display_from_database() 

    # --- MÉTODOS DE CONTROLE DE MENU (Omitidos para brevidade) ---
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

    # --- Filtro de Eventos e Redimensionamento (Omitidos para brevidade) ---
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
    
    # --- Configuração do Menu Lateral (Omitido para brevidade) ---
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
        nexus_logo_pixmap_small = QPixmap(resource_path("Interface/imagens/logo_azul.png"))
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

    # --- Configuração de Conteúdo e Filtros (Omitido para brevidade) ---
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
        
        # --- ESTILO PARA CORRIGIR O CALENDÁRIO (TEXTO PRETO) ---
        CALENDAR_STYLE = """
            QDateEdit {
                padding: 5px; 
                border: 1px solid #ccc;
            }
            QCalendarWidget QWidget {
                /* Cor de fundo para as barras de navegação */
                background-color: #f0f0f0; 
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                /* Cor de fundo para a barra de navegação (mês e ano) */
                background-color: #e0e0e0;
            }
            QCalendarWidget QToolButton {
                /* Botões de navegação (setas e mês/ano) */
                color: black; 
                background-color: transparent;
            }
            QCalendarWidget QToolButton:hover {
                 background-color: #cccccc;
            }
            QCalendarWidget QToolButton:pressed {
                 background-color: #aaaaaa;
            }
            QCalendarWidget QAbstractItemView {
                /* Visualização dos dias do mês */
                color: black;
                selection-background-color: #3b5998;
                selection-color: white;
            }
            /* Garante que o texto dos dias (domingo/sábado) não seja vermelho/branco padrão */
            QCalendarWidget QAbstractItemView::item:disabled {
                color: #808080; /* Cor cinza para dias desabilitados */
            }
        """
        # ----------------------------------------------
        
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
        # APLICAÇÃO DO NOVO ESTILO (start)
        self.date_start_input.setStyleSheet(CALENDAR_STYLE)
        self.date_hbox.addWidget(self.date_start_input)
        
        self.date_hbox.addWidget(QLabel('Até'))
        self.date_end_input = QDateEdit(self)
        self.date_end_input.setDisplayFormat("dd/MM/yyyy")
        self.date_end_input.setCalendarPopup(True) 
        self.date_end_input.setFixedWidth(120) 
        # APLICAÇÃO DO NOVO ESTILO (end)
        self.date_end_input.setStyleSheet(CALENDAR_STYLE)
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

    def _update_stats_display_from_database(self):
        """Carrega estatísticas do BD: total de artigos e quantidade por plataforma."""
        # Este método não será chamado na inicialização, apenas após uma busca.
        if not self.db_manager:
            print("[AVISO] Estatísticas simuladas - DatabaseManager não disponível")
            # Fallback para dados simulados
            total = 500
            stats = {
                'PubMed': 250,
                'Scielo': 150,
                'Lilacs': 75,
                'Capes Periódicos': 25
            }
        else:
            try:
                db_stats = self.db_manager.get_stats()
                total = db_stats.get('articles_total', 0)
                # Para exibir por plataforma usamos uma aproximação: artigos validados totais
                stats = {
                    'PubMed': db_stats.get('articles_validated', 0),
                    'Scielo': 0,
                    'Lilacs': 0,
                    'Capes Periódicos': 0
                }
                print(f"[OK] Estatísticas carregadas do BD: {total} artigos no total")
            except Exception as e:
                print(f"[AVISO] Erro ao carregar estatísticas do BD: {e}")
                # Fallback para simulados
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

        # --- CORREÇÃO 3: Ajuste no caminho da logo do HC-UFPE ---
        hc_logo_label = QLabel()
        # Assume que 'hc_logo.png' está em 'Interface/imagens/'
        hc_logo_pixmap = QPixmap(resource_path("Interface/imagens/hc_logo.png")) 
        if not hc_logo_pixmap.isNull():
            # Redimensionar para um tamanho maior (150x45)
            scaled_hc_pixmap = hc_logo_pixmap.scaled(150, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
            hc_logo_label.setPixmap(scaled_hc_pixmap)
            # Adicionar à direita no rodapé
            footer_hbox.addWidget(hc_logo_label, alignment=Qt.AlignRight) 
            print(f"Logo do HC-UFPE (PNG, maior) carregada de: Interface/imagens/hc_logo.png")
        else:
            print("Não foi possível carregar a logo do HC-UFPE (PNG) para o rodapé. Verifique o caminho.")
        
        self.main_layout.addLayout(footer_hbox) 

    # --- MÉTODOS DE INTERAÇÃO E CONFIGURAÇÃO (Omitidos para brevidade) ---
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

    # --- Métodos de Ação e Navegação (Omitidos para brevidade) ---
    def iniciar_busca(self):
        """Inicia a busca de artigos usando termos cadastrados na BD."""
        search_term_manual = self.search_term_input.text().strip()
        self.default_search_config['date_start'] = self.date_start_input.date().toString("dd/MM/yyyy")
        self.default_search_config['date_end'] = self.date_end_input.date().toString("dd/MM/yyyy")
        
        if search_term_manual:
            # Usuário digitou um termo manualmente
            term_used = search_term_manual
            platforms_used = self.default_search_config['platforms']
        else:
            # Usar termos padrão cadastrados na tabela affiliation_variations
            try:
                default_terms = get_search_terms_for_affiliation("HC-UFPE")
                if default_terms:
                    # Formatar como query PubMed (ex: ("termo1" OR "termo2" OR ...))
                    term_used = format_search_query_for_pubmed(default_terms)
                    print(f"🔍 Usando {len(default_terms)} variações de afiliação para busca automática")
                else:
                    # Fallback para termos configurados
                    term_used = "Padrão: " + ", ".join(self.default_search_config['search_terms'][:3]) + "..."
            except Exception as e:
                print(f"[AVISO] Erro ao recuperar termos padrão: {e}")
                term_used = "Padrão: " + ", ".join(self.default_search_config['search_terms'][:3]) + "..."
            
            platforms_used = self.default_search_config['platforms']
        
        print(f"[OK] Iniciando busca: Termo='{term_used[:50]}...' | Plataformas: {platforms_used}")
        print(f"[OK] Período: {self.default_search_config['date_start']} a {self.default_search_config['date_end']}")
        
        # Coletar artigos reais da(s) plataforma(s) selecionada(s).
        articles = []
        if 'PubMed' in platforms_used:
            try:
                from processing.collectors.pubmed import search_by_affiliation

                if search_term_manual:
                    pub_terms = [search_term_manual]
                else:
                    try:
                        pub_terms = get_search_terms_for_affiliation("HC-UFPE")
                    except Exception:
                        pub_terms = []

                pub_results = search_by_affiliation(pub_terms,
                                                    date_start=self.default_search_config['date_start'],
                                                    date_end=self.default_search_config['date_end'],
                                                    max_results=200)

                for idx, r in enumerate(pub_results, start=1):
                    mapped = {
                        'id': idx,
                        'titulo': r.get('title', r.get('titulo', 'N/A')),
                        'autores': r.get('authors', r.get('autores', '')),
                        'doi': r.get('doi', ''),
                        'publicacao': f"{r.get('publication_date','N/A')} (PubMed)",
                        'link': r.get('url', ''),
                        'resumo': r.get('abstract', r.get('resumo', '')),
                        'status': 'NOVO'
                    }
                    articles.append(mapped)

                print(f"[OK] PubMed: {len(pub_results)} artigos encontrados e mapeados")
            except Exception as e:
                print(f"[AVISO] Erro ao consultar PubMed: {e}")

        # Se nenhuma plataforma retornou artigos, usar dados simulados como fallback
        if not articles:
            # Não use SIMULATED_VALIDATED_ARTICLES se não for importada! Use lista vazia para simulação.
            articles = [] 
        
        # Determinar contagem final
        results_total = len(articles)

        # --- SALVAR BUSCA NO BD ---
        if self.db_manager:
            try:
                search_obj = SearchHistory(
                    search_term=term_used,
                    platforms=",".join(platforms_used),
                    date_start=self.default_search_config['date_start'],
                    date_end=self.default_search_config['date_end'],
                    
                    # CORREÇÃO AQUI: Salvar a contagem real de resultados
                    results_count=results_total 
                )
                self.current_search_id = self.db_manager.create_search_history(search_obj)
                print(f"[OK] Busca salva no BD com ID: {self.current_search_id}")
            except Exception as e:
                print(f"[AVISO] Erro ao salvar busca no BD: {e}")
                self.current_search_id = None
        
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
        
        self.config_window.set_start_date(self.date_start_input.date())
        self.config_window.set_end_date(self.date_end_input.date())

        self.config_window.populate_search_terms()
        self.config_window.show()
        
    def open_log_window(self):
        """Cria e mostra a janela de Histórico GERAL de Erros."""
        if self.log_window is None:
            errors_from_db = []
            if self.db_manager:
                try:
                    errors_from_db = self.db_manager.read_error_logs()
                    errors_from_db = [
                        {
                            'id': e.id,
                            'termo_busca': e.search_term,
                            'titulo': e.article_title,
                            'autores': '',
                            'doi': e.article_doi,
                            'data_log': QDate(e.error_date.year, e.error_date.month, e.error_date.day) if e.error_date else QDate.currentDate(),
                            'publicacao_ano': '',
                            'publicacao_plataforma': e.platform or '',
                            'link': '',
                            'resumo': e.error_reason,
                            'tipo_erro': e.error_type
                        } for e in errors_from_db
                    ]
                    print(f"[OK] {len(errors_from_db)} erros carregados do BD")
                except Exception as e:
                    print(f"[AVISO] Erro ao carregar erros do BD: {e}")
            
            self.log_window = ErrorLogWindow(parent=self, errors=errors_from_db if errors_from_db else None)
            self.log_window.setWindowTitle("Nexus - Histórico de Erros de Execução")
            self.log_window.title_label.setText('Histórico de Erros e Falhas')
            self.log_window.destroyed.connect(self._reset_log_window)
            self.log_window.log_list_items = [] 
            
        self.log_window.show()
        self.hide() 

    def _reset_log_window(self):
        """Reseta a referência da janela de log quando ela é fechada."""
        self.log_window = None
    
    def closeEvent(self, event):
        """Fecha a conexão com o BD quando a janela é fechada."""
        if self.db_manager:
            try:
                self.db_manager.close()
                print("[OK] Conexão com BD fechada")
            except Exception as e:
                print(f"[AVISO] Erro ao fechar BD: {e}")
        event.accept()

    def open_results_for_history(self, articles):
        """Recebe a lista de artigos históricos da HistoryWindow e os exibe na ResultsWindow."""
        self.open_results_window(articles)
        
    def add_search_term_from_log(self, term):
        if term and term.strip() not in self.default_search_config['search_terms']:
            cleaned_term = term.strip()
            self.default_search_config['search_terms'].append(cleaned_term)
            print(f"✅ Termo '{cleaned_term}' adicionado à configuração de busca.")
            if self.config_window and self.config_window.isVisible():
                self.config_window.add_search_term_external(cleaned_term) 
                
    def mark_article_valid_from_log(self, article_data):
        """Marca um artigo do log como VALIDADO — insere ou atualiza o artigo na tabela `articles`."""
        if not self.db_manager:
            print("[AVISO] DatabaseManager não disponível — não foi possível marcar artigo como válido.")
            QMessageBox.warning(self, "Aviso", "Conexão com o banco não disponível.")
            return

        title = article_data.get('titulo') or article_data.get('title') or 'N/A'
        authors = article_data.get('autores') or article_data.get('authors') or ''
        doi_raw = article_data.get('doi') or ''
        doi = doi_raw if doi_raw and doi_raw.strip().upper() != 'N/A' else ''
        platform = article_data.get('publicacao_plataforma') or article_data.get('publicacao') or 'Desconhecido'
        url = article_data.get('link') or ''
        abstract = article_data.get('resumo') or article_data.get('abstract') or ''

        try:
            existing = None
            if doi:
                existing = self.db_manager.read_article_by_platform_and_doi(platform, doi)
            if not existing and url:
                existing = self.db_manager.read_article_by_platform_and_url(platform, url)

            if existing:
                from database.models import Article
                updated = self.db_manager.update_article_status(existing.id, Article.Status.VALIDATED.value)
                if updated:
                    QMessageBox.information(self, "Sucesso", f"Artigo atualizado como VALIDADO (ID {existing.id}).")
                    print(f"[OK] Artigo existente (ID {existing.id}) marcado como VALIDADO")
                else:
                    QMessageBox.warning(self, "Aviso", "Falha ao atualizar status do artigo.")
                    print(f"[AVISO] Falha ao atualizar status do artigo existente (ID {existing.id})")
            else:
                from database.models import Article as ArticleModel
                art_obj = ArticleModel(
                    title=title,
                    authors=authors,
                    doi=doi,
                    platform=platform,
                    abstract=abstract,
                    url=url,
                    status='VALIDADO'
                )
                new_id = self.db_manager.create_article(art_obj)
                if new_id:
                    QMessageBox.information(self, "Sucesso", f"Artigo inserido e marcado como VALIDADO (ID {new_id}).")
                    print(f"[OK] Novo artigo inserido com ID {new_id} e status VALIDADO")
                else:
                    QMessageBox.warning(self, "Aviso", "Falha ao inserir o artigo como VALIDADO.")
                    print("[AVISO] Falha ao inserir novo artigo como VALIDADO")
        except Exception as e:
            print(f"[ERRO] Ao marcar artigo como válido: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao processar a ação: {e}")

# Bloco de execução principal para teste (se este for seu arquivo main_window.py)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchWindow() # Instancia sua janela principal
    window.show()
    sys.exit(app.exec())