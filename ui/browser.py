# Version 1.3: Adicionar mensagens de depuração e verificar permissões de pop-up

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QTabWidget, QMainWindow
from PyQt5.QtCore import QUrl, Qt, pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineProfile

class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.urlChanged.connect(self.on_url_changed)
        self.titleChanged.connect(self.on_title_changed)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.page().profile().setHttpAcceptLanguage("en-US,en;q=0.9")
        self.page().profile().setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
        print("CustomWebEngineView initialized with pop-up settings enabled.")

    def createWindow(self, _type):
        print(f"createWindow called with type: {_type}")
        if _type == QWebEnginePage.WebBrowserTab or _type == QWebEnginePage.WebBrowserBackgroundTab:
            return self.parent().create_new_tab_view()
        elif _type == QWebEnginePage.WebBrowserWindow:
            return self.parent().create_new_window()
        return super().createWindow(_type)

    @pyqtSlot(QUrl)
    def on_url_changed(self, url):
        self.parent().update_url_bar(url)
        print(f"URL changed to: {url.toString()}")

    @pyqtSlot(str)
    def on_title_changed(self, title):
        self.parent().update_tab_title(title)
        print(f"Title changed to: {title}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier):
            url = self.page().url()
            print(f"Opening URL in new tab: {url.toString()}")
            self.parent().parent().create_new_tab(url)
        else:
            super().mousePressEvent(event)

class Browser(QWidget):
    def __init__(self, prefix, parent, url=None):
        super().__init__(parent)
        self.prefix = prefix
        self.parent_tab = parent

        self.layout = QVBoxLayout(self)

        self.url_bar_layout = QHBoxLayout()

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.url_bar_layout.addWidget(self.back_button)

        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.go_forward)
        self.url_bar_layout.addWidget(self.forward_button)

        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(self.go_home)
        self.url_bar_layout.addWidget(self.home_button)

        self.url_label = QLineEdit()
        self.url_label.setReadOnly(True)
        self.url_bar_layout.addWidget(self.url_label)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_page)
        self.url_bar_layout.addWidget(self.refresh_button)

        self.layout.addLayout(self.url_bar_layout)

        self.browser = CustomWebEngineView(self)
        self.layout.addWidget(self.browser)

        self.load_url(url)

    def load_url(self, url=None):
        prefix = self.prefix.strip()
        if not prefix:
            QMessageBox.warning(self, "Error", "Please enter a prefix.")
            return

        base_url = ".service-now.com"
        if url is None:
            full_url = f"https://{prefix}{base_url}"
        else:
            full_url = url.toString()
        self.url_label.setText(full_url)
        self.browser.setUrl(QUrl(full_url))
        print(f"Loading URL: {full_url}")

    def refresh_page(self):
        self.browser.reload()
        print("Page refreshed.")

    def go_back(self):
        self.browser.back()
        print("Navigating back.")

    def go_forward(self):
        self.browser.forward()
        print("Navigating forward.")

    def go_home(self):
        self.load_url()
        print("Navigating home.")

    def update_url_bar(self, url):
        self.url_label.setText(url.toString())
        print(f"URL bar updated to: {url.toString()}")

    def update_tab_title(self, title):
        index = self.parent_tab.tab_widget.indexOf(self)
        if index != -1:
            self.parent_tab.tab_widget.setTabText(index, title)
        print(f"Tab title updated to: {title}")

    def create_new_tab_view(self):
        return self.parent_tab.create_new_tab()

    def create_new_window(self):
        new_browser = Browser(self.prefix, self.parent_tab)
        new_window = QMainWindow()
        new_window.setCentralWidget(new_browser)
        new_window.show()
        print("New window created.")
        return new_browser.browser

class InstanceTab(QWidget):
    def __init__(self, prefix, parent, color):
        super().__init__(parent)
        self.prefix = prefix
        self.color = color
        self.parent = parent

        self.layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.layout.addWidget(self.tab_widget)

        self.add_new_browser_tab()

    def add_new_browser_tab(self, url=None):
        new_browser = Browser(self.prefix, self, url)
        self.tab_widget.addTab(new_browser, "New Tab")
        self.tab_widget.setCurrentWidget(new_browser)
        print("New browser tab added.")

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            if widget is not None:
                self.tab_widget.removeTab(index)
                widget.deleteLater()
        else:
            self.parent.remove_instance_tab(self.prefix)
        print("Tab closed.")

    def create_new_tab(self, url=None):
        new_browser = Browser(self.prefix, self, url)
        self.tab_widget.addTab(new_browser, "New Tab")
        self.tab_widget.setCurrentWidget(new_browser)
        print("New tab created.")
        return new_browser.browser

    def update_tab_color(self):
        for i in range(self.tab_widget.count()):
            tab_bar = self.tab_widget.tabBar()
            tab_bar.setTabTextColor(i, QColor(self.color))
        print(f"Tab color updated to: {self.color}")
