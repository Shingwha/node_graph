from box import Box
from PySide6.QtWidgets import QLineEdit,QGraphicsProxyWidget
from PySide6.QtGui import QRegularExpressionValidator
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
class ImageBox(Box):
    def __init__(self, socket):
        super().__init__(socket=socket, height = self.width)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def update_display(self):
        pass

    def get_value(self):
        return None
