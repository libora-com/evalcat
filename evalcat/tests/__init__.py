import os
import unittest


def test():
    test_dir = os.path.dirname(__file__)
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir)

    unittest.TextTestRunner().run(suite)
