from PySide6.QtWidgets import (QLineEdit, QGraphicsProxyWidget, QWidget,
                              QLabel, QSlider, QFileDialog, QStyle, QStyleOptionSlider)
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
        self.height = self.socket.basic_height * 5
        self.value = None
        self.pixmap = None
        
        # 添加删除按钮
        self.delete_button = QLabel(self)
        self.delete_button.setText("×")
        self.delete_button.setStyleSheet("""
            color: white;
            font-size: 8px;
            background-color: rgba(70, 30, 30, 0.8);
            opacity: 0.8;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 2px 6px;
            
        """)
        self.delete_button.setFixedSize(14, 14)
        self.delete_button.move(self.width - self.delete_button.width(), 0)
        self.delete_button.mousePressEvent = self.delete_image
        
        self.update_display()
        self.setMouseTracking(True)

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
            self.delete_button.show()

    def get_value(self):
        return self.value if isinstance(self.value, QImage) else None
        
    def delete_image(self, event):
        self.value = None
        self.socket.value = None
        self.pixmap = None
        self.update_display()
        self.socket.node.update_display()

class SliderBox(Box, QSlider):
    def __init__(self, socket):
        super().__init__(socket=socket)
        self.setOrientation(Qt.Horizontal)
        self.setMinimum(0)
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

