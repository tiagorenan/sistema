from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem,
    QGridLayout, QLineEdit, QDateEdit, QMessageBox
)
from PySide6.QtGui import QFont, QCursor, QPixmap
from PySide6.QtCore import Qt, Signal, QDate, QRect
import sys 
from datetime import datetime # ESSENCIAL: Para parsear o formato de data do DB

# Adicionamos a importação da nova janela
from Interface.historico_artigos_window import HistoricoArtigosWindow 
from database.db_manager import DatabaseManager
from database.models import Article # Necessário para tipagem ou referência

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"

# ====================================================================
# DADOS SIMULADOS REMOVIDOS PARA USO APENAS DO BANCO DE DADOS
# ====================================================================

# --- Widget Customizado para o Item de Histórico Expansível ---

class HistoryListItem(QFrame):
    """Representa um registro de consulta bem-sucedida que se expande."""
    
    item_clicked = Signal(int)

    def __init__(self, entry_data, history_window_instance, parent=None): 
        super().__init__(parent)
        self.entry_data = entry_data
        self.history_window = history_window_instance 
        self.is_expanded = False
        self.entry_id = entry_data["id"]
        
        self.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; margin-bottom: 5px; background-color: white;")
        
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
        
    # Dentro da classe HistoryListItem

    def _setup_header_row(self):
        """Cria a linha que mostra o Termo de Busca, Data e o número de artigos (Layout Estável)."""
        header_widget = QWidget()
        header_hbox = QHBoxLayout(header_widget)
        header_hbox.setContentsMargins(10, 8, 10, 8)
        
        # 1. Termo de Busca (Título Principal) - Ganha mais espaço
        title_label = QLabel(f'<b>Consulta:</b> {self.entry_data.get("termo", "N/A")}')
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.setFont(QFont("Arial", 10))
        title_label.setWordWrap(True)
        header_hbox.addWidget(title_label, 1) # Prioridade 1 para absorver o espaço
        
        # 2. Data da Pesquisa (Largura Fixa - 120px)
        date_q = self.entry_data.get("data_pesquisa")
        date_str = date_q.toString('yyyy-MM-dd') if isinstance(date_q, QDate) else self.entry_data.get("data_pesquisa", "N/A")
        date_label = self._create_label(f'Data: {date_str}')
        date_label.setFixedWidth(120)
        header_hbox.addWidget(date_label)
        
        # 3. Qtd de Artigos (Largura AJUSTÁVEL ao Conteúdo - MANTENHA A LINHA REMOVIDA)
        count_label = self._create_label(f'Artigos: <b>{self.entry_data.get("artigos_encontrados", 0)}</b>')
        # count_label.setFixedWidth(80) # <--- LINHA REMOVIDA para permitir ajuste automático
        
        # Define uma dica de tamanho mínimo (Se necessário, para evitar colapso total)
        count_label.setMinimumWidth(70) 
        header_hbox.addWidget(count_label)
        
        # 4. Ícone de Expansão
        self.expand_icon = QLabel("▼")
        self.expand_icon.setFixedWidth(20)
        header_hbox.addWidget(self.expand_icon)
        
        self.main_layout.addWidget(header_widget)
        self.header_widget = header_widget
        
    def _setup_detail_content(self):
        """Cria o widget com os detalhes (Tabela de Parâmetros, Resumo e Botão de Ação)."""
        self.detail_widget = QFrame()
        self.detail_widget.setStyleSheet(f"background-color: {CINZA_FUNDO}; padding: 10px; border-top: 1px solid #ddd;")
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setSpacing(10)
        
        # --- Tabela de Detalhes ---
        detail_table_frame = QFrame()
        detail_table_layout = QGridLayout(detail_table_frame)
        detail_table_layout.setSpacing(5)
        
        def add_detail_row(layout, row, label_text, value_text, is_link=False):
            label = self._create_label(f'<b>{label_text}:</b>')
            label.setFixedWidth(120)
            layout.addWidget(label, row, 0, Qt.AlignTop)
            
            value = self._create_label(value_text, word_wrap=True)
            if is_link:
                value.setText(f'<a href="{value_text}" style="color: {AZUL_NEXUS};">{value_text}</a>')
                value.setOpenExternalLinks(True) 
            layout.addWidget(value, row, 1)

        row_map = [
            ("Termo Utilizado", self.entry_data.get("termo", "N/A")),
            ("Período de Busca", self.entry_data.get("periodo", "N/A")),
            ("Plataformas", self.entry_data.get("plataformas", "N/A")),
        ]
        
        for i, (label_text, value_text) in enumerate(row_map):
            add_detail_row(detail_table_layout, i, label_text, value_text)

        detail_table_layout.setColumnStretch(1, 1)
        detail_layout.addWidget(detail_table_frame)
        
        # --- Resumo de Resultados ---
        resumo_vbox = QVBoxLayout()
        resumo_vbox.setSpacing(5)
        resumo_vbox.addWidget(self._create_label("Resumo da Consulta:", bold=True, font_size=10)) 
        
        resumo_text = self._create_label(self.entry_data.get("resumo_resultado", "Busca salva no DB, clique em VISUALIZAR ARTIGOS."), word_wrap=True)
        resumo_vbox.addWidget(resumo_text)
        
        detail_layout.addLayout(resumo_vbox)

        # --- Botão Visualizar Artigos ---
        action_hbox = QHBoxLayout()
        action_hbox.addStretch(1) 

        btn_view_articles = QPushButton('VISUALIZAR ARTIGOS')
        style = f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; padding: 8px 15px; font-weight: bold; border-radius: 4px;"
        btn_view_articles.setStyleSheet(style)
        
        btn_view_articles.clicked.connect(self._view_articles)
        
        action_hbox.addWidget(btn_view_articles)
        detail_layout.addLayout(action_hbox)
        
        self.main_layout.addWidget(self.detail_widget)

    def _view_articles(self):
        """Notifica a HistoryWindow para abrir a tela de artigos específicos, carregando do DB."""
        
        db_manager = self.history_window.db_manager
        
        if db_manager and hasattr(db_manager, 'read_articles_for_search'):
            search_id = self.entry_data.get('id') 
            query_term = self.entry_data.get('termo', 'Consulta Histórica')
            
            try:
                # 1. Carregar artigos reais do DB
                articles = db_manager.read_articles_for_search(search_id)
                
                # 2. Abrir a nova janela
                self.history_window.open_articles_for_history(
                    articles or [], 
                    query_term
                )
            except Exception as e:
                QMessageBox.critical(self.history_window, "Erro de Carga", f"Falha ao carregar artigos do histórico: {e}")
                print(f"[ERRO] Falha ao carregar artigos do histórico (ID {search_id}): {e}")
        else:
            QMessageBox.critical(self.history_window, "Erro Crítico", "O DatabaseManager não está pronto ou o método read_articles_for_search está faltando.")


    # --- Lógica de Expansão (Padrão) ---
    def mousePressEvent(self, event):
        if self.header_widget.geometry().contains(event.pos()):
            self.item_clicked.emit(self.entry_id) 
            self._toggle_expansion()
        else:
            super().mousePressEvent(event)

    def _toggle_expansion(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.detail_widget.show()
            self.expand_icon.setText("▲")
        else:
            self.detail_widget.hide()
            self.expand_icon.setText("▼")

# --- Janela Principal de Histórico ---

class HistoryWindow(QMainWindow):
    """
    Janela para exibir o histórico de todas as consultas bem-sucedidas.
    """
    def __init__(self, parent=None, history_entries=None):
        super().__init__(parent)
        self.parent_search_window = parent 
        self.artigos_window = None 
        self.setWindowTitle('Nexus Pesquisa HC-UFPE - Histórico de Consultas')
        self.setGeometry(100, 100, 950, 700) 
        
        # --- INTEGRAÇÃO COM BANCO DE DADOS ---
        try:
            self.db_manager = DatabaseManager()
            print("[OK] DatabaseManager inicializado na HistoryWindow")
        except Exception as e:
            print(f"[AVISO] Erro ao inicializar DatabaseManager: {e}")
            self.db_manager = None

        # Carregar histórico do BD 
        if self.db_manager:
            try:
                self.all_history_data = self._load_history_from_database()
                if not self.all_history_data:
                    self.all_history_data = [] 
                    print("[AVISO] Nenhuma consulta de histórico carregada do BD.")
                else:
                     print(f"[OK] {len(self.all_history_data)} históricos carregados do BD")
            except Exception as e:
                print(f"[ERRO] Falha ao carregar histórico do BD: {e}. Usando lista vazia.")
                self.all_history_data = [] 
        else:
            self.all_history_data = [] 
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self._setup_header()
        self._setup_date_filter() 
        self._setup_content()
        self.populate_history_list()

    def _setup_header(self):
        header_hbox = QHBoxLayout()
        back_button = QPushButton('←')
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet(f"background-color: {AZUL_NEXUS}; color: {BRANCO_PADRAO}; border-radius: 15px; font-weight: bold;")
        back_button.clicked.connect(self.return_to_parent)
        header_hbox.addWidget(back_button, alignment=Qt.AlignLeft)
        
        self.title_label = QLabel('Histórico de Consultas Realizadas')
        font = QFont("Arial", 18)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        header_hbox.addWidget(self.title_label, 1) 
        
        # --- Logo HC-UFPE no Header ---
        hc_logo_label = QLabel()
        try:
            # Assumimos que o parent (SearchWindow) tem a função resource_path
            hc_logo_pixmap = QPixmap(self.parent_search_window.resource_path("Interface/imagens/hc_logo.png")) 
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

    def _setup_date_filter(self):
        """Configura o filtro de data para consultas."""
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 5, 0, 5) 
        
        filter_layout.addWidget(QLabel("Filtrar por Data de Consulta:"))
        
        filter_layout.addWidget(QLabel("De:"))
        self.date_start_input = QDateEdit(self)
        self.date_start_input.setDisplayFormat("dd/MM/yyyy")
        self.date_start_input.setCalendarPopup(True)
        # Define a data inicial para 01/01/2000 para ser mais abrangente
        self.date_start_input.setDate(QDate(2000, 1, 1)) 
        self.date_start_input.dateChanged.connect(self.filter_history_list)
        filter_layout.addWidget(self.date_start_input)

        filter_layout.addWidget(QLabel("Até:"))
        self.date_end_input = QDateEdit(self)
        self.date_end_input.setDisplayFormat("dd/MM/yyyy")
        self.date_end_input.setCalendarPopup(True)
        self.date_end_input.setDate(QDate.currentDate())
        self.date_end_input.dateChanged.connect(self.filter_history_list)
        filter_layout.addWidget(self.date_end_input)

        filter_layout.addStretch(1)
        self.main_layout.addWidget(filter_frame)

    def _setup_content(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(f"background-color: {CINZA_FUNDO};")
        self.history_vbox = QVBoxLayout(self.content_widget)
        self.history_vbox.setSpacing(8) 
        self.history_vbox.setContentsMargins(10, 10, 10, 10)
        self.history_vbox.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area, 1) 

    def populate_history_list(self, filtered_data=None):
        """Preenche a lista visual com os registros de histórico de consultas."""
        while self.history_vbox.count():
            item = self.history_vbox.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.spacerItem() is not None:
                del item

        data_to_display = filtered_data if filtered_data is not None else self.all_history_data
        
        if not data_to_display:
            no_entries_label = QLabel("Nenhuma pesquisa bem-sucedida registrada no período.")
            no_entries_label.setAlignment(Qt.AlignCenter)
            self.history_vbox.addWidget(no_entries_label)
        else:
            for entry in sorted(data_to_display, key=lambda x: x['data_pesquisa'], reverse=True):
                item = HistoryListItem(entry, history_window_instance=self, parent=self)
                self.history_vbox.addWidget(item)

        self.history_vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _load_history_from_database(self):
        """Carrega o histórico de buscas do banco e transforma no formato esperado pela UI."""
        if not getattr(self, 'db_manager', None):
            return []

        try:
            searches = self.db_manager.read_search_history(limit=200)
            ui_entries = []
            for s in searches:
                date_q = QDate.currentDate() # Default em caso de falha de parse
                
                # --- BLOCO DE PARSE SEGURO CORRIGIDO ---
                try:
                    search_date_value = s.search_date
                    if search_date_value:
                        if isinstance(search_date_value, str):
                            # Tenta parsear o formato DD/MM/YYYY
                            dt_obj = datetime.strptime(search_date_value, '%d/%m/%Y')
                            date_q = QDate(dt_obj.year, dt_obj.month, dt_obj.day)
                        else:
                            # Assume objeto datetime
                            date_q = QDate(search_date_value.year, search_date_value.month, search_date_value.day)
                except Exception as e:
                    print(f"[AVISO] Falha ao parsear data '{s.search_date}' ({e}). Usando data atual.")
                    # Continua o loop usando a data atual, mas não quebra a função
                # --- FIM DO PARSE SEGURO ---

                ui_entries.append({
                    'id': s.id,
                    'termo': s.search_term,
                    'data_pesquisa': date_q,
                    'plataformas': s.platforms,
                    
                    # CORREÇÃO CRÍTICA AQUI: LENDO O RESULTS_COUNT CORRETO DO DB
                    'artigos_encontrados': s.results_count if s.results_count is not None else 0,
                    
                    'periodo': f"{s.date_start or ''} - {s.date_end or ''}",
                    'resumo_resultado': f"Busca salva no BD: {s.search_term}",
                    'search_id': s.id 
                })
            return ui_entries
        except Exception as e:
            # Captura o erro fatal se for uma falha de comunicação com o DB ou estrutura
            print(f"[ERRO FATAL NO DB] Falha ao carregar searches (Verifique o db_manager!): {e}")
            return []

    def filter_history_list(self):
        """Filtra a lista de histórico com base nas datas selecionadas."""
        start_date = self.date_start_input.date()
        end_date = self.date_end_input.date()

        if start_date > end_date:
            print("A data inicial não pode ser maior que a data final.")
            return

        filtered_data = [
            item for item in self.all_history_data 
            if start_date <= item['data_pesquisa'] <= end_date
        ]
        
        self.populate_history_list(filtered_data)
        
    def open_articles_for_history(self, articles, query_term):
        """Abre a HistoricoArtigosWindow (filha) com os artigos da consulta."""
        if self.artigos_window is None:
            self.artigos_window = HistoricoArtigosWindow(
                parent=self, 
                articles=articles, 
                query_term=query_term
            )
            self.artigos_window.destroyed.connect(self._reset_artigos_window)
        else:
            self.artigos_window.articles = articles
            self.artigos_window.query_term = query_term
            self.artigos_window.setWindowTitle(f'Nexus - Artigos da Consulta: {query_term}')
            self.artigos_window.populate_article_list()

        self.artigos_window.show()
        self.hide() 
        
    def _reset_artigos_window(self):
        """Reseta a referência quando a janela de artigos é fechada."""
        self.artigos_window = None

    def return_to_parent(self):
        """Fecha esta janela e exibe a janela SearchWindow (Parent)."""
        self.close()
        if self.parent_search_window:
            self.parent_search_window.show()