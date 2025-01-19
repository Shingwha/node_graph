from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QPainter,QColor,QBrush,QPen
from PySide6.QtCore import QLine, Signal
import math
from commands import Command, AddNodeCommand, RemoveNodeCommand, AddEdgeCommand, RemoveEdgeCommand, CopyNodesCommand, PasteNodesCommand

class Scene(QGraphicsScene):
    changed = Signal()

    def __init__(self, scene, node_factory, parent=None):
        super().__init__()

        self.scene = scene
        self.node_factory = node_factory
        self.undo_stack = []
        self.redo_stack = []
        self.clipboard = None  # 剪贴板
        self.background_color = QColor('#212121')
        self.grid_color = QColor('#313131')
        self.grid_size = 30
        self.grid_pen = QPen(self.grid_color)
        self.grid_pen.setWidth(1)
        self.chunk_color = QColor('#151515')
        self.chunk_size = 5
        self.chunk_pen = QPen(self.chunk_color)
        self.chunk_pen.setWidth(2)
        self.setBackgroundBrush(QBrush(self.background_color))

        self.nodes = []
        self.edges = []
        self.scene_width = 64000
        self.scene_height = 64000

        self.initUI()

    def initUI(self):
        self.set_graphics_scene(self.scene_width, self.scene_height)

    def set_graphics_scene(self,width,height):
        self.setSceneRect(-width//2,-height//2,width,height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.setPen(self.grid_pen)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        grid_lines = []
        chunk_lines = []

        for v in range(first_top,bottom,self.grid_size):
            
            line = QLine(left,v,right,v)

            if v % (self.grid_size * self.chunk_size) == 0:
                chunk_lines.append(line)
            else:
                grid_lines.append(line)
        for h in range(first_left,right,self.grid_size):
            
            line = QLine(h,top,h,bottom)

            if h % (self.grid_size * self.chunk_size) == 0:
                chunk_lines.append(line)
            else:
                grid_lines.append(line)

        painter.setPen(self.grid_pen)
        painter.drawLines(grid_lines)
        painter.setPen(self.chunk_pen)
        painter.drawLines(chunk_lines)

    def push_command(self, command):
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self.changed.emit()

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
            self.changed.emit()

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.redo()
            self.undo_stack.append(command)
            self.changed.emit()

    def add_node(self, node):
        command = AddNodeCommand(self, node)
        command.redo()
        self.push_command(command)

    def add_edge(self, edge):
        command = AddEdgeCommand(self, edge)
        command.redo()
        self.push_command(command)

    def remove_node(self, node):
        command = RemoveNodeCommand(self, node)
        command.redo()
        self.push_command(command)

    def remove_edge(self, edge):
        command = RemoveEdgeCommand(self, edge)
        command.redo()
        self.push_command(command)

    def copy_nodes(self, nodes):
        """复制选中的节点"""
        command = CopyNodesCommand(self, nodes)
        command.redo()
        self.push_command(command)

    def paste_nodes(self, offset=(50, 50)):
        """粘贴节点"""
        command = PasteNodesCommand(self, offset)
        command.redo()
        self.push_command(command)
