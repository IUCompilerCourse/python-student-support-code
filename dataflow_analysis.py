from collections import deque
from graph import transpose
from functools import reduce
from utils import trace

def analyze_dataflow(G, transfer, bottom, join):
    trans_G = transpose(G)
    mapping = {}
    for v in G.vertices():
        mapping[v] = bottom
    worklist = deque()
    for v in G.vertices():
        worklist.append(v)
    while worklist:
        node = worklist.pop()
        input = reduce(join, [mapping[v] for v in trans_G.adjacent(node)], bottom)
        output = transfer(node, input)
        if output != mapping[node]:
            mapping[node] = output
            for v in G.adjacent(node):
                worklist.append(v)

