from node import Node

class NumberOutputNode(Node):
    def __init__(self):
        super().__init__(
            title="Output",
            type=2001,
            input_sockets=[{"datatype": 0, "box_type": 1}],
            output_sockets=[]
        )

    def run(self):
        """处理输入值并显示"""
        for socket in self.input_sockets:
            value = socket.value  # 直接使用socket的值，类型已在Box中判断
