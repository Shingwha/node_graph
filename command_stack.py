from typing import List, Optional

class Command:
    """命令接口"""
    def execute(self):
        raise NotImplementedError
        
    def undo(self):
        raise NotImplementedError

class CommandStack:
    """命令栈管理类"""
    def __init__(self, max_size: int = 100):
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._max_size = max_size

    def execute(self, command: Command):
        """执行新命令"""
        command.execute()
        self._undo_stack.append(command)
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> Optional[Command]:
        """撤销"""
        if not self._undo_stack:
            return None
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return command

    def redo(self) -> Optional[Command]:
        """重做"""
        if not self._redo_stack:
            return None
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return command

    def clear(self):
        """清空栈"""
        self._undo_stack.clear()
        self._redo_stack.clear()

class AddNodeCommand(Command):
    """添加节点命令"""
    def __init__(self, view, node_type, pos):
        self.view = view
        self.node_type = node_type
        self.pos = pos
        self.node = None

    def execute(self):
        if self.node is None:
            self.node = self.view.node_factory.create_node(self.node_type)
            self.node.setPos(self.pos)
            self.view.scene().add_node(self.node)
        else:
            self.view.scene().add_node(self.node)

    def undo(self):
        if self.node:
            self.view.scene().remove_node(self.node)

class DeleteNodeCommand(Command):
    """删除节点命令"""
    def __init__(self, view, node):
        self.view = view
        self.node = node
        self.edges = []

    def execute(self):
        # 保存所有连接的边
        for socket in self.node.sockets:
            self.edges.extend(socket.edges)
        # 移除节点
        self.view.scene().remove_node(self.node)

    def undo(self):
        # 恢复节点
        self.view.scene().add_node(self.node)
        # 恢复所有连接的边
        for edge in self.edges:
            self.view.scene().add_edge(edge)