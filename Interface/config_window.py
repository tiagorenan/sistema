from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QScrollArea, QSizePolicy, QSpacerItem, QInputDialog # Adicionar QInputDialog se for usar a edição real
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, QDate

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"
VERMELHO_EXCLUIR = "#dc3545"

# Dados simulados para o padrão de busca
DEFAULT_CONFIG = {
    'platforms': ['Scielo', 'PubMed', 'Lilacs'],
    'date_start': '01/01/2021',
    'date_end': QDate.currentDate().toString("dd/MM/yyyy"),
    'search_terms': [
        "HC*EBSERH",
        '"HC*UFPE"',
        '"Hospital das Clínicas - UFPE"',
        '"Hospital das Clínicas - Universidade Federal de Pernambuco"',
        '"Hospital das Clínicas at the Universidade Federal de Pernambuco"',
        '"Hospital das Clínicas da UFPE"',
        '"Hospital das Clínicas da Universidade Federal de Pernambuco"',
        '"Hospital das Clínicas de Pernambuco"',
    ]
}

# --- Widget Customizado para a Linha de Termo de Busca ---

class SearchTermItem(QFrame):
    """Representa um termo de busca na lista com botões de ação."""

    def __init__(self, term, parent=None):
        super().__init__(parent)
        self.term = term
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; margin-bottom: 3px; background-color: white;")
        
        main_hbox = QHBoxLayout(self)
        main_hbox.setContentsMargins(10, 5, 10, 5)
        
        self.term_label = QLabel(term)
        self.term_label.setWordWrap(True)
        self.term_label.setFont(QFont("Arial", 10))
        main_hbox.addWidget(self.term_label, 1)

        # Botão Editar
        btn_edit = QPushButton('Editar ✎')
        btn_edit.setStyleSheet(f"color: {AZUL_NEXUS}; border: none; padding: 5px;")
        btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        btn_edit.clicked.connect(self._edit_term)
        main_hbox.addWidget(btn_edit)

        # Botão Excluir
        btn_exclude = QPushButton('Excluir 🗑')
        btn_exclude.setStyleSheet(f"color: {VERMELHO_EXCLUIR}; border: none; padding: 5px;")
        btn_exclude.setCursor(QCursor(Qt.PointingHandCursor))
        btn_exclude.clicked.connect(self._exclude_term)
        main_hbox.addWidget(btn_exclude)
        
        # O parent agora é a ConfigWindow, que tem os métodos de manipulação
        self.config_window = parent 

    def _edit_term(self):
        """Abre uma caixa de diálogo para editar o termo."""
        if self.config_window:
            new_term, ok = QInputDialog.getText(self, 'Editar Termo de Busca', 'Novo Termo:', QLineEdit.Normal, self.term)
            
            if ok and new_term and new_term.strip() != self.term:
                self.config_window.update_search_term(self.term, new_term.strip())

    def _exclude_term(self):
        """Remove o termo de busca através da janela de configuração."""
        if self.config_window and hasattr(self.config_window, 'remove_search_term'):
            self.config_window.remove_search_term(self.term)
        self.deleteLater() 

# --- Janela de Configuração Principal ---

class ConfigWindow(QMainWindow):
    """
    Janela para editar os padrões de busca, plataformas e datas predefinidas.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Editar Padrão de Busca')
        self.setGeometry(200, 200, 700, 800)
        
        self.parent_window = parent
        self.current_config = DEFAULT_CONFIG.copy()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self._setup_header()
        self._setup_content()
        
        self.populate_search_terms()

    def _setup_header(self):
        header_hbox = QHBoxLayout()
        
        # Botão Voltar (Conecta para voltar à Tela de Busca)
        back_button = QPushButton('←')
        back_button.setFixedSize(40, 40)
        back_button.setStyleSheet(f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; border-radius: 20px; font-weight: bold; font-size: 18px;")
        back_button.clicked.connect(self.return_to_search)
        header_hbox.addWidget(back_button, alignment=Qt.AlignLeft)
        
        title_label = QLabel('Editar Padrão de Busca')
        font = QFont("Arial", 18)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        header_hbox.addWidget(title_label, 1) 
        
        header_hbox.addItem(QSpacerItem(40, 40, QSizePolicy.Fixed, QSizePolicy.Fixed)) 

        self.main_layout.addLayout(header_hbox)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        self.main_layout.addWidget(separator)
        self.main_layout.addSpacing(15)

    def _setup_content(self):
        content_vbox = QVBoxLayout()
        content_vbox.setSpacing(15)

        # 1. Seleção de Bancos de Dados (Plataformas)
        content_vbox.addWidget(QLabel('<b>Selecione os Filtros</b>'))
        content_vbox.addWidget(QLabel('Banco de dados'))
        self.platform_hbox = QHBoxLayout()
        self.platform_buttons = {}
        platforms = ['Scielo', 'PubMed', 'Lilacs', 'Capes Periódicos']
        
        for platform in platforms:
            btn = QPushButton(platform)
            btn.setProperty('platform', platform)
            self.platform_buttons[platform] = btn
            
            if platform in self.current_config['platforms']:
                btn.setStyleSheet(self._get_platform_style(True))
            else:
                btn.setStyleSheet(self._get_platform_style(False))
            
            btn.clicked.connect(self._toggle_platform_selection)
            self.platform_hbox.addWidget(btn)
        
        self.platform_hbox.addStretch(1)
        content_vbox.addLayout(self.platform_hbox)

        # 2. Período de Busca Padrão
        content_vbox.addWidget(QLabel('Período de busca'))
        date_hbox = QHBoxLayout()

        date_hbox.addWidget(QLabel('A partir de'))
        self.date_start_input = QLineEdit(self.current_config['date_start'])
        self.date_start_input.setFixedWidth(100)
        self.date_start_input.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        date_hbox.addWidget(self.date_start_input)
        
        btn_calendar_start = QPushButton('📅')
        btn_calendar_start.setFixedSize(30, 30)
        btn_calendar_start.setStyleSheet(f"background-color: {CINZA_FUNDO}; border: 1px solid #ccc; margin-left: -1px;")
        date_hbox.addWidget(btn_calendar_start)
        
        date_hbox.addWidget(QLabel('Até'))
        self.date_end_input = QLineEdit(self.current_config['date_end'])
        self.date_end_input.setFixedWidth(100) 
        self.date_end_input.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        date_hbox.addWidget(self.date_end_input)

        btn_calendar_end = QPushButton('📅')
        btn_calendar_end.setFixedSize(30, 30)
        btn_calendar_end.setStyleSheet(f"background-color: {CINZA_FUNDO}; border: 1px solid #ccc; margin-left: -1px;")
        date_hbox.addWidget(btn_calendar_end)

        date_hbox.addStretch(1)
        content_vbox.addLayout(date_hbox)

        # 3. Adicionar Termos de Busca
        content_vbox.addWidget(QLabel('Adicionar Termos de Busca'))
        add_term_hbox = QHBoxLayout()
        self.new_term_input = QLineEdit()
        self.new_term_input.setPlaceholderText("Adicionar Termo de busca")
        self.new_term_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        add_term_hbox.addWidget(self.new_term_input, 1)

        btn_add = QPushButton('Adicionar +')
        btn_add.setStyleSheet(f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 10px 15px; font-weight: bold; border-radius: 5px;")
        btn_add.clicked.connect(self.add_search_term)
        add_term_hbox.addWidget(btn_add)
        
        content_vbox.addLayout(add_term_hbox)

        # 4. Lista de Termos de Busca
        content_vbox.addWidget(QLabel('<b>Termos de Busca</b>'))

        # Área de Rolagem para os Termos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.term_list_widget = QWidget()
        self.term_list_widget.setStyleSheet(f"background-color: {CINZA_FUNDO};")
        self.term_list_vbox = QVBoxLayout(self.term_list_widget)
        self.term_list_vbox.setContentsMargins(0, 0, 0, 0)
        self.term_list_vbox.setSpacing(5)

        self.scroll_area.setWidget(self.term_list_widget)
        content_vbox.addWidget(self.scroll_area, 1)
        
        # 5. Botão de Salvar (Apenas simulação)
        btn_save = QPushButton('SALVAR CONFIGURAÇÃO')
        btn_save.setStyleSheet(f"background-color: green; color: {BRANCO_PADRAO}; padding: 12px; font-weight: bold; border-radius: 5px; margin-top: 20px;")
        btn_save.clicked.connect(self._save_config)
        content_vbox.addWidget(btn_save)

        self.main_layout.addLayout(content_vbox)
        self.main_layout.addStretch(1)
        
        footer_label = QLabel('© EBSERH')
        footer_label.setFont(QFont("Arial", 8))
        footer_label.setAlignment(Qt.AlignRight)
        self.main_layout.addWidget(footer_label)

    # ------------------------------------------------------------------
    # --- MÉTODOS DE INTERAÇÃO E LÓGICA ---
    # ------------------------------------------------------------------

    def _get_platform_style(self, is_selected):
        """Retorna o estilo para os botões de plataforma."""
        base = "padding: 5px 10px; border-radius: 15px;"
        if is_selected:
            return f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; border: 1px solid {AZUL_NEXUS}; {base}"
        else:
            return f"background-color: {BRANCO_PADRAO}; color: {AZUL_NEXUS}; border: 1px solid {AZUL_NEXUS}; {base}"

    def _toggle_platform_selection(self):
        """Alterna a seleção da plataforma."""
        button = self.sender()
        platform = button.property('platform')
        
        if platform in self.current_config['platforms']:
            self.current_config['platforms'].remove(platform)
            button.setStyleSheet(self._get_platform_style(False))
        else:
            self.current_config['platforms'].append(platform)
            button.setStyleSheet(self._get_platform_style(True))
            
        print(f"Plataformas selecionadas: {self.current_config['platforms']}")

    def populate_search_terms(self):
        """Preenche a lista visual com os termos de busca atuais."""
        
        # Limpa widgets existentes
        while self.term_list_vbox.count() > 0:
            item = self.term_list_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Adiciona os termos
        for term in self.current_config['search_terms']:
            item = SearchTermItem(term, parent=self)
            self.term_list_vbox.addWidget(item)

        # Adiciona espaçador para garantir que a lista fique no topo
        self.term_list_vbox.addStretch(1)

    def add_search_term(self):
        """Adiciona um novo termo de busca à lista (via input manual)."""
        new_term = self.new_term_input.text().strip()
        self._internal_add_term(new_term)

    # NOVO MÉTODO: Chamado externamente pela SearchWindow
    def add_search_term_external(self, term):
        """Adiciona um termo de busca vindo de uma fonte externa (ex: LogWindow)."""
        self._internal_add_term(term)
        
    def _internal_add_term(self, new_term):
        """Lógica central para adicionar um termo (manual ou externo)."""
        if new_term and new_term not in self.current_config['search_terms']:
            self.current_config['search_terms'].append(new_term)
            self.new_term_input.clear()
            self.populate_search_terms()
            self._save_config() # Salva automaticamente
            print(f"Termo adicionado: {new_term}")
            return True
        elif new_term:
            print(f"Termo '{new_term}' já existe.")
            return False
        return False
    
    def remove_search_term(self, term_to_remove):
        """Remove um termo de busca da lista e atualiza a UI."""
        if term_to_remove in self.current_config['search_terms']:
            self.current_config['search_terms'].remove(term_to_remove)
            self.populate_search_terms()
            print(f"Termo removido: {term_to_remove}")
            self._save_config() # Salva automaticamente após remover
            return True
        return False
    
    def update_search_term(self, old_term, new_term):
        """Atualiza um termo de busca na lista."""
        try:
            index = self.current_config['search_terms'].index(old_term)
            if new_term not in self.current_config['search_terms']:
                self.current_config['search_terms'][index] = new_term
                self.populate_search_terms()
                self._save_config()
                print(f"Termo atualizado de '{old_term}' para '{new_term}'.")
                return True
            else:
                print(f"O termo '{new_term}' já existe na lista.")
                return False
        except ValueError:
            print(f"Erro: O termo original '{old_term}' não foi encontrado.")
            return False

    def _save_config(self):
        """Salva a configuração atual (simulada) e aplica na tela principal."""
        self.current_config['date_start'] = self.date_start_input.text()
        self.current_config['date_end'] = self.date_end_input.text()

        print("Configuração salva (Simulação):")
        print(self.current_config)

        # Se houver uma janela principal, atualiza seus filtros
        if self.parent_window and hasattr(self.parent_window, 'apply_default_config'):
            self.parent_window.apply_default_config(self.current_config)
            
    def return_to_search(self):
        """Fecha esta janela e exibe a janela pai (SearchWindow)."""
        self._save_config() # Garante que as mudanças sejam salvas ao voltar
        self.close()
        if self.parent_window:
            self.parent_window.show()