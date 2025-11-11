from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem,
    QGridLayout, QLineEdit, QToolButton, QDateEdit
)
from PySide6.QtGui import QFont, QCursor, QColor
from PySide6.QtCore import Qt, Signal, QDate, QRect
import time 
from database.db_manager import DatabaseManager

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"

# --- Dados Simulados de Erros (Histórico Completo) ---
# Dados fictícios completos para visualização correta
SIMULATED_FULL_ERRORS = [
    {
        "id": 101,
        "termo_busca": "\"Clinics Hospital of Pernambuco Federal University[Affiliation]\"", 
        "titulo": "Uso de Insulina em Diabetes Tipo I (Rejeitado)", 
        "autores": "Silva, M.; Santos, J.", 
        "doi": "10.1177/03000605211048865",
        "data_log": QDate(2025, 10, 30),
        "publicacao_ano": "2023",
        "publicacao_plataforma": "PubMed",
        "link": "https://pubmed.ncbi.nlm.nih.gov/34719912/",
        "resumo": "O artigo sobre 'Uso de Insulina em Diabetes Tipo I' foi rejeitado. O sistema não encontrou afiliação válida do HC-UFPE.",
        "tipo_erro": "Rejeição de Conteúdo" 
    },
    {
        "id": 102,
        "termo_busca": "Polifarmácia idosos", 
        "titulo": "Artigo sobre Polifarmácia em Minas Gerais", 
        "autores": "Medeiros, J. P.",
        "doi": "10.1590/0104-1169.2023.v1",
        "data_log": QDate(2025, 10, 15),
        "publicacao_ano": "2024",
        "publicacao_plataforma": "Scielo",
        "link": "https://www.scielo.br/j/rsp/a/2023/v1/",
        "resumo": "Artigo rejeitado por relevância geográfica. A pesquisa foi realizada em uma instituição fora da região Nordeste.",
        "tipo_erro": "Rejeição de Conteúdo"
    },
    {
        "id": 103,
        "termo_busca": "Vacinação Covid", 
        "titulo": "Dados Históricos de Imunização (2018)",
        "autores": "Costa, L.",
        "doi": "N/A",
        "data_log": QDate(2024, 12, 10),
        "publicacao_ano": "2018",
        "publicacao_plataforma": "Lilacs",
        "link": "N/A",
        "resumo": "O artigo trata de dados de 2018. O período de busca configurado não inclui artigos tão antigos.",
        "tipo_erro": "Rejeição de Conteúdo"
    }
]

# --- Widget Customizado para a Linha de Log Expansível (LogListItem) ---

class LogListItem(QFrame):
    """Representa um item de log de erro, com layout harmonizado com a ResultsWindow."""
    
    item_clicked = Signal(int) 
    add_term_to_config = Signal(str)
    mark_as_valid = Signal(dict)

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.is_expanded = False
        self.item_id = item_data["id"]
        
        self.setStyleSheet(f"border: 1px solid #ddd; border-radius: 5px; margin-bottom: 5px; background-color: {BRANCO_PADRAO};")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_header_row()
        self._setup_detail_content()
        
        self.detail_widget.setVisible(False)
        
    def _create_label(self, text, bold=False, word_wrap=False, font_size=9):
        """Helper para criar QLabel formatada."""
        label = QLabel(text)
        font = QFont("Arial", font_size) 
        if bold:
            font.setBold(True)
        label.setFont(font)
        label.setWordWrap(word_wrap)
        return label
        
    def _setup_header_row(self):
        """
        CORRIGIDO: Mostra Título do Artigo e Autor no cabeçalho visível, 
        espelhando a ResultsWindow.
        """
        header_widget = QWidget()
        header_hbox = QHBoxLayout(header_widget)
        header_hbox.setContentsMargins(10, 8, 10, 8)
        
        # 1. Título do Artigo (Principal - Título original do artigo rejeitado)
        title_text = self.item_data.get("titulo", "Erro Desconhecido")
        title_label = QLabel(f'<b>{title_text}</b>')
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.setFont(QFont("Arial", 10))
        title_label.setWordWrap(True)
        header_hbox.addWidget(title_label, 1) 
        
        # 2. Autor (Largura Fixa - Autor do Artigo Rejeitado)
        authors_label = self._create_label(f'Autores: {self.item_data.get("autores", "N/A")}', word_wrap=True)
        authors_label.setFixedWidth(200) 
        header_hbox.addWidget(authors_label)
        
        # 3. Ícone de Expansão
        self.expand_icon = QLabel("▼")
        self.expand_icon.setFixedWidth(20)
        header_hbox.addWidget(self.expand_icon)
        
        self.main_layout.addWidget(header_widget)
        self.header_widget = header_widget

    def _setup_detail_content(self):
        """Cria o widget com os detalhes (Estrutura idêntica à ResultsWindow + Termo de Busca)."""
        
        self.detail_widget = QFrame()
        self.detail_widget.setStyleSheet(f"background-color: {CINZA_FUNDO}; padding: 10px; border-top: 1px solid #ccc;")
        detail_layout = QGridLayout(self.detail_widget) 
        detail_layout.setSpacing(5)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        
        def add_detail_row(layout, row, label_text, value_text, is_link=False):
            label = self._create_label(f'<b>{label_text}:</b>')
            label.setFixedWidth(120)
            layout.addWidget(label, row, 0, Qt.AlignTop)
            
            value = self._create_label(value_text, word_wrap=True)
            if is_link:
                value.setText(f'<a href="{value_text}" style="color: {AZUL_NEXUS};">{value_text}</a>')
                value.setOpenExternalLinks(True) 
            layout.addWidget(value, row, 1)
        
        current_row = 0
        
        # 1. CAMPO EXTRA SOLICITADO: Termo de Busca
        add_detail_row(detail_layout, current_row, "Termo de Busca", self.item_data.get("termo_busca", "N/A"))
        current_row += 1
        
        # 2. ID DOI
        add_detail_row(detail_layout, current_row, "ID DOI", self.item_data.get("doi", "N/A"))
        current_row += 1
        
        # 3. Publicação (Ano + Plataforma)
        publicacao_info = f'{self.item_data.get("publicacao_ano", "N/A")} ({self.item_data.get("publicacao_plataforma", "N/A")})'
        add_detail_row(detail_layout, current_row, "Publicação", publicacao_info)
        current_row += 1
        
        # 4. Link Ref.
        add_detail_row(detail_layout, current_row, "Link", self.item_data.get("link", "N/A"), is_link=True)
        current_row += 1
        
        detail_layout.setColumnStretch(1, 1)
        
        # 5. Resumo (Ocupa a linha inteira - Merge das células)
        resumo_label = QLabel('<b>Resumo (Motivo da Rejeição):</b>')
        detail_layout.addWidget(resumo_label, current_row, 0, 1, 2, Qt.AlignTop)
        current_row += 1
        
        # O Resumo exibe a razão da rejeição
        resumo_text = QLabel(self.item_data.get("resumo", "Motivo: Artigo não relacionado ao HC-UFPE (Rejeição de Conteúdo)."))
        resumo_text.setWordWrap(True)
        detail_layout.addWidget(resumo_text, current_row, 0, 1, 2)
        current_row += 1
        
        # Data de Ocorrência (Rodapé)
        data_ocorrencia_str = self.item_data.get("data_log").toString("yyyy-MM-dd") if isinstance(self.item_data.get("data_log"), QDate) else "N/A"
        data_pesquisa_label = QLabel(f'<i>Data de Ocorrência: {data_ocorrencia_str} (Simulado)</i>')
        data_pesquisa_label.setFont(QFont("Arial", 8))
        detail_layout.addWidget(data_pesquisa_label, current_row, 0, 1, 2, Qt.AlignRight)
        current_row += 1
        
        self.main_layout.addWidget(self.detail_widget) 

        # --- Ações/Botões (Usando cores padrão) ---
        actions_hbox = QHBoxLayout()
        
        btn_add_term = QPushButton('ACRESCENTAR TERMO DE BUSCA')
        style_term = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 4px;"
        btn_add_term.setStyleSheet(style_term)
        btn_add_term.clicked.connect(lambda: self.add_term_to_config.emit(self.item_data.get("termo_busca", "")))
        actions_hbox.addWidget(btn_add_term, alignment=Qt.AlignLeft)

        btn_mark_valid = QPushButton('CONSIDERAR ARTIGO COMO CERTO')
        style_valid = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 4px;"
        btn_mark_valid.setStyleSheet(style_valid)
        btn_mark_valid.clicked.connect(lambda: self.mark_as_valid.emit(self.item_data))
        actions_hbox.addWidget(btn_mark_valid, alignment=Qt.AlignRight)

        self.main_layout.addLayout(actions_hbox) 

    def mousePressEvent(self, event):
        """Sobrescreve o evento de clique para expandir/colapsar."""
        if self.header_widget.geometry().contains(event.pos()):
            self.item_clicked.emit(self.item_id) 
            self._toggle_expansion()
        else:
            super().mousePressEvent(event)

    def _handle_item_clicked(self, clicked_id):
        """Recebe o sinal do clique. Colapsa se outro item foi clicado."""
        if clicked_id != self.item_id and self.is_expanded:
            self.collapse()

    def _toggle_expansion(self):
        """Alterna o estado de expansão."""
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


# --- Janela Principal de Log de Erros (Base) ---

class ErrorLogWindow(QMainWindow):
    """
    Janela usada para exibir logs de erro, mantendo a estrutura de lista expansível.
    """
    def __init__(self, parent=None, errors=None):
        super().__init__(parent)
        self.parent_search_window = parent 
        self.setWindowTitle('Nexus - Histórico de Erros de Execução')
        self.setGeometry(100, 100, 950, 700) 
        
        # --- INTEGRAÇÃO COM BANCO DE DADOS ---
        try:
            self.db_manager = DatabaseManager()
        except Exception as e:
            print(f"[AVISO] Erro ao inicializar DatabaseManager (ErrorLogWindow): {e}")
            self.db_manager = None

        if errors is not None:
            self.all_error_data = errors
        elif self.db_manager:
            try:
                db_errors = self.db_manager.read_error_logs(limit=200)
                # converter para o formato esperado pelo UI
                self.all_error_data = [
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
                    } for e in db_errors
                ]
            except Exception as ex:
                print(f"[AVISO] Erro ao carregar erros do BD: {ex}")
                self.all_error_data = SIMULATED_FULL_ERRORS
        else:
            self.all_error_data = SIMULATED_FULL_ERRORS
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.log_list_items = []

        self._setup_header()
        self._setup_date_filter() # FILTRO DE DATA
        self._setup_content()
        self.populate_error_list() # Popula a lista inicial

    def _setup_header(self):
        header_hbox = QHBoxLayout()
        
        back_button = QPushButton('←')
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet(f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; border-radius: 15px; font-weight: bold;")
        back_button.clicked.connect(self.return_to_parent)
        header_hbox.addWidget(back_button, alignment=Qt.AlignLeft)
        
        self.title_label = QLabel('Histórico de Erros e Falhas') 
        font = QFont("Arial", 18)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        header_hbox.addWidget(self.title_label, 1) 
        
        header_hbox.addItem(QSpacerItem(30, 30, QSizePolicy.Fixed, QSizePolicy.Fixed)) 

        self.main_layout.addLayout(header_hbox)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        self.main_layout.addWidget(separator)

    def _setup_date_filter(self):
        """Configura o filtro de data para logs."""
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 5, 0, 0) # Pequena margem superior
        
        filter_layout.addWidget(QLabel("Filtrar por Data de Ocorrência:"))
        
        filter_layout.addWidget(QLabel("De:"))
        self.date_start_input = QDateEdit(self)
        self.date_start_input.setDisplayFormat("dd/MM/yyyy")
        self.date_start_input.setCalendarPopup(True)
        self.date_start_input.setDate(QDate.currentDate().addYears(-1))
        self.date_start_input.dateChanged.connect(self.filter_log_list)
        filter_layout.addWidget(self.date_start_input)

        filter_layout.addWidget(QLabel("Até:"))
        self.date_end_input = QDateEdit(self)
        self.date_end_input.setDisplayFormat("dd/MM/yyyy")
        self.date_end_input.setCalendarPopup(True)
        self.date_end_input.setDate(QDate.currentDate())
        self.date_end_input.dateChanged.connect(self.filter_log_list)
        filter_layout.addWidget(self.date_end_input)

        filter_layout.addStretch(1)
        self.main_layout.addWidget(filter_frame)
        
    def _setup_content(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(f"background-color: {CINZA_FUNDO};")
        self.errors_vbox = QVBoxLayout(self.content_widget)
        self.errors_vbox.setSpacing(8) 
        self.errors_vbox.setContentsMargins(10, 10, 10, 10)
        self.errors_vbox.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area, 1) 
        
    def populate_error_list(self, filtered_data=None):
        """Popula a lista de erros, aplicando o filtro de dados, se houver."""
        
        while self.errors_vbox.count():
            item = self.errors_vbox.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.spacerItem() is not None:
                del item

        data_to_display = filtered_data if filtered_data is not None else self.all_error_data
        self.log_list_items = []
        
        if not data_to_display:
            no_errors_label = QLabel("Nenhum erro registrado neste log para o período selecionado.")
            no_errors_label.setAlignment(Qt.AlignCenter)
            self.errors_vbox.addWidget(no_errors_label)
        else:
            for error in sorted(data_to_display, key=lambda x: x['data_log'], reverse=True):
                item = LogListItem(error) 
                
                if self.parent_search_window:
                    # CONEXÃO: Se a janela pai existe, conectamos os sinais de ação
                    try:
                        item.add_term_to_config.connect(self.parent_search_window.add_search_term_from_log)
                        item.mark_as_valid.connect(self.parent_search_window.mark_article_valid_from_log)
                    except AttributeError:
                        pass

                # Gerenciamento de expansão (Colapsa outros itens)
                for existing_item in self.log_list_items:
                    item.item_clicked.connect(existing_item._handle_item_clicked)
                    item.item_clicked.connect(existing_item._handle_item_clicked) 

                self.log_list_items.append(item) 
                self.errors_vbox.addWidget(item)
        
        self.errors_vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def filter_log_list(self):
        """Filtra a lista de logs com base nas datas selecionadas."""
        start_date = self.date_start_input.date()
        end_date = self.date_end_input.date()

        if start_date > end_date:
            print("A data inicial não pode ser maior que a data final.")
            return

        # Filtramos pela data_log (que está armazenada como QDate)
        filtered_data = [
            item for item in self.all_error_data 
            if start_date <= item['data_log'] <= end_date
        ]
        
        self.populate_error_list(filtered_data)

    def return_to_parent(self):
        """Fecha esta janela e exibe a janela SearchWindow (Parent)."""
        if self.parent_search_window:
            self.parent_search_window.show()
        self.close()