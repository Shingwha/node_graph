# main_window.py
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QAction
from scene import Scene
from view import View
from edge import Edge

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Node Editor")
        self.setGeometry(100, 100, 800, 600)
        # 创建中央widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # 创建布局
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建scene
        self.scene = Scene(self)
        # 创建view
        self.view = View(self.scene)
        self.layout.addWidget(self.view)
        self.show()
