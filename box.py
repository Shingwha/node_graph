from PySide6.QtWidgets import QLineEdit, QGraphicsProxyWidget
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression,QPointF

class Box():
    def __init__(self, socket, height=16):
        super().__init__()
        self.socket = socket
        self.value = None
        self.height = height
        self.width = self.socket.node.width * 0.84
        self.proxy = None
        self.initUI()
        
    def initUI(self):

        self.proxy = QGraphicsProxyWidget(self.socket.node)
        self.proxy.setWidget(self)
        self.setPos(self.socket.node.width/2, self.socket.pos( ).y())
        self.setFixedHeight(self.height)
        self.setFixedWidth(self.width)
        self.setStyleSheet("border: none; background-color: rgba(70, 70, 70, 0.4); color: white;")

    def setPos(self, x, y): # 使用中心点的坐标和宽度高度来设置位置
        self.proxy.setPos(x - self.width / 2, y - self.socket.node.width * 0.06)
