import unittest


def test():
    loader = unittest.TestLoader()
    suite = loader.discover('.')

    unittest.TextTestRunner().run(suite)
