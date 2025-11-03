from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem,
    QGridLayout, QLineEdit, QToolButton
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, Signal
import time 

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"
VERMELHO_ERRO = "#c53929" 
VERDE_SUCESSO = "#2e7d32" 

# --- Dados Simulados de Erros (Histórico Completo) ---
SIMULATED_FULL_ERRORS = [
    {
        "id": 101,
        "termo_busca": "\"Clinics Hospital of Pernambuco Federal University[Affiliation]\"", 
        "titulo": "Clinical and laboratory profiles with suspected dengue, chikungunya and Zika virus infections",
        "autores": "Marinho, P. E. M., Gantois, I. N., de Souza, W. C. R., et al.",
        "doi": "10.1177/03000605211048865",
        "publicacao": "2024-10-30 14:00", 
        "link": "https://pubmed.ncbi.nlm.nih.gov/34719912/",
        "resumo": "A rotina de busca por 'polifarmácia idosos' excedeu o tempo limite de 30 segundos. A causa provável foi sobrecarga no servidor externo. A busca foi interrompida.",
        "data_pesquisa": "30-09-2025 (Simulado)", 
        "tipo_erro": "Timeout/Conexão" 
    },
    {
        "id": 102,
        "termo_busca": "Percepções e conhecimentos sobre o uso de medicamentos", 
        "titulo": "Percepções e conhecimentos sobre o uso de medicamentos entre pacientes idosos",
        "autores": "Silva, A. C., Santos, R. F., Medeiros, J. P.",
        "doi": "10.1590/0104-1169.1111",
        "publicacao": "2024-10-30 14:05", 
        "link": "https://www.scielo.br/j/rsp/a/2023/v1/",
        "resumo": "O artigo foi rejeitado pois nenhuma variação de afiliação do HC-UFPE foi encontrada no resumo, e o tema não é prioritário para coleta.",
        "data_pesquisa": "01-10-2025 (Simulado)",
        "tipo_erro": "Rejeição de Conteúdo"
    }
]

# --- Widget Customizado para a Linha de Log Expansível ---

class LogListItem(QFrame):
    """
    Representa um item de log de erro, replicando a aparência de item de artigo
    e adicionando botões de ação.
    """
    
    item_clicked = Signal(int) 
    add_term_to_config = Signal(str)
    mark_as_valid = Signal(dict)

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.is_expanded = False
        self.item_id = item_data["id"]
        
        self.setStyleSheet(f"border: 1px solid {VERMELHO_ERRO}; border-radius: 5px; margin-bottom: 5px; background-color: {BRANCO_PADRAO};")
        
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
        """Cria a linha de cabeçalho (Título, Autores, Ícone)."""
        header_widget = QWidget()
        header_hbox = QHBoxLayout(header_widget)
        header_hbox.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(f'<b>{self.item_data.get("titulo", "N/A")}</b>')
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.setFont(QFont("Arial", 10))
        title_label.setWordWrap(True)
        header_hbox.addWidget(title_label, 1) 
        
        authors_label = QLabel(f'Autores: {self.item_data.get("autores", "N/A")}')
        authors_label.setFixedWidth(250)
        authors_label.setFont(QFont("Arial", 9))
        authors_label.setWordWrap(True)
        header_hbox.addWidget(authors_label)
        
        self.expand_icon = QLabel("▼")
        self.expand_icon.setFixedWidth(20)
        header_hbox.addWidget(self.expand_icon)
        
        self.main_layout.addWidget(header_widget)
        self.header_widget = header_widget

    def _setup_detail_content(self):
        """Cria o widget com os detalhes (ID DOI, Publicação, Link, Resumo) + Ações."""
        self.detail_widget = QFrame()
        self.detail_widget.setStyleSheet(f"background-color: {CINZA_FUNDO}; padding: 10px; border-top: 1px solid #ddd;")
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setSpacing(10)
        
        # --- Seção de Detalhes (Tabela) ---
        detail_table_frame = QFrame()
        detail_table_layout = QGridLayout(detail_table_frame)
        detail_table_layout.setSpacing(5)
        
        label_style = "padding: 5px; border-right: 1px solid #ccc; font-weight: bold; background-color: white;"
        value_style = "padding: 5px; background-color: white; border-bottom: 1px solid #ccc;"
        
        # Campos na ordem da Imagem (com Termo de Busca no topo)
        row_map = [
            ("Termo de Busca", self.item_data.get("termo_busca", "N/A")), 
            ("ID DOI", self.item_data.get("doi", "N/A")), 
            ("Publicação", self.item_data.get("publicacao", "N/A")), 
            ("Link", self.item_data.get("link", "N/A"))
        ]

        for i, (label_text, value_text) in enumerate(row_map):
            label = self._create_label(f'<b>{label_text}:</b>')
            label.setFixedWidth(120)
            label.setStyleSheet(label_style)
            detail_table_layout.addWidget(label, i, 0, Qt.AlignTop)
            
            value = self._create_label(value_text, word_wrap=True)
            if label_text == "Link":
                value.setText(f'<a href="{value_text}" style="color: {AZUL_NEXUS};">{value_text}</a>')
                value.setOpenExternalLinks(True)
            
            value.setStyleSheet(value_style.replace("white", BRANCO_PADRAO)) 
            detail_table_layout.addWidget(value, i, 1)

        detail_table_layout.setColumnStretch(1, 1)
        detail_layout.addWidget(detail_table_frame)
        
        # --- Resumo ---
        resumo_vbox = QVBoxLayout()
        resumo_vbox.setSpacing(5)
        resumo_vbox.addWidget(self._create_label("Resumo:", bold=True, font_size=10))
        
        resumo_text = self._create_label(self.item_data.get("resumo", "Resumo não disponível."), word_wrap=True)
        resumo_vbox.addWidget(resumo_text)
        
        data_pesquisa_label = QLabel(f'<i>Data da Pesquisa: {self.item_data.get("data_pesquisa", "N/A")}</i>')
        data_pesquisa_label.setFont(QFont("Arial", 8))
        data_pesquisa_label.setAlignment(Qt.AlignRight)
        resumo_vbox.addWidget(data_pesquisa_label)

        detail_layout.addLayout(resumo_vbox)

        # --- Ações/Botões ---
        actions_hbox = QHBoxLayout()
        
        btn_add_term = QPushButton('ACRESCENTAR TERMO DE BUSCA')
        style_term = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 4px;"
        btn_add_term.setStyleSheet(style_term)
        
        # Conecta o sinal, usando o termo de busca do item como exemplo
        btn_add_term.clicked.connect(lambda: self.add_term_to_config.emit(self.item_data.get("termo_busca", self.item_data.get("autores"))))
        actions_hbox.addWidget(btn_add_term, alignment=Qt.AlignLeft)

        btn_mark_valid = QPushButton('CONSIDERAR ARTIGO COMO CERTO')
        style_valid = f"background-color: {VERDE_SUCESSO}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 4px;"
        btn_mark_valid.setStyleSheet(style_valid)
        
        btn_mark_valid.clicked.connect(lambda: self.mark_as_valid.emit(self.item_data))
        actions_hbox.addWidget(btn_mark_valid, alignment=Qt.AlignRight)

        detail_layout.addLayout(actions_hbox)
        
        self.main_layout.addWidget(self.detail_widget)

    # --- Lógica de Expansão ---
    def mousePressEvent(self, event):
        if self.header_widget.geometry().contains(event.pos()):
            self.item_clicked.emit(self.item_id) 
            self._toggle_expansion()
        else:
            super().mousePressEvent(event)

    def _handle_item_clicked(self, clicked_id):
        if clicked_id != self.item_id and self.is_expanded:
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


# --- Janela Principal de Log de Erros (Base) ---

class ErrorLogWindow(QMainWindow):
    """
    Janela usada para exibir logs de erro.
    """
    def __init__(self, parent=None, errors=None):
        super().__init__(parent)
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Registro de Erros')
        self.setGeometry(100, 100, 1100, 700) 
        
        self.parent_window = parent 
        self.errors = errors if errors is not None else SIMULATED_FULL_ERRORS
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Chamada dos métodos de setup corrigidos
        self._setup_header()
        self._setup_content()
        self._setup_footer()

        self.log_list_items = [] # Inicializa a lista de itens para gerenciamento de expansão

    # 1. MÉTODO DE SETUP DO CABEÇALHO
    def _setup_header(self):
        header_hbox = QHBoxLayout()
        
        menu_button = QPushButton('☰')
        menu_button.setFixedSize(30, 30)
        menu_button.setStyleSheet("background-color: transparent; border: none; font-size: 16px; font-weight: bold;")
        header_hbox.addWidget(menu_button, alignment=Qt.AlignLeft) 
        
        self.title_label = QLabel('Registro de Erros da Pesquisa') 
        font = QFont("Arial", 18)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        header_hbox.addWidget(self.title_label, 1) 
        
        spacer = QWidget()
        spacer.setFixedSize(30, 30)
        header_hbox.addWidget(spacer, alignment=Qt.AlignRight)

        self.main_layout.addLayout(header_hbox)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        self.main_layout.addWidget(separator)

    # 2. MÉTODO DE SETUP DO CONTEÚDO
    def _setup_content(self):
        content_frame = QWidget()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Botão de Voltar (seta azul) - Verticalmente no lado esquerdo
        back_button_vbox = QVBoxLayout()
        back_button = QPushButton('←')
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet(f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; border-radius: 15px; font-weight: bold;")
        back_button.clicked.connect(self.return_to_parent)
        back_button_vbox.addWidget(back_button, alignment=Qt.AlignTop)
        back_button_vbox.addStretch(1) 
        content_layout.addLayout(back_button_vbox)

        # Divisão principal (Lista de Erros e Painel de Estatísticas)
        main_h_content = QHBoxLayout()
        
        # Área de Rolagem para a Lista de Erros
        results_scroll_area = QScrollArea()
        results_scroll_area.setWidgetResizable(True)
        results_list_widget = QWidget()
        results_list_widget.setStyleSheet(f"background-color: {CINZA_FUNDO};")
        self.errors_vbox = QVBoxLayout(results_list_widget)
        self.errors_vbox.setSpacing(8) 
        self.errors_vbox.setContentsMargins(10, 10, 10, 10)
        
        self.populate_error_list()

        self.errors_vbox.addStretch(1) 
        results_scroll_area.setWidget(results_list_widget)
        
        main_h_content.addWidget(results_scroll_area, 3) 
        
        # Painel de Estatísticas (Apenas um no canto superior direito)
        stats_frame = self._setup_stats_panel()
        stats_vbox = QVBoxLayout()
        stats_vbox.addWidget(stats_frame, alignment=Qt.AlignTop) 
        stats_vbox.addStretch(1)

        main_h_content.addLayout(stats_vbox, 1)
        
        content_layout.addLayout(main_h_content)
        self.main_layout.addWidget(content_frame, 1) 

    # 3. MÉTODO DE SETUP DO RODAPÉ
    def _setup_footer(self):
        footer_hbox = QHBoxLayout()
        
        style_primary = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 5px;"
        style_danger = f"background-color: {VERMELHO_ERRO}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 5px;"
        
        btn_clear = QPushButton('Limpar Log')
        btn_clear.setStyleSheet(style_danger)
        btn_clear.clicked.connect(self.clear_log)
        footer_hbox.addWidget(btn_clear, alignment=Qt.AlignLeft)

        btn_export = QPushButton('Exportar para TXT')
        btn_export.setStyleSheet(style_primary)
        footer_hbox.addWidget(btn_export)

        btn_close = QPushButton('Fechar Janela')
        btn_close.setStyleSheet(style_primary)
        btn_close.clicked.connect(self.return_to_parent)
        footer_hbox.addWidget(btn_close, alignment=Qt.AlignRight)

        self.main_layout.addLayout(footer_hbox)

    # 4. MÉTODO DE SETUP DO PAINEL DE ESTATÍSTICAS
    def _setup_stats_panel(self):
        """Configura o painel de estatísticas lateral."""
        stats_frame = QFrame()
        stats_frame.setFixedWidth(250)
        stats_frame.setStyleSheet(f"background-color: {BRANCO_PADRAO}; border: 1px solid gray; padding: 10px; border-radius: 5px;")
        
        stats_layout = QGridLayout(stats_frame)
        
        title_label = QLabel('Número de Erros por Plataforma')
        font = QFont("Arial", 10)
        font.setBold(True)
        title_label.setFont(font)
        stats_layout.addWidget(title_label, 0, 0, 1, 2) 

        stats_data = {
            "Total:": len(self.errors),
            "Timeout/Conexão:": 1,
            "Rejeição Conteúdo:": 1,
            "Outro Tipo:": 0
        }
        
        row = 1
        for label, count in stats_data.items():
            stats_layout.addWidget(QLabel(label), row, 0)
            input_field = QLineEdit(str(count))
            input_field.setReadOnly(True)
            input_field.setStyleSheet(f"background-color: {CINZA_FUNDO}; border: 1px solid gray; padding: 5px;")
            stats_layout.addWidget(input_field, row, 1)
            row += 1

        stats_layout.setRowStretch(row, 1)
        return stats_frame

    # 5. MÉTODO DE POPULAR A LISTA
    def populate_error_list(self):
        while self.errors_vbox.count() > 0:
            item = self.errors_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.log_list_items = []
        
        if not self.errors:
            no_errors_label = QLabel("Nenhum erro registrado neste log.")
            no_errors_label.setAlignment(Qt.AlignCenter)
            no_errors_label.setFont(QFont("Arial", 12))
            no_errors_label.setStyleSheet("color: green; padding: 20px;")
            self.errors_vbox.addWidget(no_errors_label)
        else:
            for error in self.errors:
                # Usamos a classe LogListItem que está definida no escopo global deste arquivo.
                item = LogListItem(error) 
                
                # Conexão dos novos sinais
                if self.parent_window:
                    try:
                        item.add_term_to_config.connect(self.parent_window.add_search_term_from_log)
                        item.mark_as_valid.connect(self.parent_window.mark_article_valid_from_log)
                    except AttributeError:
                        print("Aviso: Métodos de manipulação de log na SearchWindow (parent) não encontrados. Verifique main_window.py.")

                # Gerenciamento de expansão
                for existing_item in self.log_list_items:
                    item.item_clicked.connect(existing_item._handle_item_clicked)
                    existing_item.item_clicked.connect(item._handle_item_clicked)

                self.log_list_items.append(item) 
                self.errors_vbox.addWidget(item)
    
    # 6. MÉTODOS DE FUNCIONALIDADE
    def return_to_parent(self):
        """Fecha esta janela e exibe a janela pai."""
        self.close()
        if self.parent_window:
            self.parent_window.show()
            
    def clear_log(self):
        """Limpa a lista de erros simulados e repopula a interface."""
        self.errors = [] 
        self.populate_error_list()
        
    def add_error(self, error_data):
        """Adiciona um novo erro ao log (simulação)."""
        self.errors.append(error_data)
        self.populate_error_list()