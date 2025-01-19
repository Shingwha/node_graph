from PySide6.QtCore import QObject, QPoint
from edge import Edge

class Command(QObject):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene

    def undo(self):
        raise NotImplementedError()

    def redo(self):
        raise NotImplementedError()

class AddNodeCommand(Command):
    def __init__(self, scene, node):
        super().__init__(scene)
        self.node = node

    def undo(self):
        # 确保节点在场景中
        if self.node.scene() == self.scene:
            self.scene.removeItem(self.node)
        # 确保节点在nodes列表中
        if self.node in self.scene.nodes:
            self.scene.nodes.remove(self.node)
        self.scene.changed.emit()

    def redo(self):
        # 确保节点不在场景中
        if self.node.scene() is None:
            self.scene.addItem(self.node)
        # 确保节点不在nodes列表中
        if self.node not in self.scene.nodes:
            self.scene.nodes.append(self.node)
        self.scene.changed.emit()

class RemoveNodeCommand(Command):
    def __init__(self, scene, node):
        super().__init__(scene)
        self.node = node

    def undo(self):
        self.scene.nodes.append(self.node)
        self.scene.addItem(self.node)
        self.scene.changed.emit()

    def redo(self):
        self.scene.nodes.remove(self.node)
        self.scene.removeItem(self.node)
        self.scene.changed.emit()

class AddEdgeCommand(Command):
    def __init__(self, scene, edge):
        super().__init__(scene)
        self.edge = edge

    def undo(self):
        self.scene.edges.remove(self.edge)
        self.scene.removeItem(self.edge)
        # 断开socket连接
        self.edge.start_socket.remove_edge(self.edge)
        self.edge.end_socket.remove_edge(self.edge)
        self.scene.changed.emit()

    def redo(self):
        self.scene.edges.append(self.edge)
        self.scene.addItem(self.edge)
        # 重新连接socket
        self.edge.start_socket.add_edge(self.edge)
        self.edge.end_socket.add_edge(self.edge)
        self.scene.changed.emit()

class RemoveEdgeCommand(Command):
    def __init__(self, scene, edge):
        super().__init__(scene)
        self.edge = edge

    def undo(self):
        self.scene.edges.append(self.edge)
        self.scene.addItem(self.edge)
        # 重新连接socket
        self.edge.start_socket.add_edge(self.edge)
        self.edge.end_socket.add_edge(self.edge)
        self.scene.changed.emit()

    def redo(self):
        self.scene.edges.remove(self.edge)
        self.scene.removeItem(self.edge)
        # 断开socket连接
        self.edge.start_socket.remove_edge(self.edge)
        self.edge.end_socket.remove_edge(self.edge)
        self.scene.changed.emit()

class CopyNodesCommand(Command):
    def __init__(self, scene, nodes):
        super().__init__(scene)
        self.nodes = nodes
        self.serialized_data = None
        self.original_clipboard = None

    def undo(self):
        # 恢复原始clipboard
        self.scene.clipboard = self.original_clipboard
        self.scene.changed.emit()

    def redo(self):
        from scene_serializer import SceneSerializer
        # 保存原始clipboard
        self.original_clipboard = self.scene.clipboard
        # 只序列化选中的节点
        data = {
            "nodes": [],
            "edges": []
        }
        
        # 计算选中节点的边界矩形
        min_x = min(node.scenePos().x() for node in self.nodes)
        min_y = min(node.scenePos().y() for node in self.nodes)
        
        # 序列化选中的节点，保存相对于边界矩形左上角的偏移
        for node in self.nodes:
            node_data = {
                "type": node.type,
                "position": {
                    "x": node.scenePos().x() - min_x,  # 相对于左上角的x偏移
                    "y": node.scenePos().y() - min_y   # 相对于左上角的y偏移
                },
            }
            data["nodes"].append(node_data)
        
        # 只保留选中节点之间的连接
        for edge in self.scene.edges:
            if edge.start_socket.node in self.nodes and edge.end_socket.node in self.nodes:
                edge_data = {
                    "start_node": self.nodes.index(edge.start_socket.node),
                    "start_socket": edge.start_socket.index,
                    "end_node": self.nodes.index(edge.end_socket.node),
                    "end_socket": edge.end_socket.index
                }
                data["edges"].append(edge_data)
        
        self.serialized_data = data
        self.scene.clipboard = self.serialized_data
        self.scene.changed.emit()

class PasteNodesCommand(Command):
    def __init__(self, scene, mouse_pos):
        super().__init__(scene)
        self.mouse_pos = QPoint(*mouse_pos) if isinstance(mouse_pos, tuple) else mouse_pos
        self.pasted_nodes = []
        self.pasted_edges = []
        self.original_clipboard = None

    def undo(self):
        # 移除粘贴的边
        for edge in self.pasted_edges:
            if edge in self.scene.edges:
                self.scene.edges.remove(edge)
                self.scene.removeItem(edge)
        
        # 移除粘贴的节点
        for node in self.pasted_nodes:
            if node in self.scene.nodes:
                self.scene.nodes.remove(node)
                self.scene.removeItem(node)
        
        # 清空记录
        self.pasted_nodes.clear()
        self.pasted_edges.clear()
        self.scene.changed.emit()

    def redo(self):
        from scene_serializer import SceneSerializer
        if not self.scene.clipboard:
            return

        # 深拷贝clipboard数据
        import copy
        clipboard_data = copy.deepcopy(self.scene.clipboard)

        # 创建新节点并应用偏移量
        new_nodes = []
        for i, node_data in enumerate(clipboard_data['nodes']):
            # 创建新节点
            node = self.scene.node_factory.create_node(
                node_type=node_data['type']
            )
            # 计算相对于鼠标点击位置的位置
            # 鼠标位置作为边界矩形的左上角
            # 减去节点自身的中心偏移量
            node.setPos(
                self.mouse_pos.x() + node_data['position']['x'] - node.boundingRect().width()/2,
                self.mouse_pos.y() + node_data['position']['y'] - node.boundingRect().height()/2
            )
            self.scene.add_node(node)
            new_nodes.append(node)
            self.pasted_nodes.append(node)

        # 重建连接关系
        for edge_data in clipboard_data['edges']:
            # 获取新的节点引用
            start_node = new_nodes[edge_data['start_node']]
            end_node = new_nodes[edge_data['end_node']]
            
            # 获取对应的socket
            start_socket = start_node.output_sockets[edge_data['start_socket']]
            end_socket = end_node.input_sockets[edge_data['end_socket']]
            
            # 创建新边
            edge = Edge(start_socket, end_socket)
            self.scene.add_edge(edge)
            self.pasted_edges.append(edge)

        self.scene.changed.emit()
