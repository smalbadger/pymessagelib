"""
Created on Feb 24, 2021

This module contains the DependencyGraph class which is used by each Message to model
dependencies of auto-update fields.

This code was adapted from https://www.geeksforgeeks.org/detect-cycle-in-a-graph/

@author: smalb
"""

from collections import defaultdict


class DependencyGraph:
    """
    The DependencyGraph class is used for modeling field dependencies. After 
    """
    
    def __init__(self):
        self.graph = defaultdict(list)
        self._cycle = None

    def addEdge(self, u, v):
        self.graph[u].append(v)
        if not v in self.graph:
            self.graph[v] = []

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        def isCyclicUtil(v, visited, recStack):

            assert v in visited
            assert v in recStack

            # Mark current node as visited and adds to recursion stack
            visited[v] = True
            recStack[v] = True

            # Recur for all neighbors if any neighbor is visited and in recStack then graph is cyclic
            for neighbor in self.graph[v]:
                if not visited[neighbor]:
                    if isCyclicUtil(neighbor, visited, recStack):
                        self._cycle = [node for node in recStack]
                        return True
                elif recStack[neighbor]:
                    return True

            # The node needs to be popped from recursion stack before function ends
            recStack[v] = False
            return False

        visited = {i: False for i in self.graph.keys()}
        recStack = {i: False for i in self.graph.keys()}
        for node in self.graph.keys():
            if not visited[node]:
                if isCyclicUtil(node, visited, recStack):
                    return True
        return False
    
    @property
    def cycle(self):
        if self.isCyclic():
            return self._cycle

    @property
    def num_vertices(self):
        return len(self.graph)