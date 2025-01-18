from nodes.input_node import NumberInputNode, ImageInputNode, TestNode
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
    # 根据type值映射节点类
    node_type_map = {
        # 输入节点
        1001: NumberInputNode,
        2001: ImageInputNode,
        1003: TestNode,
        
        # 输出节点
        1002: NumberOutputNode,
        2002: ImageOutputNode,
        
        # 计算节点
        1101: SumNode,
        1102: SubtractNode,
        1103: MultiplyNode,
        1104: DivideNode,
        1105: PowerNode,
        1106: SqrtNode,
        
        # 图像处理节点
        2101: GrayscaleNode,
        2102: FlipNode,
        2103: BrightnessNode,
        2104: RotateNode,
        2105: ContrastNode,
        2106: ScaleNode,
        2107: CropNode,
        2108: ImageOverlayNode,
        2109: ImageSizeNode,
        2110: RGBSplitNode
    }

    @staticmethod
    def create_node(node_type, **kwargs):
        """根据node.type创建节点"""
        if node_type in NodeFactory.node_type_map:
            return NodeFactory.node_type_map[node_type](**kwargs)
        raise ValueError(f"未知的节点类型: {node_type}")

    @staticmethod
    def get_node_groups():
        """获取按类型分组的节点"""
        groups = {
            "输入节点": [],
            "输出节点": [],
            "计算节点": [],
            "图像处理节点": []
        }
        
        # 分类节点
        for type_id, node_class in NodeFactory.node_type_map.items():
            if 1100 <= type_id < 1200:
                groups["计算节点"].append((type_id, node_class))
            elif 2100 <= type_id < 2200:
                groups["图像处理节点"].append((type_id, node_class))
            # 余数为1为输入节点，2为输出节点
            elif type_id % 100 == 1:
                groups["输入节点"].append((type_id, node_class))
            elif type_id % 100 == 2:
                groups["输出节点"].append((type_id, node_class))
                
        return groups
