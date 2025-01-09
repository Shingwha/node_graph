# edge.py
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtGui import QPainterPath, QPen, QPainter, QColor, QPainterPathStroker
from PySide6.QtCore import Qt, QPointF

class Edge(QGraphicsPathItem):
    def __init__(self, start_socket, end_socket):
        super().__init__()
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.start_socket.edges.append(self)
        if self.end_socket is not None:
            self.end_socket.edges.append(self)
        self.initEdge()
        self.pen = QPen(self.start_socket.background_color, 2)
        self.pen_selected = QPen(QColor("#F2E383"), 2)
        self.setPen(self.pen)
        self.setZValue(-1)  
        self.update_path()  # 立即更新路径
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def initEdge(self):
        if self.start_socket is None or self.end_socket is None:
            return
        if self.start_socket.type == 1:
            self.input_socket = self.end_socket
            self.output_socket = self.start_socket
        else:
            self.input_socket = self.start_socket
            self.output_socket = self.end_socket


    # 构建函数用于传递参数
    def transfer_value(self):
        if self.output_socket is not None:
            self.value = self.output_socket.value
            self.input_socket.value = self.value


    def update_path(self, mouse_pos=None):
        path = QPainterPath()
        start_pos = self.start_socket.scenePos()
        end_pos = mouse_pos if self.end_socket is None else self.end_socket.scenePos()
        if end_pos is not None:
            # 计算控制点
            dx = end_pos.x() - start_pos.x()
            dy = end_pos.y() - start_pos.y()
            ctrl1 = start_pos + QPointF(dx * 0.5, 0)
            ctrl2 = end_pos - QPointF(dx * 0.5, 0)
            path.moveTo(start_pos)
            path.cubicTo(ctrl1, ctrl2, end_pos)
            self.setPath(path)
            self.update()


    def remove(self):
        if self.start_socket and self in self.start_socket.edges:
            self.start_socket.edges.remove(self)
        if self.end_socket and self in self.end_socket.edges:
            self.end_socket.edges.remove(self)
        if self.scene() and self in self.scene().items():
            self.scene().removeItem(self)

    def boundingRect(self):
        return self.path().boundingRect().adjusted(-5, -5, 5, 5)  # 添加一些padding以便于点击

    def shape(self):
        path = QPainterPathStroker()
        path.setWidth(10)  # 设置点击区域的宽度
        return path.createStroke(self.path())

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen_selected if self.isSelected() else self.pen)
        painter.drawPath(self.path())
