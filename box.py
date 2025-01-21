from PySide6.QtWidgets import (QLineEdit, QGraphicsProxyWidget, QWidget,
                              QLabel, QSlider, QFileDialog, QStyle, QStyleOptionSlider, QMenu,
                              QVBoxLayout, QPushButton,QDialog, QGraphicsView, QGraphicsScene, QApplication)
from PySide6.QtGui import QPainter
from PySide6.QtCore import QTimer,QEvent, QPoint,QPropertyAnimation
from PySide6.QtGui import QRegularExpressionValidator, QPixmap, QImage, QCursor, QAction
from PySide6.QtCore import QRegularExpression,QPointF, Qt
from theme import StyleSheets
class Box():
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.value = None
        self.height = self.socket.basic_height
        self.width = self.socket.node.width - self.socket.node.spacing * 2
        self.position_x = 0
        self.position_y = 0
        self.proxy = None

        
    def initUI(self):

        self.proxy = QGraphicsProxyWidget(self.socket.node)
        self.proxy.setWidget(self)
        self.update_position()
        self.setFixedHeight(self.height)
        self.setFixedWidth(self.width)
        self.setStyleSheet(StyleSheets.box())

    def update_position(self):
        self.position_x = self.socket.node.spacing
        self.position_y = self.socket.position_y - self.height / 2
        self.proxy.setPos(self.position_x, self.position_y)


class LineEditBox(Box, QLineEdit):
    def __init__(self, socket):
        super().__init__(socket=socket)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r'^-?\d*\.?\d*(?:[eE][-+]?\d+)?$')))

    def update_display(self):
        if self.socket.value is not None:
            self.setText(f"{self.socket.value:.6g}")
            self.setCursorPosition(0)  # 确保显示从开头开始
        else:
            self.clear()

    def get_value(self):
        text = self.text()
        try:
            if '.' in text:
                return float(text)
            return int(text)
        except ValueError:
            return None


# 添加一个图片组件
class ImageBox(Box, QLabel):
    def __init__(self, socket):
        super().__init__(socket=socket)
        self.height = self.socket.node.width - self.socket.node.title_height
        self.value = None
        self.pixmap = None


    def show_context_menu(self, position):
        """显示右键上下文菜单"""
        if self.pixmap is None:
            return
            
        # 使用node的view作为父级
        parent_widget = self.socket.node.scene().views()[0]
        menu = QMenu(parent_widget)
        
        # 查看大图
        view_action = QAction("查看大图", self)
        view_action.triggered.connect(self.view_large_image)
        
        # 保存图片
        save_action = QAction("保存图片", self)
        save_action.triggered.connect(self.save_image)
        
        # 删除图片
        delete_action = QAction("删除图片", self)
        delete_action.triggered.connect(self.delete_image)
        
        # 按操作顺序添加
        menu.addAction(view_action)
        menu.addAction(save_action)
        menu.addAction(delete_action)
        
        # 应用菜单样式
        menu.setStyleSheet(StyleSheets.general_menu())
        
        # 调整显示位置为全局坐标
        global_pos = self.mapToGlobal(position)
        menu.exec_(global_pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.pixmap is None:
                self.select_image()
                event.accept()
            else:
                super().mousePressEvent(event)
        else:
            event.accept() 
        if event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())
        self.socket.node.update_display()

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self.socket.node.scene().views()[0],
            "选择图片文件",
            "",
            "图片文件 (*.jpg *.png *.bmp)"
        )
        if file_name:
            self.value = QImage(file_name)
            self.socket.value = self.value
            self.update_display()

    def update_display(self):
        if self.socket.value is not None and isinstance(self.socket.value, QImage):
            self.pixmap = QPixmap.fromImage(self.socket.value)
            self.setPixmap(self.pixmap)
            self.setFixedWidth(self.width)
            self.setScaledContents(True)
            # 按照图片的高宽比来重新更新self.height
            self.height = self.width * self.socket.value.height() / self.socket.value.width()
            self.setFixedHeight(self.height)
            
        else:
            self.setText("点击选择图片")
            self.setStyleSheet(StyleSheets.image_label_placeholder())
            self.setAlignment(Qt.AlignCenter)

    def get_value(self):
        return self.value if isinstance(self.value, QImage) else None
        
    def delete_image(self):
        self.value = None
        self.socket.value = None
        self.pixmap = None
        # 设置标志位避免重复触发
        self.blockSignals(True)
        self.update_display()
        self.socket.node.update_display()
        self.blockSignals(False)
        
    def view_large_image(self):
        """优化版大图查看器：支持平滑缩放和抗锯齿渲染"""
        if not isinstance(self.socket.value, QImage):
            print("错误：没有可用的图片数据")
            return

        # 创建对话框和视图组件
        dialog = QDialog(self.socket.node.scene().views()[0])
        dialog.setWindowTitle("查看大图 (按 ESC 退出)")
        
        # 使用 QGraphicsView 实现高级渲染
        view = QGraphicsView()
        scene = QGraphicsScene()
        pixmap = QPixmap.fromImage(self.socket.value)
        pixmap_item = scene.addPixmap(pixmap)
        
        # 配置渲染参数
        view.setRenderHint(QPainter.Antialiasing)
        view.setRenderHint(QPainter.SmoothPixmapTransform)
        view.setScene(scene)
        view.setDragMode(QGraphicsView.ScrollHandDrag)  # 支持拖拽查看
        
        # 自适应初始尺寸
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        dialog.resize(min(pixmap.width(), screen_geometry.width() - 100),
                     min(pixmap.height(), screen_geometry.height() - 100))
        
        # 布局
        layout = QVBoxLayout(dialog)
        layout.addWidget(view)
        
        # 添加键盘交互 (ESC 关闭)
        dialog.keyPressEvent = lambda e: dialog.close() if e.key() == Qt.Key_Escape else None
        
        dialog.exec_()

    def save_image(self):
        """保存当前显示的图片到文件"""
        if not isinstance(self.socket.value, QImage):
            print("错误：没有可用的图片数据")
            return False
            
        # 生成默认文件名
        from datetime import datetime
        default_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 获取保存路径
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self.socket.node.scene().views()[0],
            "保存图片",
            default_name,
            "JPEG 图片 (*.jpg);;PNG 图片 (*.png);;BMP 图片 (*.bmp)"
        )
        
        if not file_name:
            print("保存操作已取消")
            return False
            
        # 根据选择的文件类型确定格式
        if selected_filter.startswith("JPEG"):
            format = "JPG"
        elif selected_filter.startswith("PNG"):
            format = "PNG"
        else:
            format = "BMP"
            
        # 保存图片
        if self.socket.value.save(file_name, format):
            print(f"图片已成功保存到：{file_name}")
            return True
        else:
            print(f"错误：无法保存图片到 {file_name}")
            return False

class SliderBox(Box, QSlider):
    def __init__(self, socket):
        super().__init__(socket=socket)
        self.setOrientation(Qt.Horizontal)
        self.setMinimum(-100)
        self.setMaximum(100)
        self.setSingleStep(1)
        self.setValue(0)
        self.valueChanged.connect(self.on_value_changed)
        

    def initUI(self):
        super().initUI()
        
        self.setStyleSheet(StyleSheets.slider())
        

    def update_display(self):
        if self.socket.value is not None:
            self.setValue(int(self.socket.value))
        else:
            self.setValue(0)
        return

    def get_value(self):
        return super().value()

    def on_value_changed(self, value):
        self.socket.value = value
