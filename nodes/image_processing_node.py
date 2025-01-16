from node import Node
from PySide6.QtGui import QImage, QColor, QPen, QBrush

class GrayscaleNode(Node):
    def __init__(self):
        super().__init__(
            title="Grayscale",
            type=4001,
            input_sockets=[
                {"datatype": 1}  # 输入图片
            ],
            output_sockets=[{"datatype": 1}]  # 输出灰度图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))

    def run(self):
        """将彩色图像转换为灰度图像"""
        input_image = self.input_sockets[0].value
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 转换为灰度图像
        grayscale_image = input_image.convertToFormat(QImage.Format_Grayscale8)
        self.output_sockets[0].value = grayscale_image

class FlipNode(Node):
    def __init__(self):
        super().__init__(
            title="Flip",
            type=4002,
            input_sockets=[
                {"datatype": 1},  # 输入图片
                {"datatype": 0, "box_type": 1}   # 翻转方向 (0:水平, 1:垂直)
            ],
            output_sockets=[{"datatype": 1}]  # 输出翻转后的图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))

    def run(self):
        """根据方向翻转图像"""
        input_image = self.input_sockets[0].value
        direction = self.input_sockets[1].value
        
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 根据方向进行翻转
        if direction == 0:  # 水平翻转
            flipped_image = input_image.mirrored(True, False)
        elif direction == 1:  # 垂直翻转
            flipped_image = input_image.mirrored(False, True)
        else:
            flipped_image = input_image  # 无效方向，返回原图

        self.output_sockets[0].value = flipped_image