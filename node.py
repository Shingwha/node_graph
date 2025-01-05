# node.py
from PySide6.QtWidgets import QGraphicsItem,QGraphicsProxyWidget,QGraphicsTextItem,QLineEdit
from PySide6.QtCore import QRectF, Qt, QPointF, QRegularExpression
from PySide6.QtGui import QBrush, QPen, QColor, QPainterPath, QFont,QRegularExpressionValidator
from socket import Socket
INPUT = 0
OUTPUT = 1

class Node(QGraphicsItem):

    def __init__(
        self, 
        title="Test Node", 
        input_sockets=[],  # 格式: [{"datatype": int, "box_type": int}]
        output_sockets=[],  # 格式: [{"datatype": int, "box_type": int}]
        type=1001,
        ):
        
        super().__init__()
        self.opacity = 0.7  # 添加透明度参数，范围0-1

        self.title_height = 20
        self.title_color = Qt.white
        self.title_font = QFont("Helvetica", 8)
        self.padding = 5
        self.socket_height = 18
        self.socket_radius = 4
        self.sockets_height = (max(len(input_sockets), len(output_sockets)) + 1) * self.socket_height
        self.height = self.title_height + self.sockets_height - 2*self.socket_radius
        self.width = 90
        self.edge_size = 3

        self.pen_default = QPen(QColor("#50B780"))
        self.pen_selected = QPen(QColor("#F2E383"))
        self.brush_title = QBrush(QColor("#1F7D6B"))
        self.brush_title.color().setAlphaF(self.opacity)
        self.brush_background = QBrush(QColor("#2a2a2a"))
        self.brush_background.color().setAlphaF(self.opacity)

        self.title = title
        self.type = type
        self.initTitle()
        self.initUI()
        self.input_sockets = []
        self.output_sockets = []
        self.initSockets(input_sockets, output_sockets)
        
    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self.title_color)
        self.title_item.setFont(self.title_font)
        self.title_item.setPos(self.padding,0)
        self.title_item.setTextWidth(self.width - 2*self.padding)
        self.title_item.setPlainText(self.title)

    def initSockets(self, inputs, outputs):
        self.input_sockets = [
            Socket(
                node=self, 
                index=i, 
                type=INPUT, 
                datatype=socket_config.get("datatype", 0), 
                box_type=socket_config.get("box_type", 0),
            ) for i, socket_config in enumerate(inputs)
        ]
        self.output_sockets = [
            Socket(
                node=self, 
                index=i, 
                type=OUTPUT, 
                datatype=socket_config.get("datatype", 0), 
                box_type=socket_config.get("box_type", 0),
            ) for i, socket_config in enumerate(outputs)
        ]

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for socket in self.input_sockets + self.output_sockets:
                for edge in socket.edges:
                    edge.update_path()
        return super().itemChange(change, value)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # title (不透明)
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0,0,self.width,self.title_height,self.edge_size,self.edge_size)
        path_title.addRect(0,self.title_height - self.edge_size,self.edge_size,self.edge_size)
        path_title.addRect(self.width - self.edge_size,self.title_height - self.edge_size,self.edge_size,self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush_title)
        painter.drawPath(path_title.simplified())

        # content (透明)
        painter.setOpacity(self.opacity)
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0,self.title_height,self.width,self.height - self.title_height,self.edge_size,self.edge_size)
        path_content.addRect(0,self.title_height,self.edge_size,self.edge_size)
        path_content.addRect(self.width - self.edge_size,self.title_height,self.edge_size,self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush_background)
        painter.drawPath(path_content.simplified())
        
        # outline
        painter.setOpacity(1.0)  # 恢复不透明
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0,0,self.width,self.height,self.edge_size,self.edge_size)
        painter.setPen(self.pen_default if not self.isSelected() else self.pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def get_socket_position(self, index, type):
        x = 0 if type == INPUT else self.width
        y = self.title_height + (index+1) * self.socket_height - self.socket_radius
        return [x,y]

    def remove(self):
        # 删除所有连接的edges
        for socket in self.input_sockets + self.output_sockets:
            for edge in socket.edges:
                edge.remove()
        # 从场景中移除节点
        if self.scene():
            self.scene().removeItem(self)

    def reset(self):
        for socket in self.input_sockets + self.output_sockets:
            socket.reset()
