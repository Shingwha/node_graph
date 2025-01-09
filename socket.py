# socket.py
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QPen, QColor
from box import LineEditBox,ImageBox

class Socket(QGraphicsItem):
    

    def __init__(self, node, index=0, type=0, datatype=1,box_type=0):
        super().__init__(node)
        self.node = node
        self.index = index
        self.type = type  # 0表示输入，1表示输出
        self.datatype = datatype
        self.position_x = 0  if self.type == 0 else self.node.width
        self.position_y = 0
        self.basic_height = 20  # 基础高度
        self.edges = []  # 存储多个Edge
        self._value = None  # 存储当前Socket的值
        self.box = None  # 存储当前Socket的输入框
        self.box_type = box_type  # 存储当前Socket的输入框类型
        # 初始化绘图属性
        self.radius = 5
        self.background_colors = [
            QColor("#39FA6A"),
            QColor("#cc6666"),
            QColor("#F7CBCB"),
        ]
        self.background_color = self.background_colors[self.datatype]
        self.outline_color = self.background_color.darker(130)
        self.outline_width = 2.0
        self.pen = QPen(self.outline_color, self.outline_width)
        self.brush_background = QBrush(self.background_color)
        self.brush_background_unconnected = QBrush(QBrush(QColor("#2a2a2a")))
        self.initBox()
        self.update_position()
        self.box.initUI() if self.box is not None else None



    @property
    def value(self):
        if self.has_edge():
            return self._value
        elif self.box is not None:
            return self.box.get_value()
        # return None

    @value.setter
    def value(self, new_value):
        self._value = new_value
        if self.box is not None:
            # self.box.update_display()
            self.node.update_display()
            self.node.update_display()
        
        

    def initBox(self):
        if self.box_type == 0:
            return
        if self.box_type == 1:
            self.box = LineEditBox(socket=self)
            
        if self.box_type == 2:
            self.box = ImageBox(socket=self)

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

    def update_position(self):
        self.position_x = 0 if self.type == 0 else self.node.width
        if self.type == 1:
            self.node.outputs_height += self.node.spacing + self.box.height  if self.box is not None else self.node.spacing + self.basic_height
            self.position_y = self.node.outputs_height - self.box.height/2 if self.box is not None else self.node.outputs_height - self.basic_height/2
            self.position_y = self.position_y + self.node.title_height
        else:
            self.node.inputs_height += self.node.spacing + self.box.height  if self.box is not None else self.node.spacing + self.basic_height
            self.position_y = self.node.inputs_height - self.box.height/2 if self.box is not None else self.node.inputs_height - self.basic_height/2
            self.position_y = self.position_y + self.node.outputs_height + self.node.title_height
        self.setPos(self.position_x, self.position_y)

    def reset(self):
        self._value = None


    def has_edge(self):
        return len(self.edges) > 0
