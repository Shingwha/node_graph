from PySide6.QtWidgets import QLineEdit, QGraphicsProxyWidget, QWidget,QLabel
from PySide6.QtGui import QRegularExpressionValidator, QPixmap
from PySide6.QtCore import QRegularExpression,QPointF

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

# 添加一个图片组件
class ImageBox(Box, QLabel):
    def __init__(self, socket):
        super().__init__(socket=socket) 
        self.height = self.socket.basic_height *5 
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
