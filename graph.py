from node import Node
from collections import deque

class Graph():
    def __init__(self, scene):
        self.scene = scene
        self.nodes = scene.nodes
        self.edges = scene.edges

    def get_execution_order(self):
        # 构建邻接表和入度表
        adj_list = {node: [] for node in self.nodes}
        in_degree = {node: 0 for node in self.nodes}
        # 填充邻接表和入度表
        for edge in self.edges:
            if edge.output_socket and edge.input_socket:  # 确保socket存在
                start_node = edge.output_socket.node
                end_node = edge.input_socket.node
                if start_node in adj_list and end_node in in_degree:  # 确保节点在表中
                    adj_list[start_node].append(end_node)
                    in_degree[end_node] += 1
                else:
                    print(f"警告：节点 {start_node.title} 或 {end_node.title} 不在节点列表中")


        # 找到所有入度为0的节点（没有input_socket的节点）
        queue = deque()
        for node in self.nodes:
            if in_degree[node] == 0:
                queue.append(node)


        # 拓扑排序
        execution_order = []
        visited = set()
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            execution_order.append(node)
            
            # 减少相邻节点的入度
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检查是否有循环依赖
        if len(execution_order) != len(self.nodes):
            raise Exception("检测到循环依赖，无法确定执行顺序")
        return execution_order
    
    # 执行
    def execute(self):
        try:
            execution_order = self.get_execution_order()
            for node in execution_order:
                try:
                    node.run()
                    # 传递数据到下游节点
                    for socket in node.output_sockets:
                        for edge in socket.edges:
                            edge.transfer_value()
                except Exception as e:
                    print(f"节点 {node} 执行失败: {str(e)}")
                    raise
        except Exception as e:
            print(f"图执行失败: {str(e)}")
            raise

    def reset(self):
        for node in self.nodes:
            node.reset()
