# Version 1.2: Ajustar métodos de carregamento de cache e criação de nova janela

import os
import json
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QTabBar
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QColor
from .instance_manager import InstanceManager
from .browser import InstanceTab
from utils.persistence import load_cache, save_cache

CACHE_DIR = 'data/cache'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instance Manager")
        self.setGeometry(300, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        self.instance_manager_tab = InstanceManager(self)
        self.tab_widget.addTab(self.instance_manager_tab, "Manage Instances")
        self.tab_widget.tabBar().setTabButton(0, QTabBar.RightSide, None)

        self.load_cache()

    def load_cache(self):
        cache_data = load_cache(CACHE_DIR)
        for prefix, data in cache_data.items():
            self.add_instance_tab_from_cache(prefix, data)

    def add_instance_tab_from_cache(self, prefix, data):
        urls = data.get("urls", [])
        color = data.get("color", "#ffffff")
        new_instance_tab = InstanceTab(prefix, self, color)
        for url in urls:
            new_instance_tab.add_new_browser_tab(QUrl(url))
        self.tab_widget.addTab(new_instance_tab, prefix)
        self.tab_widget.setCurrentWidget(new_instance_tab)
        self.update_instance_tab_color(prefix, color)

    def add_instance_tab(self, prefix, color):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == prefix:
                self.tab_widget.setCurrentIndex(i)
                return
        new_instance_tab = InstanceTab(prefix, self, color)
        self.tab_widget.addTab(new_instance_tab, prefix)
        self.tab_widget.setCurrentWidget(new_instance_tab)
        self.update_instance_tab_color(prefix, color)

    def update_instance_tab_color(self, prefix, color):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == prefix:
                tab_bar = self.tab_widget.tabBar()
                tab_bar.setTabTextColor(i, QColor(color))

    def remove_instance_tab(self, prefix):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == prefix:
                self.tab_widget.removeTab(i)
                break

        cache_file = os.path.join(CACHE_DIR, f"{prefix}.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)

    def close_tab(self, index):
        if index != 0:  # Prevent closing the "Manage Instances" tab
            widget = self.tab_widget.widget(index)
            if widget is not None:
                self.tab_widget.removeTab(index)
                widget.deleteLater()

    def create_new_tab(self, url=None):
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, InstanceTab):
            current_widget.add_new_browser_tab(url)

    def closeEvent(self, event):
        cache_data = {}
        for i in range(1, self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if isinstance(tab, InstanceTab):
                urls = [browser.url().toString() for browser in tab.browsers]
                cache_data[tab.prefix] = {
                    "color": tab.color,
                    "urls": urls
                }
        save_cache(cache_data)
        event.accept()

    def load_instances(self):
        cache_data = load_cache(CACHE_DIR)
        return {prefix: data.get("color", "#ffffff") for prefix, data in cache_data.items()}

    def save_instances(self, instances):
        cache_data = {prefix: {"color": color, "urls": []} for prefix, color in instances.items()}
        save_cache(cache_data)
