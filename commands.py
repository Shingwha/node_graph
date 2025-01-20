from PySide6.QtCore import QPointF, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QImage,QUndoCommand
import copy
from edge import Edge

class AddNodeCommand(QUndoCommand):
    def __init__(self, scene, node_type, position, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.node_type = node_type
        self.position = position
        self.node = None

    def redo(self):
        if self.node is None:
            self.node = self.scene.node_factory.create_node(self.node_type)
            self.node.setPos(self.position)
        self.scene.add_node(self.node)

    def undo(self):
        self.scene.remove_node(self.node)

class RemoveNodeCommand(QUndoCommand):
    def __init__(self, scene, node, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.node = node
        self.edges = []
        self.node_pos = node.scenePos()  # 保存节点位置
        # 保存所有关联的边
        for socket in self.node.input_sockets + self.node.output_sockets:
            self.edges.extend(socket.edges.copy())

    def redo(self):
        # 移除节点和边
        self.scene.remove_node(self.node)
        for edge in self.edges:
            if edge in self.scene.edges:
                self.scene.remove_edge(edge)

    def undo(self):
        # 恢复节点和边
        self.node.setPos(self.node_pos)  # 恢复节点位置
        self.scene.add_node(self.node)
        for edge in self.edges:
            if edge not in self.scene.edges:
                self.scene.add_edge(edge)
                edge.update_path()

class AddEdgeCommand(QUndoCommand):
    def __init__(self, scene, start_socket, end_socket, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge = None

    def redo(self):
        if self.edge is None:
            self.edge = Edge(self.start_socket, self.end_socket)
        self.scene.add_edge(self.edge)

    def undo(self):
        self.scene.remove_edge(self.edge)

class RemoveEdgeCommand(QUndoCommand):
    def __init__(self, scene, edge, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.edge = edge
        self.start_socket = edge.start_socket
        self.end_socket = edge.end_socket

    def redo(self):
        self.scene.remove_edge(self.edge)

    def undo(self):
        # 重新连接边
        self.edge = Edge(self.start_socket, self.end_socket)
        self.scene.add_edge(self.edge)

class PasteCommand(QUndoCommand):
    def __init__(self, scene, clipboard_data, offset, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.clipboard_data = clipboard_data
        self.offset = offset
        self.added_nodes = []
        self.added_edges = []

    def redo(self):
        node_mapping = {}
        # Create nodes
        for i, node_data in enumerate(self.clipboard_data['nodes']):
            node = self.scene.node_factory.create_node(node_data['type'])
            # 应用新的偏移量计算
            pos = QPointF(
                node_data['position']['x'] + self.offset.x(),
                node_data['position']['y'] + self.offset.y()
            )
            node.setPos(pos)
            self._deserialize_node(node, node_data)
            self.scene.add_node(node)
            node_mapping[i] = node
            self.added_nodes.append(node)
        
        # Create edges
        for edge_data in self.clipboard_data['edges']:
            start_node = node_mapping[edge_data['from_node_index']]
            end_node = node_mapping[edge_data['to_node_index']]
            start_socket = start_node.output_sockets[edge_data['from_socket_index']]
            end_socket = end_node.input_sockets[edge_data['to_socket_index']]
            edge = Edge(start_socket, end_socket)
            self.scene.add_edge(edge)
            self.added_edges.append(edge)

    def undo(self):
        for edge in self.added_edges:
            self.scene.remove_edge(edge)
        for node in self.added_nodes:
            self.scene.remove_node(node)
        self.added_edges.clear()
        self.added_nodes.clear()

    def _deserialize_node(self, node, node_data):
        # Deserialize socket values
        for socket_data in node_data['sockets']:
            socket = node.input_sockets[socket_data['index']] if socket_data['type'] == 0 \
                else node.output_sockets[socket_data['index']]
                
            if socket_data['box_type'] == 1:  # LineEdit
                socket.value = socket_data.get('value', None)
                if socket.box:
                    socket.box.setText(str(socket_data['value']) if socket_data.get('value') is not None else "")
            elif socket_data['box_type'] == 2:  # ImageBox
                # 不处理图片数据，保留为None
                socket.value = None
                if socket.box:
                    socket.box.value = None
                    socket.box.update_display()
            elif socket_data['box_type'] == 3:  # Slider
                socket.value = socket_data.get('value', 0)
                if socket.box:
                    socket.box.setValue(socket_data.get('value', 0))
