# Version 1.1: Inicialização corrigida para QWebEngine

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, Qt
from ui.main_window import MainWindow

# Defina o atributo Qt::AA_ShareOpenGLContexts antes de criar a instância do QGuiApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())
