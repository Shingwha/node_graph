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
