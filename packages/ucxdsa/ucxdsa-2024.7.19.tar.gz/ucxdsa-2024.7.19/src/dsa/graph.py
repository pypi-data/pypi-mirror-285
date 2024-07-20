from dsa.queue import Queue
from dsa.heap import MinHeap

class AdjacencyMatrixGraph:
    """ 
    An unweighted adjacency matrix graph implementation in Python
    (allows either directed or undirected representation)
    """
    def __init__(self, labels: list[str]):
        """ 
        Args:
            labels: list of labels for each vertex
        """
        self.labels = labels
        self.label_index = { label: index for index, label  in enumerate(labels) }

        node_count = len(self.labels)
        self.array = [[None for i in range(node_count)] for j in range(node_count)]

    def add_edge(self, a_label: str, b_label: str):
        """ 
        Add an undirected edge between one vertex to another (same as add_edge())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
        """
        self.add_adjacent_vertex(a_label, b_label)
        
    def add_adjacent_vertex(self, a_label: str, b_label: str):
        """ 
        Add an undirected edge between one vertex to another (same as add_adjacent_vertex())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
        """
        a = self.label_index[a_label]
        b = self.label_index[b_label]
        self.array[a][b] = True
        self.array[a][a] = True

        self.array[b][a] = True
        self.array[b][b] = True

    def add_directed_edge(self, a_label: str, b_label: str):
        """ 
        Add a directed edge between one vertex to another (same as add_directed_adjacent_vertex() and add_adjacent_directed_vertex())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
        """
        self.add_adjacent_directed_vertex(a_label, b_label)

    def add_directed_adjacent_vertex(self, a_label: str, b_label: str):
        """ 
        Add a directed edge between one vertex to another (same as add_adjacent_directed_vertex()  and add_directed_edge())
 
        Args:
            a_label: starting vertex label
            b_label: ending vertex label
        """
        self.add_adjacent_directed_vertex(a_label, b_label)
        
    def add_adjacent_directed_vertex(self, a_label: str, b_label: str):
        """ 
        Add a directed edge between one vertex to another (same as add_directed_adjacent_vertex() and add_directed_edge())
 
        Args:
            a_label: starting vertex label
            b_label: ending vertex label
        """
        a = self.label_index[a_label]
        b = self.label_index[b_label]
        self.array[a][b] = True
        self.array[a][a] = True
        self.array[b][b] = True

    def df_traverse(self, start_label: str):
        """ 
        Perform depth first traversal in an adjacency matrix
 
        Args:
            start_label: starting vertex label
        """
        return self._df_rec_traverse(start_label, set(), [])
        
    def _df_rec_traverse(self, start_label: str, visited, dfs):
        """ 
        Helper method for depth first recursive traversal
        """

        start_index = self.label_index[start_label]
        visited.add(start_label)
        dfs.append(self.labels[start_index])

        for adj_index, is_connected in enumerate(self.array[start_index]):
            adj_label = self.labels[adj_index]
            if is_connected and adj_label not in visited:
                self._df_rec_traverse(adj_label, visited, dfs)

        return dfs

    def bf_traverse(self, start_label: str):
        """ 
        Perform breadth first traversal in an adjacency matrix
 
        Args:
            start_label: starting vertex label
        
        Returns:
            array with breadth first order traversal
        """
        bfs = []
        q = Queue()
        visited = set()

        start_index = self.label_index[start_label]
        q.enqueue(start_index)
        bfs.append(self.labels[start_index])
        while not q.is_empty():
            current = q.dequeue()
            for i in range(len(self.array)):
                if start_index != i and self.array[current][i] and (i not in visited):
                    visited.add(i)
                    q.enqueue(i)
                    bfs.append(self.labels[i])
        return bfs
    
    def vertices(self):
        """"
        return a list of vertex labels of the graph
        """
        return self.labels
    
    def edges(self):
        """ 
        Return a list of edges in the graph. Each edge is represented by a tuple (start, end)
        """
        edges = []
        vertex_count = len(self.labels)
        for i in range(vertex_count):
            for j in range(vertex_count):
                if self.array[i][j] and i != j:  
                    edges.append((self.labels[i], self.labels[j]))
    
        return edges

    def print_graph(self):
        """ 
        Print the contents of the graph
        """
        print("   |", end="")
        for label in self.labels:
            print(f"{label:^3}", end=" ")
        print()
        print("----" * (len(self.array) + 1))
        for r, row in enumerate(self.array):
            label = self.labels[r]
            print(f"{label:^3}|", end="");
            for col in row:
                b = " T " if col else "   "
                print(b, end=" ")
            print()
            
class AdjacencyMatrixWeightedGraph(AdjacencyMatrixGraph):
    """ 
    A weighted adjacency matrix graph implementation in Python
    (allows either directed or undirected representation)
    """
    def __init__(self, labels):
        """ 
        Args:
            labels: list of labels for each vertex
        """
        super().__init__(labels)

    def add_edge(self, a_label: str, b_label: str, weight):
        """ 
        Add an undirected edge between one vertex to another (same as add_edge())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
            weight: weight of the vertex
        """
        self.add_adjacent_vertex(a_label, b_label, weight)

    def add_adjacent_vertex(self, a_label: str, b_label: str, weight):
        """ 
        Add an undirected edge between one vertex to another (same as add_edge())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
            weight: weight of the vertex
        """
        a = self.label_index[a_label]
        b = self.label_index[b_label]

        self.array[a][b] = weight
        self.array[a][a] = 0

        self.array[b][a] = weight
        self.array[b][b] = 0

    def add_directed_edge(self, a_label: str, b_label: str, weight):
        """ 
        Add a weighted directed edge between one vertex to another (same as add_adjacent_directed_vertex(), add_directed_adjacent_vertex())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
            weight: weight of the vertex
        """
        self.add_adjacent_directed_vertex(a_label, b_label, weight)

    def add_directed_adjacent_vertex(self, a_label: str, b_label: str, weight):
        """ 
        Add a weighted directed edge between one vertex to another (same as add_directed_edge(), add_adjacent_directed_vertex())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
            weight: weight of the vertex
        """
        self.add_adjacent_directed_vertex(a_label, b_label, weight)

    def add_adjacent_directed_vertex(self, a_label: str, b_label: str, weight):
        """ 
        Add a weighted directed edge between one vertex to another (same as add_directed_edge(), add_directed_adjacent_vertex())

        Args:
            a_label: starting vertex label
            b_label: ending vertex label
            weight: weight of the vertex
        """
        a = self.label_index[a_label]
        b = self.label_index[b_label]

        self.array[a][b] = weight
        self.array[a][a] = 0
        self.array[b][b] = 0
        
    def print_graph(self):
        """ 
        Print the contents of the graph.
        """
        print("   |", end="")
        for label in self.labels:
            print(f"{label:>3}", end=" ")
        print()
        print("----" * (len(self.array) + 1))
        for r, row in enumerate(self.array):
            label = self.labels[r]
            print(f"{label:^3}|", end="");
            for col in row:
                w = f"{col:3}" if col is not None else "   "
                print(w, end=" ")
            print()

    def edges(self):
        """ 
        Return a list of edges in the graph. Each edge is represented by a tuple (start, end, weight)
        """
        edges = []
        vertex_count = len(self.labels)
        for i in range(vertex_count):
            for j in range(vertex_count):
                weight = self.array[i][j]
                if weight and i != j:  
                    edges.append((self.labels[i], self.labels[j], weight))
    
        return edges
            
class Vertex:
    """ for type checking """
    pass

class Vertex:
    """ 
    (deprecated: use AdjacencyListGraph list)
    A unweighted adjacency list vertex implementation in Python
    (allows either directed or undirected representation)
    """
    def __init__(self, value):
        """ 
        Args:
            value: value of the vertex
        """
        #: value of the vertex
        self.value = value
        #: list of adjacent vertices
        self.adjacents = []
        
    def add_adjacent_vertex(self, vertex: type[Vertex]):
        """ 
        Add an undirected vertex to the adjacency list (same as add_edge()).

        Args:
            vertex: vertex to add
        """
        if vertex not in self.adjacents:
            self.adjacents.append(vertex)
        if self not in vertex.adjacents:
            vertex.add_adjacent_vertex(self)
        
    def add_edge(self, vertex: type[Vertex]):
        """ 
        Add an undirected vertex to the adjacency list (same as add_adjacent_vertex()).

        Args:
            vertex: vertex to add
        """
        self.add_adjacent_vertex(vertex)

    def add_directed_edge(self, vertex: type[Vertex]):
        """ 
        Add a directed vertex to the adjacency list (same as add_directed_adjacent_vertex()).

        Args:
            vertex: vertex to add
        """
        self.add_directed_adjacent_vertex(vertex)
        
    def add_directed_adjacent_vertex(self, vertex: type[Vertex]):
        """ 
        Add a directed vertex to the adjacency list (same as add_directed_edge()).

        Args:
            vertex: vertex to add
        """
        if vertex not in self.adjacents:
            self.adjacents.append(vertex)

    def df_traverse(self):
        """
        Perform depth first traversal.
        """
        self._df_traverse_rec(self, set())

    def _df_traverse_rec(self, vertex: type[Vertex], visited={}):
        """
        helper depth first traversal recursive function
        """
        visited[vertex] = True
        print(vertex.value)
        
        for v in vertex.adjacents:
            if not visited.get(v, False):
                v._df_traverse_rec(v, visited)
            
    def bf_traverse(self):
        """
        Perform breadth first traversal.
        """
        start = self
        visited = {}
        queue = []
        
        queue.append(start)

        while len(queue) > 0:
            current = queue[0]
            del queue[0]
            
            if not visited.get(current, False):               
                visited[current] = True
                print(current.value)
        
                for v in current.adjacents:
                    queue.append(v)
        
    def dfs(self, end):
        """ 
        Recursive depth first search.

        Args:
            end: vertex to search for
        Returns:
        Vertex in the graph
        None if not found.
        """
        return self.dfs_rec(self, end, dict())
        
    def dfs_rec(self, current, end, visited=None):
        """
        helper depth first search recursive function

        Returns:
        Vertex in the graph
        None if not found.
        """
        if current.value == end.value:
            print("Found: ", end.value)
            return current

        visited[current] = True
        print(current.value)
        
        for v in current.adjacents:
            if not visited.get(v, False):
                return v.dfs_rec(v, end, visited)
        return None
    
    def bfs(self, end):
        """ 
        Recursive breadth first search.

        Args:
            end: vertex to search for
        Returns:
        Vertex in the graph
        None if not found.
        """
        visited = {}
        queue = []
        start = self
        
        visited[start] = True
        queue.append(start)

        while len(queue) > 0:
            current = queue[0]
            del queue[0]
            print(current.value)
            # print("Visited: ", visited)
            # print("Queue: ", queue)
            
            if current.value == end.value:
                return current
            
            for v in current.adjacents:
                if not visited.get(v, False):               
                    visited[v] = True
                    queue.append(v)
        
        return None

    def __repr__(self):
        return self.value

class AdjacencyListGraph:
    """ 
    A unweighted adjacency list vertex implementation in Python
    (allows either directed or undirected representation)
    """
    def __init__(self):
        #: hash table of vertices in graph
        self._adjacents = {}
        
    def add_adjacent_vertex(self, start: str, end: str):
        """ 
        Add an undirected vertex to the adjacency list (same as add_edge()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
        """
        self.add_directed_adjacent_vertex(start, end)
        if end not in self._adjacents:
            self._adjacents[end] = [start]
        else:
            if start not in self._adjacents[end]:
                self._adjacents[end].append(start)
        
    def add_edge(self, start: str, end: str):
        """ 
        Add an undirected vertex to the adjacency list (same as add_adjacent_vertex()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
        """
        self.add_adjacent_vertex(start, end)

    def add_directed_edge(self, start: str, end: str):
        """ 
        Add a directed vertex to the adjacency list (same as add_directed_adjacent_vertex()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
        """
        self.add_directed_adjacent_vertex(start, end)
        
    def add_directed_adjacent_vertex(self, start: str, end: str):
        """ 
        Add a directed vertex to the adjacency list (same as add_directed_edge()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
        """
        if start not in self._adjacents:
            self._adjacents[start] = [end]
        else:
            if end not in self._adjacents[start]:
                self._adjacents[start].append(end)
        if end not in self._adjacents:
            self._adjacents[end] = []

    def adjacents(self, vertex: str):
        return self._adjacents[vertex]

    def df_traverse(self, start_label: str):
        """
        Perform depth first traversal.
        """
        return self._df_rec_traverse(start_label, set(), [])

    def _df_rec_traverse(self, start_label: str, visited, dfs):
        """
        helper depth first traversal recursive function
        """
        visited.add(start_label)
        dfs.append(start_label)
        
        for v in self[start_label]:
            if v not in visited:
                self._df_rec_traverse(v, visited, dfs)
        return dfs
    
    def bf_traverse(self, start: str):
        """
        Print the vertex labels in a breadth first traversal.
        Args:
            start: starting vertex label 
        """
        visited = set()
        q = Queue()
        bfs = []

        q.enqueue(start)
        visited.add(start)
        bfs.append(start)

        while len(q) > 0:
            current = q.dequeue()

            for v in self[current]:
                if v not in visited:               
                    visited.add(v)
                    q.enqueue(v)
                    bfs.append(v)
        return bfs
        
    def dfs(self, start, end):
        """ 
        Recursive depth first search.

        Args:
            start: beginning vertex
            end: vertex to search for
        Returns:
        Vertex in the graph
        None if not found.
        """
        return self.dfs_rec(start, end, dict())
        
    def dfs_rec(self, current, end, visited=None):
        """
        helper depth first search recursive function

        Returns:
        Vertex in the graph
        None if not found.
        """
        if current == end:
            print("Found: ", end)
            return current

        visited[current] = True
        print(current)
        
        for v in self.adjacents(current):
            if not visited.get(v, False):
                return self.dfs_rec(v, end, visited)
        return None
    
    def bfs(self, start, end):
        """ 
        breadth first search.

        Args:
            start: beginning vertex
            end: vertex to search for
        Returns:
            label of found vertex
            None if not found.
        """
        visited = {}
        queue = []
        
        visited[start] = True
        queue.append(start)

        while len(queue) > 0:
            current = queue[0]
            del queue[0]
            print(current)
            # print("Visited: ", visited)
            # print("Queue: ", queue)
            
            if current == end:
                return current
            
            for v in self[current]:
                if not visited.get(v, False):               
                    visited[v] = True
                    queue.append(v)
        
        return None
    
    def __getitem__(self, vertex: str):
        """ 
        Args:
            vertex: vertex label
        Returns:
            a list of adjacent vertex labels
        """

        return self._adjacents[vertex]
    
    def __len__(self):
        return len(self._adjacents)

    def edges(self):
        """ 
        Return a list of edges in the graph. Each edge is represented by a tuple (start, end)
        """
        edges = []
        for start in self._adjacents.keys():
            for end in self.adjacents(start):
                if start != end:  
                    edges.append((start, end))
        return edges

class WeightedVertex:
    """ for type checking """
    pass

class WeightedVertex:
    """ (Deprecated)
    A weighted adjacency list vertex implementation in Python
    (allows either directed or undirected representation)
    """
    def __init__(self, value):
        """ 
        Args:
            value: value of the vertex
        """
        self.value = value
        self.adjacents = {}
        
    # same as add_adjacent_vertex
    def add_edge(self, vertex: type[WeightedVertex], weight):
        """ 
        Add a weighted directed edge to the adjacency list (same as add_adjacent_vertex()).

        Args:
            vertex: vertex to add
            weight: weight of the vertex
        """
        self.add_adjacent_vertex(vertex, weight)

    # same as add_directed_adjacent_vertex
    def add_directed_edge(self, vertex: type[WeightedVertex], weight):
        """ 
        Add a weighted directed edge to the adjacency list (same as add_directed_adjacent_vertex()).

        Args:
            vertex: vertex to add
            weight: weight of the vertex
        """
        self.add_directed_adjacent_vertex(vertex, weight)

    def add_directed_adjacent_vertex(self, vertex: type[WeightedVertex], weight):
        """ 
        Add a weighted directed edge to the adjacency list (same as add_directed_edge()).

        Args:
            vertex: vertex to add
            weight: weight of the vertex
        """
        if vertex not in self.adjacents:
            self.adjacents[vertex] = weight

    def add_adjacent_vertex(self, vertex: type[WeightedVertex], weight):
        """ 
        Add a weighted edge to the adjacency list (same as add_directed_edge()).

        Args:
            vertex: vertex to add
            weight: weight of the vertex
        """
        if vertex not in self.adjacents:
            self.adjacents[vertex] = weight
        if self not in vertex.adjacents:
            vertex.adjacents[self] = weight
        
    def df_traverse(self, vertex: type[WeightedVertex], visited={}):
        """ 
        depth first traversal 

        Args:
            vertex: starting vertex
            visited: dictionary of visited vertices
        """
        visited[vertex] = True
        print(vertex.value)
        
        for v in vertex.adjacents:
            if not visited.get(v, False):
                v.df_traverse(v, visited)
            
    def bf_traverse(self, vertex: type[WeightedVertex]):
        """ 
        breadth first traversal 
        
        Args:
            vertex: starting vertex
        """
        visited = {}
        queue = []
        
        queue.append(vertex)

        while len(queue) > 0:
            current = queue[0]
            del queue[0]
            
            if not visited.get(current, False):               
                visited[current] = True
                print(current.value)
        
                for v in current.adjacents:
                    queue.append(v)
                    
    def dfs(self, target: type[WeightedVertex]):
        """ 
        depth first search 

        Args:
            target: target value to search for
        """
        return self._dfs_rec(self, target, dict())
        
    def _dfs_rec(self, current, end, visited={}):
        """ 
        recursive depth first search healper function

        Args:
            current: starting vertex
            end: target vertex to search for
            visited: dictionary of visited values
        """

        print(current.value, visited.keys())
        if current.value == end.value:
            return current

        visited[current] = True
        print("Current: ", current.value)
        
        for v in current.adjacents:
            if not visited.get(v, False):
                v.dfs_rec(v, end, visited)
        return None

    
    def bfs(self, vertex: type[WeightedVertex], target):
        """ 
        breadth first search 

        Args:
            vertex: startering vertex
            target: target value to search for
        """
        visited = {}
        queue = []
        
        queue.append(vertex)

        while len(queue) > 0:
            current = queue[0]
            del queue[0]
            
            if current.value == target:
                return current
            
            if not visited.get(current, False):               
                visited[current] = True
                print(current.value)
        
                for v in current.adjacents:
                    queue.append(v)
        return None
    
    def __repr__(self):
        return self.value

    def __lt__(self, vertex):
        return self.value < vertex.value

class AdjacencyListWeightedGraph:
    """ 
    A weighted adjacency list vertex implementation in Python
    (allows either directed or undirected representation)
    """
    def __init__(self):
        #: hash table of vertices in graph
        self._adjacents = {}
        
    def add_adjacent_vertex(self, start: str, end: str, weight):
        """ 
        Add an undirected vertex to the adjacency list (same as add_edge()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
            weight: edge weight
        """
        self.add_directed_adjacent_vertex(start, end, weight)
        if end not in self._adjacents:
            self._adjacents[end] = {}
        self._adjacents[end][start] = weight
        
    def add_edge(self, start: str, end: str, weight):
        """ 
        Add an undirected vertex to the adjacency list (same as add_adjacent_vertex()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
            weight: edge weight
        """
        self.add_adjacent_vertex(start, end, weight)

    def add_directed_edge(self, start: str, end: str, weight):
        """ 
        Add a directed vertex to the adjacency list (same as add_directed_adjacent_vertex()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
            weight: edge weight
        """
        self.add_directed_adjacent_vertex(start, end, weight)
        
    def add_directed_adjacent_vertex(self, start: str, end: str, weight):
        """ 
        Add a directed vertex to the adjacency list (same as add_directed_edge()).

        Args:
            start: starting vertex label 
            end: ending vertex label 
            weight: edge weight
        """
        if start not in self._adjacents:
            self._adjacents[start] = {}
            
        self._adjacents[start][end] = weight
        if end not in self._adjacents:
            self._adjacents[end] = {}

    def adjacents(self, vertex: str):
        return self._adjacents[vertex]

    def df_traverse(self):
        """
        Perform depth first traversal.
        """
        return self._df_traverse_rec(self, dict())

    def _df_traverse_rec(self, vertex: type[Vertex], visited={}):
        """
        helper depth first traversal recursive function
        """
        visited[vertex] = True
        print(vertex.value)
        
        for v in vertex.adjacents:
            if not visited.get(v, False):
                v._df_traverse_rec(v, visited)
            
    def bf_traverse(self):
        """
        Perform breadth first traversal.
        """
        start = self
        visited = {}
        queue = []
        
        queue.append(start)

        while len(queue) > 0:
            current = queue[0]
            del queue[0]
            
            if not visited.get(current, False):               
                visited[current] = True
                print(current.value)
        
                for v in current.adjacents:
                    queue.append(v)
        
    def dfs(self, start, end):
        """ 
        Recursive depth first search.

        Args:
            start: beginning vertex
            end: vertex to search for
        Returns:
        Vertex in the graph
        None if not found.
        """
        return self.dfs_rec(start, end, dict())
        
    def dfs_rec(self, current, end, visited=None):
        """
        helper depth first search recursive function

        Returns:
        Vertex in the graph
        None if not found.
        """
        if current == end:
            print("Found: ", end.value)
            return current

        visited[current] = True
        print(current)
        
        for v in self.adjacents(current):
            if not visited.get(v, False):
                return v.dfs_rec(v, end, visited)
        return None
    
    def bfs(self, end):
        """ 
        Recursive breadth first search.

        Args:
            end: vertex to search for
        Returns:
        Vertex in the graph
        None if not found.
        """
        visited = {}
        queue = []
        start = self
        
        visited[start] = True
        queue.append(start)

        while len(queue) > 0:
            current = queue[0]
            del queue[0]
            print(current.value)
            # print("Visited: ", visited)
            # print("Queue: ", queue)
            
            if current.value == end.value:
                return current
            
            for v in current.adjacents:
                if not visited.get(v, False):               
                    visited[v] = True
                    queue.append(v)
        
        return None

    def __getitem__(self, vertex: str):
        return self._adjacents[vertex]

    def __len__(self):
        return len(self._adjacents)

    def edges(self):
        """ 
        Return a list of edges in the graph. Each edge is represented by a tuple (start, end, weight)
        """
        edges = []
        for start in self._adjacents.keys():
            for end in self.adjacents(start):
                weight = self[start][end]
                if start != end:  
                    edges.append((start, end, weight))
        return edges


#### Dijkstra's Algorithm Functions
def shortest_path(graph, start: str, end: str, debug=False):
    """ 
    Helper function that returns a weight table and a previous vertex table using Dijkstra's Algorithm.

    Args:
        graph: adjacency list graph
        start: starting vertex
        end: ending vertex
        debug: if True, display weight table as it is being built
    
    Returns:
    a tuple of a weight table dictionary and a previous path dictionary
    """
    weight_table = {}
    previous = {}
    visited = set()
    h = MinHeap()

    current = start
    h.insert(current)
    weight_table[current] = 0
    previous[current] = current
    
    while not h.is_empty():
        current_weight = weight_table.get(current, float('inf'))
        visited.add(current)

        for adjacent in graph[current]:
            weight = graph[current][adjacent]
            if adjacent not in visited:
                h.insert(adjacent)

            wt = weight_table.get(adjacent, float('inf'))
            if wt > weight + current_weight:
                weight_table[adjacent] = weight + current_weight
                previous[adjacent] = current
                if debug:
                    print(weight_table)

        current = h.pop()

    return weight_table, previous

def find_path(graph, start: str, end: str, debug=False):
    """ 
    Return the shortest path of two vertices using Dijkstra's Algorithm.

    Args:
        graph: graph object (adjacency list)
        start: starting vertex
        end: ending vertex
        debug: if True, display the weight table 

    Returns:
    A list of vertices that form a shortest path
    """
    weight_table, previous = shortest_path(graph, start, end, debug)
    path = []

    current = end
    path.append(current)
    while current != start:
        current = previous[current]
        path.append(current)
        
    path.reverse()

    if debug:
        print("previous table")
        print(previous)

        print("weight table")
        print(weight_table)
        print("price ", weight_table[end])
    return path


