from PySide6.QtWidgets import QGraphicsView, QMenu
from PySide6.QtGui import QPainter, QMouseEvent, QCursor,QAction
from PySide6.QtCore import Qt, QPointF
from node_socket import Socket
from edge import Edge
from node import Node
from graph import Graph
from node_factory import NodeFactory
from commands import AddNodeCommand, AddEdgeCommand, RemoveNodeCommand, RemoveEdgeCommand,PasteCommand

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_RUBBER_BAND = 3
EDGE_DRAG_START_THRESHOLD = 10


class View(QGraphicsView):
    def __init__(self, scene, undo_stack):
        super().__init__(scene)
        self.undo_stack = undo_stack  # 新增
        self.clipboard = None
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

        self.node_factory = NodeFactory()

    def initUI(self):
        # 设置渲染提示：抗锯齿 文本抗锯齿 平滑图像变换
        self.setRenderHint(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭垂直滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭水平滚动条
        
        # 设置为随鼠标锚点进行缩放
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # 设置菜单样式
        self.setup_menu_style()

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
                # 创建临时连线，不加入撤销栈
                self.drag_edge = Edge(self.drag_start_socket, None)
                self.scene().add_edge(self.drag_edge)
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
            for edge in end_socket.edges[:]:
                self.scene().remove_edge(edge)
        # 如果start_socket是input且已有连接，先移除旧连接
        if start_socket.type == 0 and start_socket.edges:
            for edge in start_socket.edges[:]:
                self.scene().remove_edge(edge)
        # 创建新连接
        cmd = AddEdgeCommand(self.scene(), start_socket, end_socket)
        self.undo_stack.push(cmd)
        start_socket.update()
        end_socket.update()

    def RightButtonPress(self, event):
        """处理右键点击事件，显示对应的上下文菜单"""
        item = self.itemAt(event.pos())
        if isinstance(item, Node):
            self.show_node_context_menu(event)
        elif isinstance(item, Edge):
            self.show_edge_context_menu(event)
        else:
            self.show_background_context_menu(event)
        return super().mousePressEvent(event)

    def show_background_context_menu(self, event):
        """显示空白处的上下文菜单（添加节点 + 编辑操作）"""
        menu = QMenu(self)
        menu.setStyleSheet(self.menu_style)
        
        # 添加节点菜单
        node_menu = menu.addMenu("添加节点")
        pos = self.mapToScene(event.pos())
        self.populate_node_menu(node_menu, pos)
        
        menu.addSeparator()  # 分隔线
        
        # 复制粘贴删除操作
        self.add_edit_actions_to_menu(menu)
        
        menu.exec_(self.mapToGlobal(event.pos()))

    def show_node_context_menu(self, event):
        """显示节点的上下文菜单（复制/粘贴/删除）"""
        item = self.itemAt(event.pos())
        if not isinstance(item, Node):
            return
        
        # 确保只选中当前节点
        self.scene().clearSelection()
        item.setSelected(True)
        
        menu = QMenu(self)
        menu.setStyleSheet(self.menu_style)
        self.add_edit_actions_to_menu(menu)
        menu.exec_(self.mapToGlobal(event.pos()))

    def show_edge_context_menu(self, event):
        """显示边的上下文菜单（删除）"""
        item = self.itemAt(event.pos())
        if not isinstance(item, Edge):
            return
        
        # 确保只选中当前边
        self.scene().clearSelection()
        item.setSelected(True)
        
        menu = QMenu(self)
        menu.setStyleSheet(self.menu_style)
        
        delete_action = QAction("删除\tDel", self)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        menu.exec_(self.mapToGlobal(event.pos()))

    def populate_node_menu(self, parent_menu, position):
        """填充节点类型菜单"""
        groups = {
            "输入节点": [],
            "输出节点": [],
            "计算节点": [],
            "图像处理节点": []
        }
        
        # 分类节点类型
        for type_id, node_class in self.node_factory.node_type_map.items():
            if 1100 <= type_id < 1200:
                groups["计算节点"].append((type_id, node_class))
            elif 2100 <= type_id < 2200:
                groups["图像处理节点"].append((type_id, node_class))
            elif type_id % 100 == 1:
                groups["输入节点"].append((type_id, node_class))
            elif type_id % 100 == 2:
                groups["输出节点"].append((type_id, node_class))
        
        # 添加子菜单
        for group_name, nodes in groups.items():
            if nodes:
                sub_menu = parent_menu.addMenu(group_name)
                for type_id, node_class in nodes:
                    node_title = getattr(node_class, 'title', node_class.__name__)
                    action = sub_menu.addAction(node_title)
                    action.triggered.connect(
                        lambda checked=False, t=type_id, p=position: 
                            self.create_node(t, p)
                    )

    def add_edit_actions_to_menu(self, menu):
        """为菜单添加编辑操作（复制/粘贴/删除）"""
        # 复制
        copy_action = QAction("复制\tCtrl+C", self)
        copy_action.triggered.connect(self.copy_selected)
        copy_action.setEnabled(bool(self.scene().selectedItems()))
        menu.addAction(copy_action)
        
        # 粘贴
        paste_action = QAction("粘贴\tCtrl+V", self)
        paste_action.triggered.connect(self.paste)
        paste_action.setEnabled(bool(self.clipboard))
        menu.addAction(paste_action)
        
        # 删除
        delete_action = QAction("删除\tDel", self)
        delete_action.triggered.connect(self.delete_selected)
        delete_action.setEnabled(bool(self.scene().selectedItems()))
        menu.addAction(delete_action)

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
            self.delete_selected()
            event.accept()
        elif event.key() == Qt.Key_S:
            self.start_graph()
            event.accept()
        elif event.key() == Qt.Key_P:
            self.stop_graph()
            event.accept()
        elif event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_C:
                self.copy_selected()
                event.accept()
            elif event.key() == Qt.Key_V:
                self.paste()
                event.accept()
            elif event.key() == Qt.Key_Z:
                self.undo_stack.undo()
                event.accept()
            elif event.key() == Qt.Key_Y:
                self.undo_stack.redo()
                event.accept()
        else:
            super().keyPressEvent(event)
            
    def delete_selected(self):
        selected_items = self.scene().selectedItems()
        if not selected_items:
            return
        
        self.undo_stack.beginMacro("Delete Selected Items")
        for item in selected_items:
            if isinstance(item, Node):
                cmd = RemoveNodeCommand(self.scene(), item)
                self.undo_stack.push(cmd)
            elif isinstance(item, Edge):
                cmd = RemoveEdgeCommand(self.scene(), item)
                self.undo_stack.push(cmd)
        self.undo_stack.endMacro()

    def copy_selected(self):
        selected_nodes = [item for item in self.scene().selectedItems() if isinstance(item, Node)]
        if not selected_nodes:
            return
        
        clipboard_data = {
            'nodes': [],
            'edges': [],
            'center': None  # 新增中心点存储
        }
        
        # 计算选中节点的中心点
        sum_x = sum(node.scenePos().x() for node in selected_nodes)
        sum_y = sum(node.scenePos().y() for node in selected_nodes)
        center = QPointF(sum_x / len(selected_nodes), sum_y / len(selected_nodes))
        clipboard_data['center'] = {'x': center.x(), 'y': center.y()}
        
        node_indices = {node: idx for idx, node in enumerate(selected_nodes)}
        
        # Serialize nodes
        for node in selected_nodes:
            node_data = {
                'type': node.type,
                'position': {'x': node.scenePos().x(), 'y': node.scenePos().y()},
                'sockets': self._serialize_node_sockets(node)
            }
            clipboard_data['nodes'].append(node_data)
        
        # Serialize edges
        for edge in self.scene().edges:
            # 关键修复：检查 socket 是否存在且节点在选中列表中
            if (
                edge.start_socket is not None
                and edge.end_socket is not None
                and edge.start_socket.node in node_indices
                and edge.end_socket.node in node_indices
            ):
                edge_data = {
                    'from_node_index': node_indices[edge.start_socket.node],
                    'from_socket_index': edge.start_socket.index,
                    'to_node_index': node_indices[edge.end_socket.node],
                    'to_socket_index': edge.end_socket.index
                }
                clipboard_data['edges'].append(edge_data)
        
        self.clipboard = clipboard_data

    def paste(self):
        if not self.clipboard:
            return
        
        # 获取鼠标当前位置（场景坐标）
        mouse_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        
        # 计算偏移量：鼠标位置 - 原中心点
        if 'center' in self.clipboard and self.clipboard['center'] is not None:
            original_center = QPointF(self.clipboard['center']['x'], self.clipboard['center']['y'])
            offset = mouse_pos - original_center
        else:
            offset = QPointF(20, 20)  # 默认偏移
        
        cmd = PasteCommand(self.scene(), self.clipboard, offset)
        self.undo_stack.push(cmd)

    def _serialize_node_sockets(self, node):
        sockets_data = []
        for socket in node.input_sockets + node.output_sockets:
            socket_data = {
                'index': socket.index,
                'type': socket.type,
                'box_type': socket.box_type,
            }
            # 不保存ImageBox的图片数据和值
            if socket.box_type != 2:  # 2代表ImageBox
                socket_data['value'] = socket.value
            sockets_data.append(socket_data)
        return sockets_data

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

    def setup_menu_style(self):
        """设置菜单样式"""
        self.menu_style = """
            QMenu {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                padding: 5px;
                border-radius: 7px;
            }
            QMenu::item {
                color: #DCDCDC;
                padding-left: 7px;
                padding-right: 15px;
                padding-top: 8px;
                padding-bottom: 8px;
                
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3E3E40;
            }
            QMenu::item:disabled {
                color: #808080;
            }
            QMenu::separator {
                height: 1px;
                background: #3F3F46;
                margin: 5px 0;
            }
        """


    def create_node(self, node_type, pos):
        """根据节点类型创建节点"""
        try:
            cmd = AddNodeCommand(self.scene(), node_type, pos)
            self.undo_stack.push(cmd)
        except ValueError as e:
            print(f"创建节点失败: {e}")
