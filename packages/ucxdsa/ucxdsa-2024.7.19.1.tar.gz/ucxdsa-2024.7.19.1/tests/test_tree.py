import unittest

from dsa.tree import Tree

class TestTree(unittest.TestCase):
    def test_create(self):
        t = Tree()

    def test_insert(self):
        t = Tree()

        t.insert(20)
        t.insert(30)
        t.insert(10)
        t.insert(5)
        t.insert(40)
        t.insert(2)
        t.insert(35)
        t.insert(7)

        t.print()

        self.assertIsNotNone(t.search(20))
        self.assertIsNotNone(t.search(7))
        self.assertIsNotNone(t.search(5))
        self.assertIsNotNone(t.search(40))

        self.assertIsNone(t.search(0))
        self.assertIsNone(t.search(60))
        self.assertIsNone(t.search(-1))

        t.delete(20)
        self.assertIsNone(t.search(20))
        t.delete(20)
        self.assertIsNone(t.search(20))
