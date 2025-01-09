from PySide6.QtWidgets import QGraphicsView, QMenu
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtCore import Qt
from socket import Socket
from edge import Edge
from node import Node
from graph import Graph
from nodes.input_node import *
from nodes.output_node import *
from nodes.calculate_node import *

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_RUBBER_BAND = 3
EDGE_DRAG_START_THRESHOLD = 10


class View(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.initUI()
        # scale
        self.zoom_in_factor = 1.25
        self.zoom_out_factor = 1 / self.zoom_in_factor
        self.zoom = 5
        self.zoom_clamp = False # 是否限制缩放范围
        self.zoom_step = 1 # 缩放步长
        self.zoom_range = [0, 10] # 缩放范围
        self.mode = MODE_NOOP
        
        # 拖动连接相关
        self.drag_start_socket = None
        self.drag_edge = None
        self.drag_start_pos = None

        # 初始化节点类型映射
        self.node_types = {
            "输入节点": NumberInputNode,
            "图片输入": ImageInputNode,
            "输出节点": NumberOutputNode,
            "图片输出": ImageOutputNode,
            "加法节点": SumNode,
            "减法节点": SubtractNode,
            "乘法节点": MultiplyNode,
            "除法节点": DivideNode,
            "幂运算节点": PowerNode,
            "平方根节点": SqrtNode
        }

    def initUI(self):
        # 设置渲染提示：抗锯齿 文本抗锯齿 平滑图像变换
        self.setRenderHint(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭垂直滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭水平滚动条
        
        # 设置为随鼠标锚点进行缩放
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.MiddleButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.RightButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.LeftButtonPress(event)
        else:
            return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.MiddleButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.RightButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.LeftButtonRelease(event)
        else:
            return super().mouseReleaseEvent(event)


    def MiddleButtonPress(self, event):
        releaseEvent = QMouseEvent(QMouseEvent.MouseButtonPress, event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def MiddleButtonRelease(self, event):
        # 模拟左键释放
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)


    def LeftButtonPress(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, Socket):
            self.drag_start_socket = item
            self.drag_start_pos = self.mapToScene(event.pos())
            self.mode = MODE_EDGE_DRAG
            # 在拖动连接线时禁用节点拖动
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            # 如果点击空白区域，进入框选模式
            self.rubber_band_start = event.pos()
            self.mode = MODE_RUBBER_BAND
            self.setDragMode(QGraphicsView.RubberBandDrag)
            super().mousePressEvent(event)
        

    def LeftButtonRelease(self, event):
        if self.mode == MODE_EDGE_DRAG:
            item = self.itemAt(event.pos())
            if isinstance(item, Socket) and item != self.drag_start_socket:
                if self.can_connect(self.drag_start_socket, item):
                    self.create_edge(self.drag_start_socket, item)
            if self.drag_edge:
                # 移除临时Edge对Socket的影响
                if self.drag_start_socket and self.drag_edge in self.drag_start_socket.edges:
                    self.drag_start_socket.edges.remove(self.drag_edge)
                if self.drag_edge.scene() and self.drag_edge in self.drag_edge.scene().items():
                    self.scene().removeItem(self.drag_edge)
                self.drag_edge = None
                # 更新Socket显示
                if self.drag_start_socket:
                    self.drag_start_socket.update()
            self.drag_start_socket = None
        elif self.mode == MODE_RUBBER_BAND:
            # 处理框选结果
            selected_items = self.scene().selectedItems()
            for item in selected_items:
                if isinstance(item, Node):
                    item.setSelected(True)
        
        self.mode = MODE_NOOP
        self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            if not self.drag_edge:
                self.drag_edge = Edge(self.drag_start_socket, None)
                self.scene().addItem(self.drag_edge)
            end_pos = self.mapToScene(event.pos())
            self.drag_edge.end_socket = None
            self.drag_edge.update_path(end_pos)
        super().mouseMoveEvent(event)

    def can_connect(self, start_socket, end_socket):
        if start_socket.datatype != end_socket.datatype:
            return False
        if start_socket.type == end_socket.type:
            return False
        if start_socket.node == end_socket.node:
            return False
        return True

    def create_edge(self, start_socket, end_socket):
        # 如果end_socket是input且已有连接，先移除旧连接
        if end_socket.type == 0 and end_socket.edges:
            for edge in end_socket.edges[:]:  # 使用切片创建副本以避免修改正在迭代的列表
                edge.remove()
        # 如果start_socket是input且已有连接，先移除旧连接
        if start_socket.type == 0 and start_socket.edges:
            for edge in start_socket.edges[:]:  # 使用切片创建副本以避免修改正在迭代的列表
                edge.remove()
        # 创建新连接
        edge = Edge(start_socket, end_socket)
        self.scene().add_edge(edge)  # 将边添加到scene的edges列表中
        start_socket.update()
        end_socket.update()

    def RightButtonPress(self, event):
        # 右键点击时显示节点创建菜单
        self.create_nodes_menu(event)
        return super().mousePressEvent(event)

    def RightButtonRelease(self, event):
        return super().mouseReleaseEvent(event)

    def wheelEvent(self,event):
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = self.zoom_out_factor
            self.zoom -= self.zoom_step
        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom = self.zoom_range[0]
            clamped = True
        elif self.zoom > self.zoom_range[1]:
            self.zoom = self.zoom_range[1]
            clamped = True
        if not clamped or not self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            # 删除所有选中的items
            for item in self.scene().selectedItems():
                if isinstance(item, (Node, Edge)):
                    item.remove()
            event.accept()
        elif event.key() == Qt.Key_S:
            self.start_graph()
            event.accept()
        elif event.key() == Qt.Key_P:
            self.stop_graph()
            event.accept()
        else:
            super().keyPressEvent(event)
            
    def start_graph(self):
        if hasattr(self, 'graph') and self.graph is not None:
            self.graph.reset()
            self.graph.execute()
            # 打印重新执行
            print("Graph execution restarted")
            return
            
        # 创建Graph实例并执行
        self.graph = Graph(self.scene())
        self.graph.execute()
        print("Graph execution started")
        
    def stop_graph(self):
        if not hasattr(self, 'graph') or self.graph is None:
            print("No graph is running")
            return
        self.graph = None
        print("Graph execution stopped")

    def create_nodes_menu(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            # 创建上下文菜单
            menu = QMenu(self)
            
            # 动态添加节点创建选项
            actions = {}
            for node_name in self.node_types:
                actions[node_name] = menu.addAction(f"创建{node_name}")
            
            # 显示菜单并获取选择
            action = menu.exec_(self.mapToGlobal(event.pos()))
            
            if action:
                # 获取点击位置
                pos = self.mapToScene(event.pos())
                # 根据选择创建节点
                self.create_node(action.text().replace("创建", ""), pos)
        else:
            return super().mousePressEvent(event)

    def create_node(self, node_type, pos):
        """根据节点类型创建节点"""
        if node_type in self.node_types:
            node_class = self.node_types[node_type]
            node = node_class()
            node.setPos(pos)
            self.scene().add_node(node)
