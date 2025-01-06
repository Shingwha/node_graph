from PySide6.QtWidgets import QLineEdit,QGraphicsProxyWidget
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression,QPointF

class LineEditBox(QLineEdit):
    def __init__(self, socket, box_type):
        super().__init__()
        self.socket = socket
        self.type = box_type
        self.value = None
        proxy = QGraphicsProxyWidget(self.socket.node)
        proxy.setWidget(self)

        # 计算输入框位置
        socket_pos = self.socket.node.get_socket_position(self.socket.index, 1)
        box_x = socket_pos[0] - self.socket.node.width + self.socket.node.socket_height / 2
        box_y = socket_pos[1] - self.socket.node.socket_height * 0.45
        proxy.setPos(box_x, box_y)

        # 设置输入框大小
        self.setFixedWidth(int(self.socket.node.width * 0.8))
        self.setFixedHeight(int(self.socket.node.socket_height * 0.9))
        self.setStyleSheet("border:none;background-color: rgba(70, 70, 70, 0.4);color:white;")

        self.setValidator(QRegularExpressionValidator(QRegularExpression(r'^-?\d*\.?\d*$')))

    def update_display(self):
        """更新显示内容"""
        if self.socket.value is not None:
            # 使用科学计数法显示，保留10位小数
            self.setText(f"{self.socket.value:.6g}")
            self.setCursorPosition(0)  # 确保显示从开头开始
        else:
            self.clear()


    
    def get_value(self):
        """获取输入框内容"""
        text = self.text()
        try:
            if '.' in text:
                return float(text)
            return int(text)
        except ValueError:
            return None
