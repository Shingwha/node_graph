from node import Node
import logging

class SumNode(Node):
    def __init__(self):
        super().__init__(
            title="Sum",
            type=1101,  # 加法
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算所有输入值的和"""
        try:
            # 计算前统一处理None值
            for socket in self.input_sockets:
                if socket.value is None:
                    socket.value = 0
            self.output_sockets[0].value = sum(socket.value for socket in self.input_sockets)
        except ValueError as e:
            logging.error(f"SumNode calculation error: {e}")
            self.output_sockets[0].value = None

class SubtractNode(Node):
    def __init__(self):
        super().__init__(
            title="Subtract",
            type=1102,  # 减法
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算两个输入值的差"""
        try:
            # 计算前统一处理None值
            for socket in self.input_sockets:
                if socket.value is None:
                    socket.value = 0
            a = self.input_sockets[0].value
            b = self.input_sockets[1].value
            self.output_sockets[0].value = a - b
        except ValueError as e:
            logging.error(f"SubtractNode calculation error: {e}")
            self.output_sockets[0].value = None

class MultiplyNode(Node):
    def __init__(self):
        super().__init__(
            title="Multiply",
            type=1103,  # 乘法
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算两个输入值的乘积"""
        try:
            # 计算前统一处理None值
            for socket in self.input_sockets:
                if socket.value is None:
                    socket.value = 0
            a = self.input_sockets[0].value
            b = self.input_sockets[1].value
            self.output_sockets[0].value = a * b
        except ValueError as e:
            logging.error(f"MultiplyNode calculation error: {e}")
            self.output_sockets[0].value = None

class DivideNode(Node):
    def __init__(self):
        super().__init__(
            title="Divide",
            type=1104,  # 除法
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算两个输入值的商"""
        try:
            # 计算前统一处理None值
            for socket in self.input_sockets:
                if socket.value is None:
                    socket.value = 0
            a = self.input_sockets[0].value
            b = self.input_sockets[1].value
            self.output_sockets[0].value = a / b if b != 0 else None
        except ValueError as e:
            logging.error(f"DivideNode calculation error: {e}")
            self.output_sockets[0].value = None

class PowerNode(Node):
    def __init__(self):
        super().__init__(
            title="Power",
            type=1105,  # 幂运算
            input_sockets=[
                {"datatype": 0, "box_type": 1},
                {"datatype": 0, "box_type": 1}
            ],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算幂运算"""
        try:
            # 计算前统一处理None值
            for socket in self.input_sockets:
                if socket.value is None:
                    socket.value = 0
            base = self.input_sockets[0].value
            exponent = self.input_sockets[1].value
            self.output_sockets[0].value = base ** exponent
        except ValueError as e:
            logging.error(f"PowerNode calculation error: {e}")
            self.output_sockets[0].value = None

class SqrtNode(Node):
    def __init__(self):
        super().__init__(
            title="Sqrt",
            type=1106,  # 平方根
            input_sockets=[{"datatype": 0, "box_type": 1}],
            output_sockets=[{"datatype": 0}]
        )

    def run(self):
        """计算平方根"""
        try:
            # 计算前统一处理None值
            if self.input_sockets[0].value is None:
                self.input_sockets[0].value = 0
            value = self.input_sockets[0].value
            self.output_sockets[0].value = value ** 0.5 if value >= 0 else None
        except ValueError as e:
            logging.error(f"SqrtNode calculation error: {e}")
            self.output_sockets[0].value = None
