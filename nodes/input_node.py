from node import Node
from PySide6.QtGui import QColor, QPen, QBrush, QFont

class NumberInputNode(Node):
    def __init__(self):
        super().__init__(
            title="Input",
            type=1001,
            input_sockets=[],
            output_sockets=[{"datatype": 0, "box_type": 1}],
        )

    def run(self):
        """将输入框的值赋给所有输出socket"""
        for socket in self.output_sockets:
            socket.value = socket.box.get_value()

class ImageInputNode(Node):
    def __init__(self):
        super().__init__(
            title="Image Input",
            type=1002,
            input_sockets=[],
            output_sockets=[
                {"datatype": 1, "box_type": 2}
                ],
        )
        self.height = 110
        # 设置线条，标题背景深一点
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))

    def run(self):
        pass
        
