from nodes.input_node import NumberInputNode, ImageInputNode
from nodes.output_node import NumberOutputNode, ImageOutputNode  
from nodes.calculate_node import SumNode, SubtractNode, MultiplyNode, DivideNode, PowerNode, SqrtNode

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
        }
    }

    @staticmethod
    def find_node_class(node_types, node_type):
        """递归查找节点类"""
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
