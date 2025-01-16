from nodes.input_node import NumberInputNode, ImageInputNode
from nodes.output_node import NumberOutputNode, ImageOutputNode
from nodes.calculate_node import SumNode, SubtractNode, MultiplyNode, DivideNode, PowerNode, SqrtNode
from nodes.image_processing_node import (
    GrayscaleNode,
    FlipNode,
    BrightnessNode,
    RotateNode,
    ContrastNode,
    ScaleNode,
    CropNode,
    ImageOverlayNode,
    ImageSizeNode,
    RGBSplitNode
)

class NodeFactory:
    # 分组节点类型映射
    node_types = {
        "输入节点": {
            "数字": NumberInputNode,
            "图片": ImageInputNode
        },
        "输出节点": {
            "数字": NumberOutputNode,
            "图片": ImageOutputNode
        },
        "计算节点": {
            "加法": SumNode,
            "减法": SubtractNode,
            "乘法": MultiplyNode,
            "除法": DivideNode,
            "幂运算": PowerNode,
            "平方根": SqrtNode
        },
        "图像处理": {
            "灰度化": GrayscaleNode,
            "翻转": FlipNode,
            "亮度调整": BrightnessNode,
            "旋转": RotateNode,
            "对比度调整": ContrastNode,
            "缩放": ScaleNode,
            "裁剪": CropNode,
            "图片叠加": ImageOverlayNode,
            "图片尺寸": ImageSizeNode,
            "RGB分离": RGBSplitNode
        }
    }

    @staticmethod
    def find_node_class(node_types, node_type):
        """递归查找节点类，支持带斜杠的路径格式"""
        # 如果包含斜杠，先分割路径
        if '/' in node_type:
            parts = node_type.split('/')
            current = node_types
            # 遍历路径的每一部分
            for part in parts[:-1]:
                if part in current and isinstance(current[part], dict):
                    current = current[part]
                else:
                    return None
            # 最后一部分是实际的节点类型
            node_type = parts[-1]
            return current.get(node_type) if node_type in current else None
        
        # 如果不包含斜杠，保持原有逻辑
        for name, value in node_types.items():
            if name == node_type and not isinstance(value, dict):
                return value
            elif isinstance(value, dict):
                result = NodeFactory.find_node_class(value, node_type)
                if result:
                    return result
        return None

    @staticmethod
    def create_node(node_type, **kwargs):
        node_class = NodeFactory.find_node_class(NodeFactory.node_types, node_type)
        if node_class:
            return node_class(**kwargs)
        else:
            raise ValueError(f"未知的节点类型: {node_type}")
