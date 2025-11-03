import sys
from PySide6.QtWidgets import QApplication
# Certifique-se de que o caminho de importação está correto
from Interface.main_window import SearchWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Cria e exibe a janela principal (Tela de Busca)
    main_window = SearchWindow()
    main_window.show()
    
    # Inicia o loop de eventos da aplicação
    sys.exit(app.exec())