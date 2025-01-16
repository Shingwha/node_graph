from node import Node
from PySide6.QtGui import QPen, QBrush, QColor, QFont

class NumberOutputNode(Node):
    def __init__(self):
        super().__init__(
            title="Number Output",
            type=2001,
            input_sockets=[{"datatype": 0, "box_type": 1}],
            output_sockets=[]
        )

    def run(self):
        """处理输入值并显示"""
        for socket in self.input_sockets:
            value = socket.value  # 直接使用socket的值，类型已在Box中判断

class ImageOutputNode(Node):
    def __init__(self):
        super().__init__(
            title="Image Output",
            type=2002,
            input_sockets=[{"datatype": 1, "box_type": 2}],
            output_sockets=[]
        )
    
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))

    def run(self):
        """处理输入值并显示"""
        for socket in self.input_sockets:
            value = socket.value  # 直接使用socket的值，类型已在Box中判断
