from box import Box
from PySide6.QtWidgets import QLineEdit, QGraphicsProxyWidget, QWidget,QLabel
from PySide6.QtGui import QRegularExpressionValidator, QPixmap
from PySide6.QtCore import QRegularExpression,QPointF

class LineEditBox(Box, QLineEdit):
    def __init__(self, socket):
        super().__init__(socket=socket, height=16)
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
        super().__init__(socket=socket, height=100) 
        self.image = None
        self.update_display()


    def update_display(self):
        self.image = QPixmap("dog.jpg")  # 加载图片
        self.setPixmap(self.image)  # 设置图片
        self.setFixedWidth(self.width)
        self.setScaledContents(True)
        # 按照图片的高宽比来重新更新self.height
        self.height = self.width * self.image.height() / self.image.width()
        self.setFixedHeight(self.height)

    def get_value(self):
        return None
