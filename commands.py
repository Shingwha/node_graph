from PySide6.QtCore import QObject

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
        self.scene.nodes.remove(self.node)
        self.scene.removeItem(self.node)
        self.scene.changed.emit()

    def redo(self):
        self.scene.nodes.append(self.node)
        self.scene.addItem(self.node)
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

    def undo(self):
        # 清空clipboard
        self.scene.clipboard = None
        self.scene.changed.emit()

    def redo(self):
        from scene_serializer import SceneSerializer
        # 使用serialize_scene方法序列化选中的节点
        self.serialized_data = SceneSerializer.serialize_scene(self.scene)
        self.scene.clipboard = self.serialized_data
        self.scene.changed.emit()

class PasteNodesCommand(Command):
    def __init__(self, scene, offset=(50, 50)):
        super().__init__(scene)
        self.offset = offset
        self.pasted_nodes = []
        self.original_clipboard = None

    def undo(self):
        from scene_serializer import SceneSerializer
        # 移除粘贴的节点
        for node in self.pasted_nodes:
            self.scene.nodes.remove(node)
            self.scene.removeItem(node)
        # 恢复clipboard
        self.scene.clipboard = self.original_clipboard
        self.scene.changed.emit()

    def redo(self):
        from scene_serializer import SceneSerializer
        if not self.scene.clipboard:
            return

        # 保存原始clipboard
        self.original_clipboard = self.scene.clipboard

        # 应用偏移量
        for node_data in self.scene.clipboard['nodes']:
            node_data['position']['x'] += self.offset[0]
            node_data['position']['y'] += self.offset[1]
        
        # 使用deserialize_scene方法反序列化
        SceneSerializer.deserialize_scene(self.scene, self.scene.clipboard)
        self.scene.changed.emit()
