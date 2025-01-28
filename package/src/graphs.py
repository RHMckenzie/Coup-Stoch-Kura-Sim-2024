# a short set of python functions designed to produce Watts-Strogatz and Albert-Barabasi graphs

import numpy as np
import networkx as nx
import itertools as iter

# Helper function to replace link edges in Watts-Strogatz function
def _watts_strogatz_replace_helper(edge, rng, n, p, existing_edges, new_edges):
    if rng.random() < p:
        source, target = edge
        new_source = rng.integers(0, n)
        # Ensure no self-loops and no existing edges
        while new_source == target\
            or (new_source, target) in existing_edges \
            or (new_source, target) in new_edges:
            new_source = rng.integers(0, n)
        return (new_source, target)
    return edge
            

# Partially based upon: 
# https://networkx.org/documentation/stable/reference/generated/networkx.generators.random_graphs.watts_strogatz_graph.html#networkx.generators.random_graphs.watts_strogatz_graph
# Generates a directed watts_strogatz graph and returns a networkX DiGraph object
def watts_strogatz_directed(n, k, p, seed=None):
    rng = np.random.default_rng(seed = seed)
    #construct edge list
    edge_list = []
    for i in range(n):
        for j in range(1, k//2 + 1):
            edge_list.append((i, (i + j) % n))  # Forward neighbors
            edge_list.append((i, (i - j) % n))  # Backward neighbors
    #probabilistically remove edges:
    new_edges = []
    for edge in edge_list:
        new_edges.append(_watts_strogatz_replace_helper(edge, rng, n, p, edge_list, new_edges))
    if len(edge_list) == 0:
        return None
    G = nx.DiGraph(new_edges)
    return G


# Also based upon:
# https://networkx.org/documentation/stable/reference/generated/networkx.generators.random_graphs.connected_watts_strogatz_graph.html
# Rerolls the above watts_strogatz_directed generator to try to get weakly connected
def weak_connected_ws_directed(n, k, p, tries = 100, seed = None):
    for t in range(tries):
        if seed is not None:
            seed = seed + 1
        G = watts_strogatz_directed(n, k, p, seed = seed)
        if G is None:
            continue
        if nx.is_weakly_connected(G) and len(G.nodes) == n:
            return G
    return None

# Same as weakly connected but generates a strongly connected graph instead
def strong_connected_ws_directed(n, k, p, tries = 100, seed = None):
    for t in range(tries):
        if seed is not None:
            seed = seed + 1
        G = watts_strogatz_directed(n, k, p, seed = seed)
        if G is None:
            continue
        if nx.is_strongly_connected(G) and len(G.nodes) == n:
            return G
    return None

# normalise the columns of the matrix to produce a matrix with an in-degree of 1 (or 0 if there are no in-edges) for all nodes
# self coupling include
def in_degree_normalisation(G):
    G = G.copy()
    T = G.transpose()
    for i in range(T.shape[0]):
        if np.sum(T[i]) == 0:
            continue
        T[i] /= np.sum(T[i])
    return np.matrix(T.transpose())

#Sets the value of cross coupling for the graph
def cross_couple(G, c):
    c = np.clip(0, 1, c)
    c = 1 - c
    G = G.copy()
    G_c = np.eye(G.shape[0]) * c
    # rescale the graph
    G = (G * (1-c)) + G_c
    return G

