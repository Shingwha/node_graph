from PySide6.QtWidgets import QLineEdit, QGraphicsProxyWidget, QWidget,QLabel
from PySide6.QtGui import QRegularExpressionValidator, QPixmap
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
        # self.initUI()
        
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

from PySide6.QtWidgets import QFileDialog

# 添加一个图片组件
class ImageBox(Box, QLabel):
    def __init__(self, socket):
        super().__init__(socket=socket)
        self.height = self.socket.basic_height * 5
        self.value = None
        self.pixmap = None
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
            self.value = file_name
            self.update_display()

    def update_display(self):
        if self.socket.value is not None:
            self.pixmap = QPixmap(self.socket.value)
            self.setPixmap(self.pixmap)
            self.setFixedWidth(self.width)
            self.setScaledContents(True)
            # 按照图片的高宽比来重新更新self.height
            self.height = self.width * self.pixmap.height() / self.pixmap.width()
            self.setFixedHeight(self.height)
        else:
            self.setText("点击选择图片")
            self.setStyleSheet("border: none; background-color: rgba(70, 70, 70, 0.4); color: white;")
            self.setAlignment(Qt.AlignCenter)

    def get_value(self):
        return self.value
