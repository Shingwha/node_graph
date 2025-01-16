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
            output_sockets=[{"datatype": 1}]
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        # 设置输入框的placeholderText
        self.input_sockets[1].box.setPlaceholderText("0:水平, 1:垂直")

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

class BrightnessNode(Node):
    def __init__(self):
        super().__init__(
            title="Brightness",
            type=4003,
            input_sockets=[
                {"datatype": 1},  # 输入图片
                {"datatype": 0, "box_type": 1}  # 亮度调整值 (-100到100)
            ],
            output_sockets=[{"datatype": 1}]  # 输出调整后的图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        # 设置输入框的placeholderText
        self.input_sockets[1].box.setPlaceholderText("亮度, -100-100")

    def run(self):
        """调整图像亮度"""
        input_image = self.input_sockets[0].value
        brightness = self.input_sockets[1].value
        
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 将亮度值限制在-100到100之间
        brightness = max(-100, min(100, brightness))
        
        # 创建新图像并调整亮度
        result_image = QImage(input_image.size(), QImage.Format_ARGB32)
        for y in range(input_image.height()):
            for x in range(input_image.width()):
                color = QColor(input_image.pixel(x, y))
                h, s, v, a = color.getHsv()
                v = min(255, max(0, v + brightness * 2.55))  # 调整亮度
                color.setHsv(h, s, v, a)
                result_image.setPixelColor(x, y, color)
        
        self.output_sockets[0].value = result_image

class RotateNode(Node):
    def __init__(self):
        super().__init__(
            title="Rotate",
            type=4004,
            input_sockets=[
                {"datatype": 1},  # 输入图片
                {"datatype": 0, "box_type": 1}  # 旋转角度 (0-360)
            ],
            output_sockets=[{"datatype": 1}]  # 输出旋转后的图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        # 设置输入框的placeholderText
        self.input_sockets[1].box.setPlaceholderText("旋转角度 (0-360)")

    def run(self):
        """旋转图像"""
        input_image = self.input_sockets[0].value
        angle = self.input_sockets[1].value
        
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 创建变换矩阵并旋转
        transform = QTransform()
        transform.rotate(angle)
        rotated_image = input_image.transformed(transform)
        
        self.output_sockets[0].value = rotated_image

class ContrastNode(Node):
    def __init__(self):
        super().__init__(
            title="Contrast",
            type=4005,
            input_sockets=[
                {"datatype": 1},  # 输入图片
                {"datatype": 0, "box_type": 1}  # 对比度调整值 (-100到100)
            ],
            output_sockets=[{"datatype": 1}]  # 输出调整后的图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        # 设置输入框的placeholderText
        self.input_sockets[1].box.setPlaceholderText("对比度-100-100")

    def run(self):
        """调整图像对比度"""
        input_image = self.input_sockets[0].value
        contrast = self.input_sockets[1].value
        
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 将对比度值限制在-100到100之间
        contrast = max(-100, min(100, contrast))
        
        # 创建新图像并调整对比度
        result_image = QImage(input_image.size(), QImage.Format_ARGB32)
        factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
        
        for y in range(input_image.height()):
            for x in range(input_image.width()):
                color = QColor(input_image.pixel(x, y))
                r = min(255, max(0, factor * (color.red() - 128) + 128))
                g = min(255, max(0, factor * (color.green() - 128) + 128))
                b = min(255, max(0, factor * (color.blue() - 128) + 128))
                color.setRgb(r, g, b)
                result_image.setPixelColor(x, y, color)
        
        self.output_sockets[0].value = result_image

class ScaleNode(Node):
    def __init__(self):
        super().__init__(
            title="Scale",
            type=4006,
            input_sockets=[
                {"datatype": 1},  # 输入图片
                {"datatype": 0, "box_type": 1},  # 宽度比例
                {"datatype": 0, "box_type": 1}   # 高度比例
            ],
            output_sockets=[{"datatype": 1}]  # 输出缩放后的图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        # 设置输入框的placeholderText
        self.input_sockets[1].box.setPlaceholderText("宽度 0-100")
        self.input_sockets[2].box.setPlaceholderText("高度 0-100")

    def run(self):
        """缩放图像"""
        input_image = self.input_sockets[0].value
        width_scale = self.input_sockets[1].value
        height_scale = self.input_sockets[2].value
        
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 计算新尺寸
        new_width = int(input_image.width() * width_scale)
        new_height = int(input_image.height() * height_scale)
        
        # 缩放图像
        scaled_image = input_image.scaled(new_width, new_height,
                                        Qt.AspectRatioMode.IgnoreAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
        
        self.output_sockets[0].value = scaled_image

class CropNode(Node):
    def __init__(self):
        super().__init__(
            title="Crop",
            type=4007,
            input_sockets=[
                {"datatype": 1},  # 输入图片
                {"datatype": 0, "box_type": 1},  # x坐标
                {"datatype": 0, "box_type": 1},  # y坐标
                {"datatype": 0, "box_type": 1},  # 宽度
                {"datatype": 0, "box_type": 1}   # 高度
            ],
            output_sockets=[{"datatype": 1}]  # 输出裁剪后的图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        # 设置输入框的placeholderText
        self.input_sockets[1].box.setPlaceholderText("x, 0-图片宽度")
        self.input_sockets[2].box.setPlaceholderText("y, 0-图片高度")
        self.input_sockets[3].box.setPlaceholderText("宽度, 0-图片宽度")
        self.input_sockets[4].box.setPlaceholderText("高度, 0-图片高度")

    def run(self):
        """裁剪图像"""
        input_image = self.input_sockets[0].value
        x = self.input_sockets[1].value
        y = self.input_sockets[2].value
        width = self.input_sockets[3].value
        height = self.input_sockets[4].value
        
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 确保裁剪区域在图像范围内
        x = max(0, min(x, input_image.width() - 1))
        y = max(0, min(y, input_image.height() - 1))
        width = min(width, input_image.width() - x)
        height = min(height, input_image.height() - y)
        
        # 执行裁剪
        cropped_image = input_image.copy(x, y, width, height)
        self.output_sockets[0].value = cropped_image