from node import Node
from PySide6.QtGui import QImage, QColor, QPen, QBrush, QPainter, QTransform
from PySide6.QtCore import Qt
import cv2
import numpy as np

def qimage_to_mat(qimg):
    """将QImage转换为OpenCV Mat"""
    qimg = qimg.convertToFormat(QImage.Format_RGB888)
    width = qimg.width()
    height = qimg.height()
    ptr = qimg.constBits()
    bytes_per_line = qimg.bytesPerLine()
    
    # 处理字节对齐问题
    if bytes_per_line == width * 3:
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape(height, width, 3)
    else:
        # 处理有填充字节的情况
        arr = np.frombuffer(ptr, dtype=np.uint8, count=bytes_per_line * height)
        arr = arr.reshape(height, bytes_per_line)
        arr = arr[:, :width * 3].reshape(height, width, 3)
    
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def mat_to_qimage(mat):
    """将OpenCV Mat转换为QImage"""
    rgb_image = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    return QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)


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

        # 使用OpenCV进行灰度转换
        mat = qimage_to_mat(input_image)
        gray_mat = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)
        grayscale_image = mat_to_qimage(gray_mat)
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

        # 使用OpenCV进行翻转
        mat = qimage_to_mat(input_image)
        if direction == 0:  # 水平翻转
            flipped_mat = cv2.flip(mat, 1)
        elif direction == 1:  # 垂直翻转
            flipped_mat = cv2.flip(mat, 0)
        else:
            flipped_mat = mat  # 无效方向，返回原图

        flipped_image = mat_to_qimage(flipped_mat)
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
        
        # 使用OpenCV调整亮度
        mat = qimage_to_mat(input_image)
        alpha = 1.0
        beta = brightness * 2.55  # 将-100到100映射到-255到255
        result_mat = cv2.convertScaleAbs(mat, alpha=alpha, beta=beta)
        
        result_image = mat_to_qimage(result_mat)
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

        # 使用OpenCV进行旋转
        mat = qimage_to_mat(input_image)
        (h, w) = mat.shape[:2]
        center = (w // 2, h // 2)
        
        # 计算旋转矩阵
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 计算新的边界尺寸
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # 调整旋转矩阵以考虑平移
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        # 执行旋转
        rotated_mat = cv2.warpAffine(mat, M, (new_w, new_h))
        
        rotated_image = mat_to_qimage(rotated_mat)
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

        # 处理contrast为None的情况
        if contrast is None:
            contrast = 0
            
        # 将对比度值限制在-100到100之间
        contrast = max(-100, min(100, contrast))
        
        # 使用OpenCV调整对比度
        mat = qimage_to_mat(input_image)
        alpha = (contrast + 100) / 100.0  # 将-100到100映射到0到2
        beta = 0
        result_mat = cv2.convertScaleAbs(mat, alpha=alpha, beta=beta)
        
        result_image = mat_to_qimage(result_mat)
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
        self.input_sockets[1].box.setPlaceholderText("宽度 0-10.0")
        self.input_sockets[2].box.setPlaceholderText("高度 0-10.0")

    def run(self):
        """缩放图像"""
        input_image = self.input_sockets[0].value
        # 获取并验证缩放比例
        width_scale = self.input_sockets[1].value or 1.0
        height_scale = self.input_sockets[2].value or 1.0
        
        # 限制缩放比例在0.1到10.0之间
        width_scale = max(0.1, min(10.0, float(width_scale)))
        height_scale = max(0.1, min(10.0, float(height_scale)))
        
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            return

        # 使用OpenCV进行缩放
        mat = qimage_to_mat(input_image)
        new_width = int(input_image.width() * width_scale)
        new_height = int(input_image.height() * height_scale)
        
        scaled_mat = cv2.resize(mat, (new_width, new_height),
                              interpolation=cv2.INTER_LINEAR)
        
        scaled_image = mat_to_qimage(scaled_mat)
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
        # 将输入值转换为整数，如果为None则使用0
        x = int(max(0, min(x or 0, input_image.width() - 1)))
        y = int(max(0, min(y or 0, input_image.height() - 1)))
        width = int(min(width or input_image.width(), input_image.width() - x))
        height = int(min(height or input_image.height(), input_image.height() - y))
        
        # 使用OpenCV进行裁剪
        mat = qimage_to_mat(input_image)
        cropped_mat = mat[y:y+height, x:x+width]
        
        cropped_image = mat_to_qimage(cropped_mat)
        self.output_sockets[0].value = cropped_image

class ImageOverlayNode(Node):
    def __init__(self):
        super().__init__(
            title="图片叠加",
            type=4008,
            input_sockets=[
                {"datatype": 1},  # 输入图片1
                {"datatype": 1},  # 输入图片2
                {"datatype": 0, "box_type": 1}  # 透明度 (0-1)
            ],
            output_sockets=[{"datatype": 1}]  # 输出叠加后的图片
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        # 设置输入框的placeholderText
        self.input_sockets[2].box.setPlaceholderText("透明度 0-1")

    def run(self):
        """将两张图片叠加"""
        image1 = self.input_sockets[0].value
        image2 = self.input_sockets[1].value
        alpha = self.input_sockets[2].value or 0.5
        
        if image1 is None or not isinstance(image1, QImage) or \
           image2 is None or not isinstance(image2, QImage):
            self.output_sockets[0].value = None
            return

        # 确保透明度在0到1之间
        alpha = max(0, min(1, alpha))
        
        # 将QImage转换为Mat
        mat1 = qimage_to_mat(image1)
        mat2 = qimage_to_mat(image2)
        
        # 调整图像尺寸
        height = max(mat1.shape[0], mat2.shape[0])
        width = max(mat1.shape[1], mat2.shape[1])
        
        # 调整图像大小
        mat1 = cv2.resize(mat1, (width, height))
        mat2 = cv2.resize(mat2, (width, height))
        
        # 使用OpenCV进行图像叠加
        result_mat = cv2.addWeighted(mat1, 1 - alpha, mat2, alpha, 0)
        
        result_image = mat_to_qimage(result_mat)
        self.output_sockets[0].value = result_image

class ImageSizeNode(Node):
    def __init__(self):
        super().__init__(
            title="图片尺寸",
            type=4009,
            input_sockets=[{"datatype": 1}],  # 输入图片
            output_sockets=[
                {"datatype": 0, "box_type": 1},  # 宽度
                {"datatype": 0, "box_type": 1}   # 高度
            ]
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))
        
    def run(self):
        input_image = self.input_sockets[0].value
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            self.output_sockets[1].value = None
            return
            
        width = input_image.width()
        height = input_image.height()
        self.output_sockets[0].value = width
        self.output_sockets[1].value = height
        self.update_display()

class RGBSplitNode(Node):
    def __init__(self):
        super().__init__(
            title="RGB分离",
            type=4010,
            input_sockets=[{"datatype": 1}],  # 输入图片
            output_sockets=[
                {"datatype": 1},  # R通道
                {"datatype": 1},  # G通道
                {"datatype": 1}   # B通道
            ]
        )
        self.pen_default = QPen(QColor("#cc6666"))
        self.brush_title = QBrush(QColor("#c36060"))

    def run(self):
        """将输入图片分离为R、G、B三个通道"""
        input_image = self.input_sockets[0].value
        if input_image is None or not isinstance(input_image, QImage):
            self.output_sockets[0].value = None
            self.output_sockets[1].value = None
            self.output_sockets[2].value = None
            return

        # 将QImage转换为OpenCV Mat
        mat = qimage_to_mat(input_image)
        
        # 分离通道
        b, g, r = cv2.split(mat)
        
        # 创建单通道图像
        zeros = np.zeros(mat.shape[:2], dtype="uint8")
        
        # 生成R通道图像
        r_img = cv2.merge([zeros, zeros, r])
        # 生成G通道图像
        g_img = cv2.merge([zeros, g, zeros])
        # 生成B通道图像
        b_img = cv2.merge([b, zeros, zeros])
        
        # 转换为QImage
        r_qimg = mat_to_qimage(r_img)
        g_qimg = mat_to_qimage(g_img)
        b_qimg = mat_to_qimage(b_img)
        
        # 设置输出
        self.output_sockets[0].value = r_qimg
        self.output_sockets[1].value = g_qimg
        self.output_sockets[2].value = b_qimg
