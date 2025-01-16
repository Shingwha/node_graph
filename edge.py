# edge.py
import math
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtGui import QPainterPath, QPen, QPainter, QColor, QPainterPathStroker
from PySide6.QtCore import Qt, QPointF

EDGE_CP_ROUNDNESS = 0.5  # 控制点曲率系数

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
        start_pos = self.start_socket.scenePos()
        end_pos = mouse_pos if self.end_socket is None else self.end_socket.scenePos()
        
        if end_pos is None:
            return
            
        dist = (end_pos.x() - start_pos.x()) * 0.5

        ctrl1_x = +dist
        ctrl2_x = -dist
        ctrl1_y = 0
        ctrl2_y = 0

        if self.start_socket is not None:
            if (start_pos.x() > end_pos.x() and self.start_socket.type == 1) or (start_pos.x() < end_pos.x() and self.start_socket.type == 0):
                ctrl2_x *= -1
                ctrl1_x *= -1

                ctrl2_y = (
                    (start_pos.y() - end_pos.y()) / math.fabs(
                        (start_pos.y() - end_pos.y()) if (start_pos.y() - end_pos.y()) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS
                ctrl1_y = (
                    (end_pos.y() - start_pos.y()) / math.fabs(
                        (end_pos.y() - start_pos.y()) if (end_pos.y() - start_pos.y()) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(start_pos)
        path.cubicTo(
            start_pos.x() + ctrl1_x, start_pos.y() + ctrl1_y,
            end_pos.x() + ctrl2_x, end_pos.y() + ctrl2_y,
            end_pos.x(), end_pos.y()
        )
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
