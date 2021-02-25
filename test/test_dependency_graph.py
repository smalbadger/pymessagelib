import unittest
from dependency_graph import DependencyGraph


class TestDependencyGraph(unittest.TestCase):
    def setUp(self):
        self.graph = DependencyGraph(3)

    def testAddingEdges(self):
        self.graph.addEdge(1, 2)
        self.graph.addEdge(2, 3)
        
    def testCyclic(self):
        self.graph.addEdge("hello", "world")
        self.graph.addEdge("world", "cool")
        self.graph.addEdge("cool", "hello")
        self.assertTrue(self.graph.isCyclic())
        self.assertEqual(self.graph.cycle, ["hello", "world", "cool"])

    def testNotCyclic(self):
        self.graph.addEdge("hello", "world")
        self.graph.addEdge("world", "cool")
        self.assertFalse(self.graph.isCyclic())
