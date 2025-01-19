# main_window.py
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtGui import QAction
from scene import Scene
from node_factory import NodeFactory
from view import View
from edge import Edge
from scene_serializer import save_scene_to_file, load_scene_from_file

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
        
        # 创建node factory
        self.node_factory = NodeFactory()
        # 创建scene
        self.scene = Scene(self, self.node_factory)
        # 创建view
        self.view = View(self.scene)
        self.layout.addWidget(self.view)
        
        # 创建菜单栏
        self.create_menus()
        
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
        
        # Undo
        self.undo_action = QAction('撤销', self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.triggered.connect(self.scene.undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        # Redo
        self.redo_action = QAction('重做', self)
        self.redo_action.setShortcut('Ctrl+Y')
        self.redo_action.triggered.connect(self.scene.redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)

        # 连接场景变化信号
        self.scene.changed.connect(self.update_edit_menu)

    def update_edit_menu(self):
        """更新编辑菜单项状态"""
        self.undo_action.setEnabled(len(self.scene.undo_stack) > 0)
        self.redo_action.setEnabled(len(self.scene.redo_stack) > 0)

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
