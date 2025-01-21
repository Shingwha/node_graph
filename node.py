# node.py
from PySide6.QtWidgets import QGraphicsItem,QGraphicsProxyWidget,QGraphicsTextItem,QLineEdit
from PySide6.QtCore import QRectF, Qt, QPointF, QRegularExpression
from PySide6.QtGui import QBrush, QPen, QColor, QPainterPath, QFont,QRegularExpressionValidator
from node_socket import Socket
from theme import Font, Color
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
        self.title_font_color = QColor(Color.NODE_TITLE_FONT)
        self.title_font = QFont(Font.NODE_TITLE, Font.NODE_TITLE_SIZE)
        self.inputs_height = 0
        self.outputs_height = 0
        self.content_height = 0
        self.padding = 5
        self._height = self.title_height + self.content_height
        self.width = 120
        self.edge_size = 3
        self.spacing = 7
        self.type = type
        self.initColor()

        self.title = title

        self.input_sockets = []
        self.output_sockets = []
        self.height = self.title_height + self.content_height
        self.initSockets(input_sockets, output_sockets)
        self.update_display()
        self.initTitle()
        self.initUI()

    @property
    def height(self):
        return self.title_height + self.content_height

    @height.setter
    def height(self, value):
        self._height = value

    def initColor(self):
        """根据节点类型设置颜色"""
        if 2000 < self.type < 2199:  # 图像处理节点
            self.pen_default = QPen(QColor(Color.IMAGE_NODE))
            self.pen_selected = QPen(QColor(Color.NODE_SELECTED))
            self.brush_title = QBrush(QColor(Color.IMAGE_NODE))
        else:  # 默认颜色
            self.pen_default = QPen(QColor(Color.NODE_DEFAULT))
            self.pen_selected = QPen(QColor(Color.NODE_SELECTED))
            self.brush_title = QBrush(QColor(Color.NODE_TITLE))
        self.brush_title.color().setAlphaF(self.opacity)
        self.brush_background = QBrush(QColor(Color.BACKGROUND))
        self.brush_background.color().setAlphaF(self.opacity)

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self.title_font_color)
        self.title_item.setFont(self.title_font)
        self.title_item.setPos(self.padding,0)
        self.title_item.setTextWidth(self.width - 2*self.padding)
        self.title_item.setPlainText(self.title)

    def initSockets(self, inputs, outputs):
        self.output_sockets = [
            Socket(
                node=self, 
                index=i, 
                type=OUTPUT, 
                datatype=socket_config.get("datatype", 0), 
                box_type=socket_config.get("box_type", 0),
            ) for i, socket_config in enumerate(outputs)
        ]
        self.input_sockets = [
            Socket(
                node=self, 
                index=i, 
                type=INPUT, 
                datatype=socket_config.get("datatype", 0), 
                box_type=socket_config.get("box_type", 0),
            ) for i, socket_config in enumerate(inputs)
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
        path_content.addRoundedRect(0, self.title_height, self.width, self.content_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
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


    def reset(self):
        for socket in self.input_sockets + self.output_sockets:
            socket.reset()

    def update_display(self):
        self.prepareGeometryChange()
        # 重置高度
        self.inputs_height = 0
        self.outputs_height = 0
        
        
        # 更新所有sockets
        for socket in self.output_sockets + self.input_sockets:
            socket.update_position()
            socket.update()
            for edge in socket.edges:
                edge.update_path()
            if socket.box is not None:
                socket.box.update_display()
                socket.box.update_position()
        
        # 计算最终高度
        self.content_height = max(self.inputs_height, self.outputs_height) + self.spacing
        self.height = self.title_height + self.content_height
        self.update()
