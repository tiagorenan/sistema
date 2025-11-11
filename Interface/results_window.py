import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, QMessageBox,
    QScrollArea, QSpacerItem, QSizePolicy, QButtonGroup
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, Signal, QRect, QDate # ADICIONADO QDate

# Importações de outras janelas e dados simulados (Assumindo que estão definidos ou importados em main_window)
from database.db_manager import DatabaseManager
from database.models import Article

SIMULATED_VALIDATED_ARTICLES = [
    {
        "id": 1,
        "titulo": "Clinical and laboratory profiles with suspected dengue, chikungunya and Zika virus infections",
        "autores": "Marinho, P. E. M., Gantois, I. N., de Souza, W. C. R., et al.",
        "doi": "10.1177/03000605211048865",
        "publicacao": "2022-01 (PubMed)",
        "link": "https://pubmed.ncbi.nlm.nih.gov/34719912/",
        "resumo": "O estudo objetivou analisar o perfil de utilização de antimicrobianos em um hospital universitário em Recife, Pernambuco...",
        "status": "VALIDADO" 
    },
    {
        "id": 2,
        "titulo": "Percepções e conhecimentos sobre o uso de medicamentos entre pacientes idosos",
        "autores": "Silva, A. C., Santos, R. F., Medeiros, J. P.",
        "doi": "10.1590/0104-1169.1111",
        "publicacao": "2023-05 (Scielo)",
        "link": "https://www.scielo.br/j/rsp/a/2023/v1/",
        "resumo": "Este estudo qualitativo explorou as percepções e o nível de conhecimento de pacientes idosos sobre a polifarmácia e a adesão ao tratamento...",
        "status": "VALIDADO" 
    }
]

# CORRIGIDO: Adicionado 'data_log' para compatibilidade com ErrorLogWindow
SIMULATED_SEARCH_ERRORS = [
    {
        "id": 201,
        "termo_busca": "Polifarmácia idosos",
        "titulo": "Artigo sobre Polifarmácia em Minas Gerais",
        "autores": "Medeiros, J. P.",
        "doi": "10.1590/0104-1169.2023.v1",
        "data_log": QDate.currentDate(), # Erro mais recente
        "publicacao_ano": "2024",
        "publicacao_plataforma": "Scielo",
        "link": "https://www.scielo.br/j/rsp/a/2023/v1/",
        "resumo": "Artigo rejeitado por relevância geográfica. A pesquisa foi realizada em uma instituição fora da região Nordeste.",
        "tipo_erro": "Rejeição de Conteúdo"
    },
    {
        "id": 202,
        "termo_busca": "Vacinação Covid",
        "titulo": "Dados Históricos de Imunização (2018)",
        "autores": "Costa, L.",
        "doi": "N/A",
        "data_log": QDate.currentDate().addDays(-1), # Erro um pouco mais antigo
        "publicacao_ano": "2018",
        "publicacao_plataforma": "Lilacs",
        "link": "N/A",
        "resumo": "O artigo trata de dados de 2018. O período de busca configurado não inclui artigos tão antigos.",
        "tipo_erro": "Rejeição de Conteúdo"
    }
]

# --- Definições de Cores ---
AZUL_NEXUS = "#3b5998"
CINZA_FUNDO = "#f7f7f7"
BRANCO_PADRAO = "white"
VERMELHO_ERRO = "#c53929" 

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
        """Cria a linha que mostra Título, Autores e o ícone de expansão, com larguras fixas."""
        header_widget = QWidget()
        header_hbox = QHBoxLayout(header_widget)
        header_hbox.setContentsMargins(10, 8, 10, 8)
        
        # 1. Título do Artigo (Ocupa o espaço restante)
        title_label = QLabel(f'<b>{self.article_data.get("titulo", "N/A")}</b>')
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.setFont(QFont("Arial", 10))
        title_label.setWordWrap(True)
        header_hbox.addWidget(title_label, 1) 
        
        # 2. Autores (Largura Fixa para estabilidade)
        authors_label = QLabel(f'Autores: {self.article_data.get("autores", "N/A")}')
        authors_label.setFixedWidth(200) 
        authors_label.setFont(QFont("Arial", 9))
        authors_label.setWordWrap(True)
        header_hbox.addWidget(authors_label)
        
        # 3. Ícone de Expansão (Largura Fixa Mínima)
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

        add_detail_row(detail_layout, 0, "ID DOI", self.article_data.get("doi", "N/A"))
        add_detail_row(detail_layout, 1, "Publicação", self.article_data.get("publicacao", "N/A"))
        add_detail_row(detail_layout, 2, "Link", f'<a href="{self.article_data.get("link", "#")}">{self.article_data.get("link", "N/A")}</a>')
        
        resumo_label = QLabel('<b>Resumo:</b>')
        detail_layout.addWidget(resumo_label, 3, 0, 1, 2, Qt.AlignTop)
        resumo_text = QLabel(self.article_data.get("resumo", "Resumo não disponível."))
        resumo_text.setWordWrap(True)
        detail_layout.addWidget(resumo_text, 4, 0, 1, 2)
        
        data_pesquisa_label = QLabel('<i>Data da Pesquisa: (Simulado)</i>')
        data_pesquisa_label.setFont(QFont("Arial", 8))
        data_pesquisa_label.setAlignment(Qt.AlignRight)
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
        self.articles = articles if articles is not None else SIMULATED_VALIDATED_ARTICLES
        self.current_search_errors = SIMULATED_SEARCH_ERRORS # Simulação de erros desta consulta
        self.current_log_window = None 
        
        # --- INTEGRAÇÃO COM BANCO DE DADOS ---
        try:
            self.db_manager = DatabaseManager()
            print("[OK] DatabaseManager inicializado na ResultsWindow")
        except Exception as e:
            print(f"[AVISO] Erro ao inicializar DatabaseManager: {e}")
            self.db_manager = None

        # ID da busca que originou estes resultados (vem da SearchWindow)
        self.current_search_id = parent.current_search_id if parent and hasattr(parent, 'current_search_id') else None
        
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
        
        title_label = QLabel('Resultados da Pesquisa (Apenas Validados)')
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
        self.stats_frame = QFrame()
        self.stats_frame.setFixedWidth(250)
        self.stats_frame.setStyleSheet(f"background-color: {BRANCO_PADRAO}; border: 1px solid gray; padding: 10px; border-radius: 5px;")
        self._setup_stats_panel(self.stats_frame)
        content_hbox.addWidget(self.stats_frame, 1) 

        self.main_layout.addLayout(content_hbox, 1) 

    def populate_article_list(self):
        """Popula a lista de artigos e conecta os sinais de expansão/colapso."""
        
        # Limpar layout anterior
        while self.results_vbox.count() > 0:
            item = self.results_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem() is not None:
                del item 

        self.article_list_items = []

        if not self.articles:
            no_results_label = QLabel("Nenhum artigo validado encontrado.")
            no_results_label.setAlignment(Qt.AlignCenter)
            no_results_label.setFont(QFont("Arial", 12))
            no_results_label.setStyleSheet("color: gray; padding: 20px;")
            self.results_vbox.addWidget(no_results_label)
            return

        for article in self.articles:
            item = ArticleListItem(article)
            
            for existing_item in self.article_list_items:
                item.item_clicked.connect(existing_item._handle_item_clicked)
                existing_item.item_clicked.connect(item._handle_item_clicked)
            
            self.article_list_items.append(item)
            self.results_vbox.addWidget(item)
        
        pagination_label = QLabel("<div align='center'><a href='#' style='color: #3b5998; font-weight: bold;'>1</a> <span style='color: gray;'>2 3 ...</span></div>")
        self.results_vbox.addWidget(pagination_label, alignment=Qt.AlignCenter)
        
        self.results_vbox.addStretch(1)


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
        style_red = f"background-color: {VERMELHO_ERRO}; color: {BRANCO_PADRAO}; padding: 10px 20px; font-weight: bold; border-radius: 5px;"

        btn_new_search = QPushButton('NOVA PESQUISA')
        btn_new_search.setStyleSheet(style)
        btn_new_search.clicked.connect(self.return_to_search) 
        footer_hbox.addWidget(btn_new_search, alignment=Qt.AlignLeft)
        
        btn_add = QPushButton('ADICIONAR À BASE DE DADOS')
        btn_add.setStyleSheet(style)
        btn_add.clicked.connect(self.save_articles_to_database)
        footer_hbox.addWidget(btn_add)
        
        btn_error = QPushButton(f'Registro de Erros ({len(self.current_search_errors)})')
        btn_error.setStyleSheet(style_red)
        btn_error.clicked.connect(self.open_current_error_log)
        footer_hbox.addWidget(btn_error, alignment=Qt.AlignRight)

        self.main_layout.addLayout(footer_hbox)
        
        copyright_label = QLabel('© EBSERH')
        copyright_label.setFont(QFont("Arial", 8))
        copyright_label.setAlignment(Qt.AlignRight)
        self.main_layout.addWidget(copyright_label)

    # --- Método de Ação e Navegação ---
    
    def open_current_error_log(self):
        """Abre a janela de Registro de Erros focada apenas nos erros encontrados."""
        if self.current_log_window is None:
            # Importação feita internamente para evitar ciclo
            from Interface.log_windows import ErrorLogWindow 
            self.current_log_window = ErrorLogWindow(parent=self.parent_window, errors=self.current_search_errors)
            self.current_log_window.setWindowTitle("Nexus - Registro de Erros da Consulta Atual")
            self.current_log_window.title_label.setText("Registro de Erros da Consulta Atual")
            self.current_log_window.destroyed.connect(self._reset_current_log_window)
        
        self.current_log_window.show()
        self.hide()

    def _reset_current_log_window(self):
        """Reseta a referência da janela de log quando ela é fechada."""
        self.current_log_window = None

    def return_to_search(self):
        """Fecha esta janela e exibe a janela pai (SearchWindow)."""
        self.close()
        if self.parent_window:
            self.parent_window.show()

    def save_articles_to_database(self):
        """Salva os artigos validados na tabela 'articles' do BD."""
        if not self.db_manager:
            QMessageBox.warning(self, "Erro", "Conexão com banco de dados não disponível.")
            print("[AVISO] DatabaseManager não disponível")
            return

        if not self.articles:
            QMessageBox.information(self, "Aviso", "Nenhum artigo para salvar.")
            return

        try:
            saved_count = 0
            skipped_count = 0
            for article in self.articles:
                # Extrair platform e doi
                platform = article.get("publicacao", "").split("(")[-1].rstrip(")") if "(" in article.get("publicacao", "") else "Desconhecido"
                doi = article.get("doi", "") or ""

                # Verificação de duplicata:
                # 1) se houver DOI, checar por (platform, doi)
                # 2) caso contrário, se houver URL, checar por (platform, url)
                existing = None
                try:
                    if doi:
                        existing = self.db_manager.read_article_by_platform_and_doi(platform, doi)
                    else:
                        url = article.get("link", "") or ""
                        # normalizar url básica: remover trailing spaces e barras duplicadas
                        url = url.strip()
                        if url:
                            existing = self.db_manager.read_article_by_platform_and_url(platform, url)
                except Exception as e:
                    print(f"[AVISO] Erro ao checar duplicatas: {e}")

                if existing:
                    skipped_count += 1
                    key = doi if doi else (article.get('link','') or 'N/A')
                    print(f"[AVISO] Artigo ({key}) já existe na plataforma {platform} (ID {existing.id}) — pulando inserção")
                    continue

                art_obj = Article(
                    title=article.get("titulo", "N/A"),
                    authors=article.get("autores", "N/A"),
                    doi=doi,
                    platform=platform,
                    abstract=article.get("resumo", "N/A"),
                    url=article.get("link", "N/A"),
                    status=article.get("status", "NOVO")
                )
                article_id = self.db_manager.create_article(art_obj)
                if article_id:
                    saved_count += 1
                    print(f"[OK] Artigo '{article.get('titulo')[:50]}...' salvo com ID {article_id}")

            # Mensagens para o usuário
            QMessageBox.information(self, "Sucesso", f"{saved_count} artigo(s) salvo(s). {skipped_count} duplicata(s) ignorada(s).")
            print(f"[OK] {saved_count} artigos salvos no BD; {skipped_count} duplicatas ignoradas")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar artigos: {str(e)}")
            print(f"[AVISO] Erro ao salvar artigos no BD: {e}")

    def closeEvent(self, event):
        """Fecha a conexão com o BD quando a janela é fechada."""
        if self.db_manager:
            try:
                self.db_manager.close()
                print("[OK] Conexão com BD fechada (ResultsWindow)")
            except Exception as e:
                print(f"[AVISO] Erro ao fechar BD (ResultsWindow): {e}")
        event.accept()