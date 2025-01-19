from PySide6.QtWidgets import (QLineEdit, QGraphicsProxyWidget, QWidget,
                              QLabel, QSlider, QFileDialog, QStyle, QStyleOptionSlider, QMenu,
                              QDialog, QVBoxLayout)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QRegularExpressionValidator, QPixmap, QImage
from PySide6.QtCore import QRegularExpression,QPointF, Qt

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
        self.setStyleSheet("border: none; background-color: rgba(70, 70, 70, 0.4); color: white;")

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
        
        # 初始化右键菜单
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D30;
                color: #DCDCDC;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
            }
            QMenu::item {
                padding: 4px 8px;
            }
            QMenu::item:selected {
                background-color: #3E3E40;
                border-radius: 2px;
            }
        """)
        delete_action = self.menu.addAction("删除图片")
        delete_action.triggered.connect(self.delete_image)
        save_action = self.menu.addAction("保存图片") 
        save_action.triggered.connect(self.save_image)
        view_action = self.menu.addAction("查看大图")
        view_action.triggered.connect(self.view_large_image)
        
        self.update_display()
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def mousePressEvent(self, event):
        if self.pixmap is None:
            self.select_image()
            event.accept()
        else:
            super().mousePressEvent(event)
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
            self.setStyleSheet("border: none; background-color: rgba(70, 70, 70, 0.4); color: white;")
            self.setAlignment(Qt.AlignCenter)

    def get_value(self):
        return self.value if isinstance(self.value, QImage) else None
        
    def show_context_menu(self, pos):
        self.menu.exec_(self.mapToGlobal(pos))
        
    def delete_image(self):
        self.value = None
        self.socket.value = None
        self.pixmap = None
        self.update_display()
        self.socket.node.update_display()
        
    def view_large_image(self):
        """在新窗口中查看大图"""
        if not isinstance(self.socket.value, QImage):
            print("错误：没有可用的图片数据")
            return
            
        # 创建新窗口
        dialog = QDialog(self.socket.node.scene().views()[0])
        dialog.setWindowTitle("查看大图")
        dialog.setMinimumSize(800, 600)
        
        # 创建布局和标签
        layout = QVBoxLayout()
        image_label = QLabel(dialog)
        image_label.setPixmap(QPixmap.fromImage(self.socket.value))
        image_label.setScaledContents(True)
        
        # 设置布局
        layout.addWidget(image_label)
        dialog.setLayout(layout)
        
        # 显示对话框
        dialog.exec_()

    def save_image(self):
        """保存当前显示的图片到文件"""
        if not isinstance(self.socket.value, QImage):
            print("错误：没有可用的图片数据")
            return False
            
        # 获取保存路径
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self.socket.node.scene().views()[0],
            "保存图片",
            "",
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
        
        self.setStyleSheet("""
            QSlider {
                background: rgba(70, 70, 70, 0.4);
                height: 4px;
                border-radius: 2px;
            }
            QSlider::groove:horizontal {
                background: rgba(200, 200, 200, 0.2);
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        

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
