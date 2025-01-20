from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QPainter,QColor,QBrush,QPen
from PySide6.QtCore import QLine
import math

class Scene(QGraphicsScene):
    def __init__(self, scene, node_factory, parent=None):
        super().__init__()

        self.scene = scene
        self.node_factory = node_factory
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

    def add_node(self, node):
        self.nodes.append(node)
        self.addItem(node)

    def add_edge(self, edge):
        # 仅在边两端插座都存在时添加
        if edge.start_socket is not None and edge.end_socket is not None:
            if edge not in self.edges:
                self.edges.append(edge)
                self.addItem(edge)
                # 确保边被正确关联到插座
                edge.start_socket.edges.append(edge)
                edge.end_socket.edges.append(edge)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            # 断开所有关联的边
            for socket in node.input_sockets + node.output_sockets:
                for edge in socket.edges.copy():  # 使用copy避免遍历时修改
                    self.remove_edge(edge)
            self.removeItem(node)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
            # 清理socket引用
            if edge.start_socket and edge in edge.start_socket.edges:
                edge.start_socket.edges.remove(edge)
            if edge.end_socket and edge in edge.end_socket.edges:
                edge.end_socket.edges.remove(edge)
            if edge in self.items():  # 更严格的场景检查
                self.removeItem(edge)
