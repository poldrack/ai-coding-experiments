# generate a python class to represent a directed graph. generate a function that takes in a directed graph and a two sets of vertices and and returns whether those two sets are d-separated.
# add a test that compares the results from this code to the d-separation results computed using the NetworkX library

from collections import deque
import networkx as nx
from networkx.algorithms.d_separation import d_separated


class DirectedGraph:
    def __init__(self):
        self.graph = {}

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []

    def add_edge(self, from_vertex, to_vertex):
        if from_vertex in self.graph and to_vertex in self.graph:
            self.graph[from_vertex].append(to_vertex)
        else:
            raise ValueError("One or both vertices not found in the graph")

    def remove_vertex(self, vertex):
        if vertex in self.graph:
            del self.graph[vertex]
            for v in self.graph:
                if vertex in self.graph[v]:
                    self.graph[v].remove(vertex)
        else:
            raise ValueError("Vertex not found in the graph")

    def remove_edge(self, from_vertex, to_vertex):
        if from_vertex in self.graph and to_vertex in self.graph:
            if to_vertex in self.graph[from_vertex]:
                self.graph[from_vertex].remove(to_vertex)
            else:
                raise ValueError("Edge not found in the graph")
        else:
            raise ValueError("One or both vertices not found in the graph")

    def get_neighbors(self, vertex):
        if vertex in self.graph:
            return self.graph[vertex]
        else:
            raise ValueError("Vertex not found in the graph")

    def __repr__(self):
        return str(self.graph)



def is_d_separated(graph, set1, set2, conditioning_set):
    def is_head_to_head(node1, node2, node3):
        return node1 in graph.get_neighbors(node2) and node3 in graph.get_neighbors(node2)

    def is_tail_to_tail(node1, node2, node3):
        return node2 in graph.get_neighbors(node1) and node2 in graph.get_neighbors(node3)

    def is_active_triplet(node1, node2, node3):
        return (is_tail_to_tail(node1, node2, node3) or
                (is_head_to_head(node1, node2, node3) and node2 not in conditioning_set) or
                (node2 in conditioning_set and not is_head_to_head(node1, node2, node3)))

    def is_path_active(path):
        for i in range(len(path) - 2):
            if not is_active_triplet(path[i], path[i + 1], path[i + 2]):
                return False
        return True

    def find_all_paths(graph, start, end, visited, path):
        visited[start] = True
        path.append(start)

        if start == end:
            if is_path_active(path):
                return True
        else:
            for neighbor in graph.get_neighbors(start):
                if not visited[neighbor]:
                    if find_all_paths(graph, neighbor, end, visited, path):
                        return True

        path.pop()
        visited[start] = False
        return False

    for vertex in conditioning_set:
        if vertex not in graph.graph:
            raise ValueError("One or more vertices in the conditioning set are not in the graph")

    for v1 in set1:
        if v1 not in graph.graph:
            raise ValueError("One or more vertices in set1 are not in the graph")
        for v2 in set2:
            if v2 not in graph.graph:
                raise ValueError("One or more vertices in set2 are not in the graph")

            visited = {v: False for v in graph.graph}
            if find_all_paths(graph, v1, v2, visited, []):
                return False

    return True


# Example usage
if __name__ == "__main__":
    dg = DirectedGraph()
    dg.add_vertex("A")
    dg.add_vertex("B")
    dg.add_vertex("C")

    dg.add_edge("A", "B")
    dg.add_edge("A", "C")
    dg.add_edge("B", "C")

    print(dg)  # Output: {'A': ['B', 'C'], 'B': ['C'], 'C': []}

    dg.remove_edge("A", "B")
    print(dg)  # Output: {'A': ['C'], 'B': ['C'], 'C': []}

    print(is_d_separated(dg, {"A"}, {"B"}, {"C"}))  # Output: True

    dg.remove_vertex("C")
    print(dg)  # Output: {'A': [], 'B': []}


    # Create a directed graph using the custom DirectedGraph class
    custom_graph = DirectedGraph()
    custom_graph.add_vertex("A")
    custom_graph.add_vertex("B")
    custom_graph.add_vertex("C")
    custom_graph.add_vertex("D")
    custom_graph.add_edge("A", "B")
    custom_graph.add_edge("B", "C")
    custom_graph.add_edge("C", "D")

    # Create an equivalent directed graph using NetworkX
    nx_graph = nx.DiGraph()
    nx_graph.add_edge("A", "B")
    nx_graph.add_edge("B", "C")
    nx_graph.add_edge("C", "D")

    # Test sets of vertices for d-separation
    set1 = {"A"}
    set2 = {"D"}
    conditioning_set = {"C"}

    # Check d-separation using the custom function
    custom_result = is_d_separated(custom_graph, set1, set2, conditioning_set)

    # Check d-separation using the NetworkX function
    nx_result = d_separated(nx_graph, set1, set2, conditioning_set)

    assert custom_result == nx_result, "Results from the custom function and NetworkX do not match"
    print("Results match!")
