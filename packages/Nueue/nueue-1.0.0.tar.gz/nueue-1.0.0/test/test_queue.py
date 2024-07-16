import unittest

from Nueue.queue import Queue


class TestQueueStress(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        for i in range(1, 1000001):
            self.queue.add(f"Song {i}")

    def test_extreme_operations(self):
        for i in range(10000):
            if i % 2 == 0:
                self.assertIsNotNone(self.queue.next())
            else:
                self.assertIsNotNone(self.queue.previous())

        for _ in range(999999):
            self.queue.next()
        self.assertEqual(self.queue.current_item(), "Song 1000000")

        for _ in range(999999):
            self.queue.previous()
        self.assertEqual(self.queue.current_item(), "Song 1")

        for i in range(10000):
            if i % 2 == 0:
                self.assertIsNotNone(self.queue.next())
            else:
                self.assertIsNotNone(self.queue.previous())

        self.assertIsNotNone(self.queue.source())
        if self.queue.now > 0:
            self.assertIsNotNone(self.queue.source(previous=True))

        self.queue.clear()
        self.assertTrue(self.queue.is_empty())
        self.assertIsNone(self.queue.current_item())
        self.assertIsNone(self.queue.next())
        self.assertIsNone(self.queue.previous())
        self.assertIsNone(self.queue.source())
        self.assertIsNone(self.queue.source(previous=True))


if __name__ == "__main__":
    unittest.main(argv=[""], exit=False)
