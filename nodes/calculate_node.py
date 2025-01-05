from node import Node

class SumNode(Node):
    def __init__(self):
        super().__init__(
            title="Sum",
            type=3001,
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算所有输入值的和"""
        try:
            self.output_sockets[0].value = sum(
                socket.value if socket.value is not None else 0
                for socket in self.input_sockets
            )
        except ValueError:
            self.output_sockets[0].value = None

class SubtractNode(Node):
    def __init__(self):
        super().__init__(
            title="Subtract",
            type=3002,
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算两个输入值的差"""
        try:
            a = self.input_sockets[0].value if self.input_sockets[0].value is not None else 0
            b = self.input_sockets[1].value if self.input_sockets[1].value is not None else 0
            self.output_sockets[0].value = a - b
        except ValueError:
            self.output_sockets[0].value = None

class MultiplyNode(Node):
    def __init__(self):
        super().__init__(
            title="Multiply",
            type=3003,
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算两个输入值的乘积"""
        try:
            a = self.input_sockets[0].value if self.input_sockets[0].value is not None else 1
            b = self.input_sockets[1].value if self.input_sockets[1].value is not None else 1
            self.output_sockets[0].value = a * b
        except ValueError:
            self.output_sockets[0].value = None

class DivideNode(Node):
    def __init__(self):
        super().__init__(
            title="Divide",
            type=3004,
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算两个输入值的商"""
        try:
            a = self.input_sockets[0].value if self.input_sockets[0].value is not None else 0
            b = self.input_sockets[1].value if self.input_sockets[1].value is not None else 1
            self.output_sockets[0].value = a / b if b != 0 else None
        except ValueError:
            self.output_sockets[0].value = None

class PowerNode(Node):
    def __init__(self):
        super().__init__(
            title="Power",
            type=3005,
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算幂运算"""
        try:
            base = self.input_sockets[0].value if self.input_sockets[0].value is not None else 0
            exponent = self.input_sockets[1].value if self.input_sockets[1].value is not None else 1
            self.output_sockets[0].value = base ** exponent
        except ValueError:
            self.output_sockets[0].value = None

class SqrtNode(Node):
    def __init__(self):
        super().__init__(
            title="Sqrt",
            type=3006,
            input_sockets=[{"datatype": 0, "box_type": 1}],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算平方根"""
        try:
            value = self.input_sockets[0].value if self.input_sockets[0].value is not None else 0
            self.output_sockets[0].value = value ** 0.5 if value >= 0 else None
        except ValueError:
            self.output_sockets[0].value = None
