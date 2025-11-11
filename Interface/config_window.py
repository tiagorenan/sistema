from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, 
    QScrollArea, QSizePolicy, QSpacerItem, QInputDialog, QDateEdit,
    QMessageBox
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from database.models import AffiliationVariation

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"
VERMELHO_EXCLUIR = "#dc3545"

# Dados padrão para o padrão de busca
DEFAULT_CONFIG = {
    'platforms': ['Scielo', 'PubMed', 'Lilacs'],
    'date_start': '01/01/2021',
    'date_end': QDate.currentDate().toString("dd/MM/yyyy"),
    'search_terms': []  # Será preenchido do banco de dados
}

# --- Widget Customizado para a Linha de Termo de Busca ---

class SearchTermItem(QFrame):
    """Representa um termo de busca na lista com botões de ação."""

    def __init__(self, term_id, original_text, normalized_text, parent=None):
        super().__init__(parent)
        self.term_id = term_id
        self.original_text = original_text
        self.normalized_text = normalized_text
        self.config_window = parent
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; margin-bottom: 3px; background-color: white;")
        
        main_hbox = QHBoxLayout(self)
        main_hbox.setContentsMargins(10, 5, 10, 5)
        
        # Exibe o texto original (o que o usuário vê)
        self.term_label = QLabel(original_text)
        self.term_label.setWordWrap(True)
        self.term_label.setFont(QFont("Arial", 10))
        main_hbox.addWidget(self.term_label, 1)

        # Botão Editar
        btn_edit = QPushButton('Editar')
        btn_edit.setStyleSheet(f"color: {AZUL_NEXUS}; border: none; padding: 5px;")
        btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        btn_edit.clicked.connect(self._edit_term)
        main_hbox.addWidget(btn_edit)

        # Botão Excluir
        btn_exclude = QPushButton('Excluir')
        btn_exclude.setStyleSheet(f"color: {VERMELHO_EXCLUIR}; border: none; padding: 5px;")
        btn_exclude.setCursor(QCursor(Qt.PointingHandCursor))
        btn_exclude.clicked.connect(self._exclude_term)
        main_hbox.addWidget(btn_exclude)

    def _edit_term(self):
        """Abre uma caixa de diálogo para editar o termo."""
        if self.config_window:
            new_term, ok = QInputDialog.getText(
                self, 
                'Editar Termo de Busca', 
                'Novo Termo:', 
                QLineEdit.Normal, 
                self.original_text
            )
            
            if ok and new_term and new_term.strip() != self.original_text:
                self.config_window.update_search_term(self.term_id, new_term.strip())

    def _exclude_term(self):
        """Remove o termo de busca através da janela de configuração."""
        if self.config_window:
            self.config_window.remove_search_term(self.term_id)
        self.deleteLater() 

# --- Janela de Configuração Principal ---

class ConfigWindow(QMainWindow):
    """
    Janela para editar os padrões de busca, plataformas e datas predefinidas.
    Conecta-se ao banco de dados para gerenciar variações de afiliação.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Editar Padrão de Busca')
        self.setGeometry(200, 200, 700, 800)
        
        self.parent_window = parent
        self.db = None
        self.current_config = DEFAULT_CONFIG.copy()
        
        # Inicializa o banco de dados
        self._initialize_database()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self._setup_header()
        self._setup_content()
        
        # Carrega termos do banco de dados
        self.populate_search_terms()

    def _initialize_database(self):
        """Inicializa a conexão com o banco de dados."""
        try:
            self.db = DatabaseManager()
            self.db.connect()
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao banco de dados: {e}")
            QMessageBox.warning(self, "Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{e}")

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

        # 2. Período de Busca Padrão (AGORA USANDO QDateEdit)
        content_vbox.addWidget(QLabel('Período de busca'))
        date_hbox = QHBoxLayout()

        date_hbox.addWidget(QLabel('A partir de'))
        
        # === QDateEdit - Data de Início ===
        self.date_start_input = QDateEdit(self)
        self.date_start_input.setDisplayFormat("dd/MM/yyyy")
        self.date_start_input.setCalendarPopup(True) 
        self.date_start_input.setFixedWidth(130)
        self.date_start_input.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        
        start_date = QDate.fromString(self.current_config['date_start'], "dd/MM/yyyy")
        self.date_start_input.setDate(start_date if start_date.isValid() else QDate.currentDate())
        
        date_hbox.addWidget(self.date_start_input)
        
        date_hbox.addWidget(QLabel('Até'))
        
        # === QDateEdit - Data Final ===
        self.date_end_input = QDateEdit(self)
        self.date_end_input.setDisplayFormat("dd/MM/yyyy")
        self.date_end_input.setCalendarPopup(True) 
        self.date_end_input.setFixedWidth(130) 
        self.date_end_input.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        
        end_date = QDate.fromString(self.current_config['date_end'], "dd/MM/yyyy")
        self.date_end_input.setDate(end_date if end_date.isValid() else QDate.currentDate())

        date_hbox.addWidget(self.date_end_input)
        
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
        
        # 5. Botão de Salvar
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
        """Preenche a lista visual com os termos de busca do banco de dados."""
        
        # Limpa widgets existentes
        while self.term_list_vbox.count() > 0:
            item = self.term_list_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Carrega termos do banco de dados (HC-UFPE)
        try:
            if self.db:
                variations = self.db.read_affiliation_variations_by_institution("HC-UFPE")
                
                if variations:
                    for variation in variations:
                        item = SearchTermItem(
                            term_id=variation.id,
                            original_text=variation.original_text,
                            normalized_text=variation.normalized_text,
                            parent=self
                        )
                        self.term_list_vbox.addWidget(item)
                else:
                    msg = QLabel("Nenhum termo de busca configurado para HC-UFPE.")
                    msg.setStyleSheet("color: #999; padding: 20px;")
                    self.term_list_vbox.addWidget(msg)
            else:
                msg = QLabel("Erro: Banco de dados não conectado.")
                msg.setStyleSheet("color: red; padding: 20px;")
                self.term_list_vbox.addWidget(msg)
                
        except Exception as e:
            print(f"[ERRO] Falha ao carregar termos de busca: {e}")
            msg = QLabel(f"Erro ao carregar termos: {str(e)}")
            msg.setStyleSheet("color: red; padding: 20px;")
            self.term_list_vbox.addWidget(msg)

        # Adiciona espaçador para garantir que a lista fique no topo
        self.term_list_vbox.addStretch(1)

    def add_search_term(self):
        """Adiciona um novo termo de busca à lista (via input manual)."""
        new_term = self.new_term_input.text().strip()
        self._internal_add_term(new_term)

    def add_search_term_external(self, term):
        """Adiciona um termo de busca vindo de uma fonte externa (ex: LogWindow)."""
        self._internal_add_term(term)
        
    def _internal_add_term(self, new_term):
        """Lógica central para adicionar um termo (manual ou externo) ao banco de dados."""
        if not new_term:
            QMessageBox.warning(self, "Campo vazio", "Digite um termo de busca antes de adicionar.")
            return False
        
        try:
            if self.db:
                # Verifica se o termo já existe
                variations = self.db.read_affiliation_variations_by_institution("HC-UFPE")
                existing_terms = [v.original_text for v in variations]
                
                if new_term in existing_terms:
                    QMessageBox.information(self, "Termo duplicado", f"O termo '{new_term}' já existe.")
                    return False
                
                # Cria nova variação de afiliação
                new_variation = AffiliationVariation(
                    original_text=new_term,
                    normalized_text=new_term,  # Pode ser normalizado conforme necessário
                    institution="HC-UFPE",
                    platform="Manual"
                )
                
                # Insere no banco de dados
                self.db.create_affiliation_variation(new_variation)
                self.new_term_input.clear()
                self.populate_search_terms()
                print(f"[OK] Termo adicionado: {new_term}")
                return True
            else:
                QMessageBox.critical(self, "Erro", "Banco de dados não conectado.")
                return False
                
        except Exception as e:
            print(f"[ERRO] Falha ao adicionar termo: {e}")
            QMessageBox.critical(self, "Erro", f"Falha ao adicionar termo:\n{e}")
            return False
    
    def remove_search_term(self, term_id):
        """Remove um termo de busca do banco de dados e atualiza a UI."""
        try:
            if self.db:
                success = self.db.delete_affiliation_variation(term_id)
                if success:
                    self.populate_search_terms()
                    print(f"[OK] Termo removido (ID: {term_id})")
                    return True
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível remover o termo.")
                    return False
            else:
                QMessageBox.critical(self, "Erro", "Banco de dados não conectado.")
                return False
        except Exception as e:
            print(f"[ERRO] Falha ao remover termo: {e}")
            QMessageBox.critical(self, "Erro", f"Falha ao remover termo:\n{e}")
            return False
    
    def update_search_term(self, term_id, new_term):
        """Atualiza um termo de busca no banco de dados."""
        try:
            if self.db:
                # Lê a variação existente
                variation = self.db.read_affiliation_variation(term_id)
                if not variation:
                    QMessageBox.warning(self, "Erro", "Termo não encontrado.")
                    return False
                
                # Verifica se o novo termo já existe
                variations = self.db.read_affiliation_variations_by_institution("HC-UFPE")
                existing_terms = [v.original_text for v in variations if v.id != term_id]
                
                if new_term in existing_terms:
                    QMessageBox.information(self, "Duplicado", f"O termo '{new_term}' já existe.")
                    return False
                
                # Atualiza o termo
                variation.original_text = new_term
                variation.normalized_text = new_term
                
                success = self.db.update_affiliation_variation(variation)
                if success:
                    self.populate_search_terms()
                    print(f"[OK] Termo atualizado: '{new_term}'")
                    return True
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível atualizar o termo.")
                    return False
            else:
                QMessageBox.critical(self, "Erro", "Banco de dados não conectado.")
                return False
        except Exception as e:
            print(f"[ERRO] Falha ao atualizar termo: {e}")
            QMessageBox.critical(self, "Erro", f"Falha ao atualizar termo:\n{e}")
            return False

    def _save_config(self):
        """
        Salva a configuração atual (datas e plataformas) e aplica na tela principal.
        Garante que a data seja salva como string (dd/MM/yyyy).
        """
        try:
            # Coleta a data do QDateEdit e salva como string formatada
            self.current_config['date_start'] = self.date_start_input.date().toString("dd/MM/yyyy")
            self.current_config['date_end'] = self.date_end_input.date().toString("dd/MM/yyyy")

            print("[OK] Configuracao salva:")
            print(f"  Datas: {self.current_config['date_start']} a {self.current_config['date_end']}")
            print(f"  Plataformas: {self.current_config['platforms']}")

            # Se houver uma janela principal, atualiza seus filtros
            if self.parent_window and hasattr(self.parent_window, 'apply_default_config'):
                self.parent_window.apply_default_config(self.current_config)
                
            QMessageBox.information(self, "Sucesso", "Configuração salva com sucesso!")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar configuração: {e}")
            QMessageBox.critical(self, "Erro", f"Falha ao salvar configuração:\n{e}")
            
    def return_to_search(self):
        """Fecha esta janela e exibe a janela pai (SearchWindow)."""
        self._save_config()  # Garante que as mudanças sejam salvas ao voltar
        self.close()
        if self.parent_window:
            self.parent_window.show()

    def closeEvent(self, event):
        """Fecha a conexão com o BD quando a janela é fechada."""
        try:
            if self.db:
                self.db.close()
        except Exception as e:
            print(f"[AVISO] Erro ao fechar conexao com BD: {e}")
        event.accept()
            
    # --- MÉTODOS EXTERNOS DE INTERFACE (Setters para a SearchWindow chamar) ---
    
    def set_start_date(self, date_obj):
        """Define a data de início do QDateEdit da ConfigWindow."""
        if date_obj and isinstance(date_obj, QDate):
            self.date_start_input.setDate(date_obj)

    def set_end_date(self, date_obj):
        """Define a data final do QDateEdit da ConfigWindow."""
        if date_obj and isinstance(date_obj, QDate):
            self.date_end_input.setDate(date_obj)