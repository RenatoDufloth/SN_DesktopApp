# Version 1.3: Adicionar mensagens de depuração e melhorar o diálogo de configuração

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QSizePolicy, QFrame, QInputDialog, QColorDialog, QDialog, QDialogButtonBox, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import os

class ConfigDialog(QDialog):
    def __init__(self, parent, prefix, color):
        super().__init__(parent)
        self.prefix = prefix
        self.color = color
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Config - {self.prefix}")

        layout = QFormLayout(self)

        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        layout.addRow("Color", self.color_button)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        layout.addRow("Cache", self.clear_cache_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_color(self):
        color = QColorDialog.getColor(QColor(self.color), self)
        if color.isValid():
            self.color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.color}")

    def clear_cache(self):
        cache_file = os.path.join('data/cache', f"{self.prefix}.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)
        self.parent().parent().remove_instance_tab(self.prefix)
        print(f"Cache cleared for prefix: {self.prefix}")

    def get_color(self):
        return self.color

class InstanceManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout(self)
        self.instances_layout = QHBoxLayout()
        self.layout.addLayout(self.instances_layout)
        self.instances_layout.setSpacing(20)  # Add spacing between instance buttons

        self.add_button = QPushButton("Add Instance\n+")
        self.add_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.add_button.setStyleSheet("""
            QPushButton {
                border: 2px dashed gray;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.add_button.setToolTip("Click to add a new instance")
        self.add_button.clicked.connect(self.add_instance)
        self.layout.addWidget(self.add_button, alignment=Qt.AlignCenter)

        self.load_instances()

    def load_instances(self):
        self.instances = self.parent.load_instances()
        for prefix, color in self.instances.items():
            self.create_instance_button(prefix, color)

    def add_instance(self):
        prefix, ok = QInputDialog.getText(self, 'Add Instance', 'Enter the instance prefix:')
        if ok and prefix:
            color = "#ffffff"
            self.create_instance_button(prefix, color)
            self.instances[prefix] = color
            self.parent.save_instances(self.instances)
            print(f"Instance added with prefix: {prefix} and color: {color}")

    def create_instance_button(self, prefix, color):
        instance_frame = QFrame()
        instance_layout = QVBoxLayout()
        instance_frame.setLayout(instance_layout)
        instance_frame.setStyleSheet(f"border: 2px solid {color}; border-radius: 10px; padding: 10px;")

        instance_button = QPushButton(prefix)
        instance_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        instance_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                padding: 20px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
        """)
        instance_button.clicked.connect(lambda: self.open_browser(prefix, color))
        instance_button.setToolTip("Click to open this instance")

        config_button = QPushButton("Config")
        config_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        config_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        config_button.clicked.connect(lambda: self.config_instance(prefix, color))
        config_button.setToolTip("Click to configure this instance")

        delete_button = QPushButton("Delete")
        delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        delete_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_instance(prefix))
        delete_button.setToolTip("Click to delete this instance")

        instance_layout.addWidget(instance_button)
        instance_layout.addWidget(config_button)
        instance_layout.addWidget(delete_button)

        self.instances_layout.addWidget(instance_frame)
        print(f"Instance button created for prefix: {prefix}")

    def open_browser(self, prefix, color):
        self.parent.add_instance_tab(prefix, color)
        print(f"Browser opened for prefix: {prefix}")

    def config_instance(self, prefix, color):
        dialog = ConfigDialog(self, prefix, color)
        if dialog.exec_() == QDialog.Accepted:
            new_color = dialog.get_color()
            self.instances[prefix] = new_color
            self.parent.save_instances(self.instances)
            self.update_instance_button(prefix, new_color)
            print(f"Instance {prefix} configured with new color: {new_color}")

    def update_instance_button(self, prefix, color):
        for i in range(self.instances_layout.count()):
            instance_frame = self.instances_layout.itemAt(i).widget()
            instance_button = instance_frame.findChild(QPushButton, prefix)
            if instance_button:
                instance_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        padding: 20px;
                        font-size: 16px;
                    }}
                    QPushButton:hover {{
                        background-color: #e0e0e0;
                    }}
                """)
                instance_frame.setStyleSheet(f"border: 2px solid {color}; border-radius: 10px; padding: 10px;")
                print(f"Instance button updated for prefix: {prefix} with color: {color}")

    def delete_instance(self, prefix):
        self.parent.remove_instance_tab(prefix)
        for i in range(self.instances_layout.count()):
            instance_frame = self.instances_layout.itemAt(i).widget()
            instance_button = instance_frame.findChild(QPushButton, prefix)
            if instance_button:
                self.instances_layout.removeWidget(instance_frame)
                instance_frame.deleteLater()
                break
        del self.instances[prefix]
        self.parent.save_instances(self.instances)
        print(f"Instance {prefix} deleted.")
