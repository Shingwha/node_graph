# main_window.py
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtGui import QUndoStack, QAction
from scene import Scene
from node_factory import NodeFactory
from view import View
from edge import Edge
from scene_serializer import save_scene_to_file, load_scene_from_file

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.undo_stack = QUndoStack(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Node Editor")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建菜单栏
        self.create_menus()
        
        # 创建中央widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # 创建布局
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建node factory
        self.node_factory = NodeFactory()
        # 创建scene
        self.scene = Scene(self, self.node_factory)
        # 创建view
        self.view = View(self.scene, self.undo_stack)
        self.layout.addWidget(self.view)
        self.show()

    def create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 导入
        import_action = QAction('导入', self)
        import_action.triggered.connect(self.import_scene)
        file_menu.addAction(import_action)
        
        # 导出
        export_action = QAction('导出', self)
        export_action.triggered.connect(self.export_scene)
        file_menu.addAction(export_action)

        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        undo_action = QAction('撤销', self)
        undo_action.triggered.connect(self.undo_stack.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('重做', self)
        redo_action.triggered.connect(self.undo_stack.redo)
        edit_menu.addAction(redo_action)

    def import_scene(self):
        """导入场景"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            "导入场景", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        if filepath:
            self.scene.clear()
            load_scene_from_file(self.scene, filepath)

    def export_scene(self):
        """导出场景"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "导出场景",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filepath:
            save_scene_to_file(self.scene, filepath)
