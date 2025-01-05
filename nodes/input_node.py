from node import Node

class InputNumberNode(Node):
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
