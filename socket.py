# socket.py
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QPen, QColor
from boxes import Box

class Socket(QGraphicsItem):
    

    def __init__(self, node, index=0, type=0, datatype=1,box_type=0):
        super().__init__(node)
        self.node = node
        self.index = index
        self.type = type  # 0表示输入，1表示输出
        self.datatype = datatype
        x, y = self.node.get_socket_position(index, type)
        self.setPos(x, y)
        self.edges = []  # 存储多个Edge
        self._value = None  # 存储当前Socket的值
        self.box = None  # 存储当前Socket的输入框
        self.box_type = box_type  # 存储当前Socket的输入框类型
        # 初始化绘图属性
        self.radius = self.node.socket_radius
        self.background_colors = [
            QColor("#39FA6A"),
            QColor("#F3FF96"),
            QColor("#F7CBCB"),
        ]
        self.background_color = self.background_colors[0]
        self.outline_color = QColor("#39FA6A")
        self.outline_width = 1.0
        self.pen = QPen(self.outline_color, self.outline_width)
        self.brush_background = QBrush(self.background_color)
        self.brush_background_unconnected = QBrush(QBrush(QColor("#dbead5")))
        self.initBox()

    @property
    def value(self):
        if self.has_edge():
            return self._value
        elif self.box is not None:
            return self.box.get_value()
        return None

    @value.setter
    def value(self, new_value):
        self._value = new_value
        if self.box is not None:
            self.box.update_display()
        # 如果没有连接且graph存在，执行graph
        if not self.has_edge() and self.graph is not None:
            self.graph.execute()
        
        

    def initBox(self):
        if self.box_type == 0:
            return
        self.box = Box(socket=self, box_type=self.box_type)
        self.box.update_display()

    def boundingRect(self):
        return QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width)
        )

    def paint(self, painter, option, widget):
        if len(self.edges) > 0:  # 如果有连接
            painter.setBrush(self.brush_background)
        else:
            painter.setBrush(self.brush_background_unconnected)
        painter.setPen(self.pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def get_position(self):
        return self.node.get_socket_position(self.index, self.type)

    def reset(self):
        self._value = None


    def has_edge(self):
        return len(self.edges) > 0
