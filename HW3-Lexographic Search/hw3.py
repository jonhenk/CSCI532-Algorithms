# -*- coding: utf-8 -*-
"""HW3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cs3xreTvHgbJGHzeichyavc_wNP1NRUR
"""

from copy import copy
import heapq
from collections import defaultdict
import io
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
import random

def genflow(n):

  num_edges = n * (n - 1) // 4  # Maximum number of edges for an undirected graph

  # Generate random edge capacities between 1 and 1000
  capacities = [random.randint(1, 1000) for _ in range(num_edges)]

  # Generate random edges
  edges = set()
  while len(edges) < num_edges:
      u = random.randint(0, n - 1)
      v = random.randint(0, n - 1)
      if u != v:
          edges.add((u, v))

  # Write the flow network in the required format
  output = f"{n}\n"
  for i, (u, v) in enumerate(edges):
      capacity = capacities[i]
      output += f"{u} {v} {capacity}\n"

  print(output)

class FlowNetwork:
    def __init__(self):
        # use default dictionary so all values have a default value to avoid key errors
        self.adj = defaultdict(list)
        self.flow = defaultdict(int)
        self.flowcopy = self.flow.copy()
        self.capacity = defaultdict(int)

    def add_edge(self, u, v, cap):

        # add the connection from u to v and v to u into adjacent li
        self.adj[u].append(v)
        self.adj[v].append(u)
        self.capacity[(u, v)] = cap

    def get_nodes(self):
        nodes = set(self.adj.keys())
        return nodes

    def get_edges(self):
        edges = set()
        for u, neighbors in self.adj.items():
            for v in neighbors:
                # Use a tuple of sorted nodes (u, v) to avoid duplicates
                edge = tuple(sorted((u, v)))
                edges.add(edge)
        return edges

    def lexicographic_bfs(self, source, sink):
        #initializing and empty set 'visited' and q is the priority queue
        q = [(source, [])]
        visited = set()

        while q:
            # gets the smallest element (in lexicographic order) from the priority queue
            node, path = heapq.heappop(q)

            # checks if sink/destination if is returns augmented path
            if node == sink:
                return path

            # if node already visted skip it
            if node in visited:
                continue
            # add to current set of visted nodes
            visited.add(node)

            # iterates through the neighbors of current node (in lexographic order) and adds to q
            # if resid capacity along the edge > 0 and not visited

            for neighbor in sorted(self.adj[node]):
                residual_flow = self.capacity[(node, neighbor)] - self.flow[(node, neighbor)]

                if residual_flow > 0 and neighbor not in visited:
                    heapq.heappush(q, (neighbor, path + [(node, neighbor)]))

        return None

    def bfs(self, source, sink):
        q = deque([source]) #initialize queue with source node
        visited = set() #set to keep track of visited nodes
        path = {} #dictionary to store the augmented path

        while q:
            #get first node in queue
            node = q.popleft()

            #if we have reached the sink node, we have found an augmenting path
            if node == sink:
                break

            # mark the current node as visited
            visited.add(node)

            #iterates though adjacent nodes and cacluated residual cap
            for neighbor in self.adj[node]:
                residual = self.capacity[(node, neighbor)] - self.flow[(node, neighbor)]

                # if resid capacity along the edge > 0 and not visited
                # add node to queue
                if residual > 0 and neighbor not in visited:
                    path[neighbor] = node
                    q.append(neighbor)

        #if we don't find augmented path
        if sink not in path:
            return None

        #stores augmented path
        augment_path = []

        #start at sink and add each edge to get the augmented path
        node = sink
        while node != source:
            parent = path[node]
            augment_path.append((parent, node))
            node = parent

        #reverse path order and return
        augment_path.reverse()
        return augment_path

    def ford_fulkerson_lexicographic(self, source, sink):
        # defines the path from source to sink, sets max_flow to 0, num_aug_path to 0
        path = self.lexicographic_bfs(source, sink) # gets lexographically smallest augmented path
        max_flow = 0  # stores max flow for network
        num_augmented_paths = 0 # stores number of paths

        # while an augmenting path exists
        while path:
            # getting the smallest capacity remaining/ residual
            min_residual = min(self.capacity[u, v] - self.flow[u, v] for u, v in path)
            max_flow += min_residual
            num_augmented_paths += 1

            for u, v in path:
                self.flow[u, v] += min_residual

                self.flow[v, u] -= min_residual

            path = self.lexicographic_bfs(source, sink)

        print(f"Lexographic Ford-Fulkerson augmented paths: {num_augmented_paths}")
        print(f"Ford-Fulkerson max flow: {max_flow}")
        return max_flow

    def edmonds_karp(self, source, sink):
        max_flow = 0 # stores max flow for network
        num_augmented_paths = 0 # stores number of paths

        #finds the first shortest path from source to sink using bfs
        path = self.bfs(source, sink)

        while path:
            #finds min capacity of path and updates max_flow and num_augmented_paths
            path_flow = min(self.capacity[u, v] - self.flow[u, v] for u, v in path)
            max_flow += path_flow
            num_augmented_paths += 1

            #updates the flow network with the new flow and add it to the total max flow
            for u, v in path:
                self.flow[u, v] += path_flow
                self.flow[v, u] -= path_flow

            #finds the next shortest path using bfs
            path = self.bfs(source, sink)


        print(f"Edmonds Karp augmented paths: {num_augmented_paths}")
        print(f"Edmunds Karp max flow: {max_flow}")
        return max_flow

    def draw(self, size=500, labels=True):
        G = nx.DiGraph()
        G.add_nodes_from(self.get_nodes())
        G.add_edges_from(self.get_edges())
        nx.draw(G, with_labels=labels, node_size=size, node_color='lightblue', font_size=20)
        plt.show()

    def test(self, source, sink):
        self.ford_fulkerson_lexicographic(source, sink)
        self.flow = self.flowcopy.copy()
        self.edmonds_karp(source, sink)


def read_flow_network(input_data):
    lines = input_data.strip().split('\n')
    num = int(lines[0])


    network = FlowNetwork()

    for line in lines[1:]:
        u, v, cap = map(int, line.strip().split())
        network.add_edge(u, v, cap)

    return network

input_file = '''20
0 1 12
0 2 10
1 3 9
1 4 8
2 5 5
2 6 6
3 7 5
3 8 9
4 9 4
4 10 5
5 11 7
5 12 8
6 13 5
6 14 6
7 15 3
7 16 6
8 17 7
8 18 8
9 19 7
10 19 6
11 12 3
11 13 4
12 14 4
13 15 2
14 16 2
15 17 4
16 18 5
17 19 6
18 19 8
'''


flow_network = read_flow_network(input_file)
flow_network.draw()
flow_network.test(0, 19)

#is input file for 100 nodes
input2 = '''100
0 16 23
16 23 91
23 27 85
27 57 27
57 81 37
81 19 45
19 96 13
96 65 98
65 50 68
50 88 12
88 80 81
80 54 45
54 3 70
3 85 28
85 58 71
58 25 89
25 78 68
78 1 84
1 24 59
24 20 29
20 18 9
18 70 6
70 51 75
51 67 92
67 49 18
49 76 20
76 21 82
21 79 85
79 31 12
31 97 29
97 2 30
2 32 46
32 43 62
43 68 25
68 99 58
99 60 89
60 13 83
13 5 54
5 71 90
71 77 35
77 64 63
64 87 16
87 98 36
98 52 27
52 8 23
8 91 91
91 45 4
45 28 15
28 44 95
44 48 94
48 11 62
11 55 73
55 74 57
74 34 30
34 10 56
10 39 99
39 17 98
17 94 86
94 66 48
66 41 1
41 47 38
47 72 32
72 22 70
22 14 61
14 37 56
37 95 41
95 53 24
53 61 87
61 42 79
42 75 2
75 9 72
9 40 17
40 69 70
69 33 87
33 63 34
63 83 21
83 4 5
4 26 40
26 36 33
36 46 52
46 7 46
7 90 19
90 50 53
50 12 48
12 59 74
59 73 22
73 6 80
6 15 65
15 92 52
92 77 89
77 84 10
84 30 61
30 21 44
21 67 81
67 18 96
18 64 45
64 50 33
50 9 57
9 28 56
28 20 24
20 37 18
37 26 86
26 40 9
40 45 11
45 58 69
58 51 39
51 63 97
63 38 65
38 35 77
35 31 92
31 43 15
43 80 63
80 46 23
46 54 6
54 16 55
16 27 89
27 81 3
81 79 37
79 76 98
76 8 4
8 2 32
2 94 35
94 66 52
66 62 38
62 99 76
'''
flow_network = read_flow_network(input2)
flow_network.draw(size=100, labels=False)
flow_network.test(0, 99)
#max flow = 23