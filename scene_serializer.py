import json
from typing import Dict, Any
from PySide6.QtCore import QPointF
from scene import Scene
from node import Node
from edge import Edge

class SceneSerializer:
    @staticmethod
    def serialize_scene(scene: Scene) -> Dict[str, Any]:
        """将场景序列化为字典"""
        data = {
            "nodes": [],
            "edges": []
        }
        
        # 序列化节点
        for node in scene.nodes:
            node_data = {
                "type": node.type,
                "position": {
                    "x": node.scenePos().x(),
                    "y": node.scenePos().y()
                },
            }
            data["nodes"].append(node_data)
        
        # 序列化边
        for edge in scene.edges:
            edge_data = {
                "start_node": scene.nodes.index(edge.start_socket.node),
                "start_socket": edge.start_socket.index,
                "end_node": scene.nodes.index(edge.end_socket.node),
                "end_socket": edge.end_socket.index
            }
            data["edges"].append(edge_data)
            
        return data

    @staticmethod
    def deserialize_scene(scene: Scene, data: Dict[str, Any]):
        """将字典反序列化为场景"""
        # 先创建所有节点
        nodes = []
        for node_data in data["nodes"]:
            # 直接使用node_factory创建节点，socket由节点类自行创建
            node = scene.node_factory.create_node(
                node_type=node_data["type"],
            )
            node.setPos(QPointF(node_data["position"]["x"], node_data["position"]["y"]))
            scene.add_node(node)
            nodes.append(node)
        
        # 创建所有边
        for edge_data in data["edges"]:
            start_node = nodes[edge_data["start_node"]]
            end_node = nodes[edge_data["end_node"]]
            start_socket = start_node.output_sockets[edge_data["start_socket"]]
            end_socket = end_node.input_sockets[edge_data["end_socket"]]
            edge = Edge(start_socket, end_socket)
            scene.add_edge(edge)

def save_scene_to_file(scene: Scene, filepath: str):
    """将场景保存到文件"""
    data = SceneSerializer.serialize_scene(scene)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_scene_from_file(scene: Scene, filepath: str):
    """从文件加载场景"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    SceneSerializer.deserialize_scene(scene, data)
