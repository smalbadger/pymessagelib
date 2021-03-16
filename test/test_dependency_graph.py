import unittest
from pymessagelib import DependencyGraph


class TestDependencyGraph(unittest.TestCase):
    def setUp(self):
        self.graph = DependencyGraph()

    def testAddingEdges(self):
        self.graph.addEdge(1, 2)
        self.graph.addEdge(2, 3)

    def testCyclic(self):
        self.graph.addEdge("hello", "world")
        self.graph.addEdge("world", "cool")
        self.graph.addEdge("cool", "hello")
        self.assertTrue(self.graph.isCyclic())

    def testCycle(self):
        self.graph.addEdge("hello", "world")
        self.graph.addEdge("world", "cool")
        self.graph.addEdge("cool", "hello")
        self.assertEqual(self.graph.cycle, ["hello", "world", "cool"])

    def testNotCyclic(self):
        self.graph.addEdge("hello", "world")
        self.graph.addEdge("world", "cool")
        self.assertFalse(self.graph.isCyclic())

    def testNumVertices(self):
        self.assertEqual(self.graph.num_vertices, 0)
        self.graph.addEdge("hello", "world")
        self.assertEqual(self.graph.num_vertices, 2)
        self.graph.addEdge("world", "cool")
        self.assertEqual(self.graph.num_vertices, 3)
        self.graph.addEdge("cool", "hello")
        self.assertEqual(self.graph.num_vertices, 3)
