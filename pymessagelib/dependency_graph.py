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
    The DependencyGraph class is used for modeling field dependencies. Once the graph has been
    built, cycles can be detected and an optimal update sequence can be obtained.

    This is important because cycles in auto-update fields will result in unstable fields and/or
    infinite looping while updating. Fields that depend on each other need to be updated in the
    correct order to make sure they each end up with the correct values.
    """

    def __init__(self):
        """Constructs an empty DependencyGraph. Each edge must be added individually."""
        self.graph = defaultdict(list)
        self._cycle = None

    def addEdge(self, u, v):
        """Add an edge from node u to node v"""
        self.graph[u].append(v)
        if not v in self.graph:
            self.graph[v] = []

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        """
        Determine if there are any cycles in the graph. If there are return True. Else, return False.

        If a cycle is detected, a list of the nodes in the cycle is stored in self._cycle
        """

        def isCyclicUtil(v, visited, recStack):
            """Recursive portion of the cycle detection algorithm."""
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
        """If there is a cycle, return the list of nodes in the cycle."""
        if self.isCyclic():
            return self._cycle

    @property
    def num_vertices(self):
        """Return the number of vertices in the graph"""
        return len(self.graph)
