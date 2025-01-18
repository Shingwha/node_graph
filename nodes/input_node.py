from node import Node
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPixmap

class NumberInputNode(Node):
    def __init__(self):
        super().__init__(
            title="Input",
            type=1001,  # 数字输入
            input_sockets=[],
            output_sockets=[{"datatype": 0, "box_type": 1}],
        )

    def run(self):
        for socket in self.output_sockets:
            socket.value = socket.box.get_value()

class ImageInputNode(Node):
    def __init__(self):
        super().__init__(
            title="Image Input",
            type=2001,  # 图像输入
            input_sockets=[],
            output_sockets=[
                {"datatype": 1, "box_type": 2}
                ],
        )
        self.height = 110

    def run(self):
        for socket in self.output_sockets:
            socket.value = socket.box.get_value()

class TestNode(Node):
    def __init__(self):
        super().__init__(
            title="Test",
            type=1002,  # 测试输入
            input_sockets=[],
            output_sockets=[
                {"datatype": 0, "box_type": 3}
            ],
        )

    def run(self):
        for socket in self.output_sockets:
            socket.value = socket.box.get_value()
