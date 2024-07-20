import unittest

from blank_project import __version__


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.3.0")
