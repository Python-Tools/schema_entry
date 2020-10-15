import sys
import unittest
from pathlib import Path

module_import_path = find_module_import_path(Path(__file__),"entry-tree","src")
print(module_import_path)
if module_import_path not in sys.path:
    sys.path.append(module_import_path)

from entry_tree import 

def setUpModule():
    print("[SetUp Submodule test]")


def tearDownModule():
    print("[TearDown Submodule test]")


class SubmoduletTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("setUp model test context")

    @classmethod
    def tearDownClass(cls):
        print("tearDown model test context")

    def setUp(self):
        print("instance setUp")

    def tearDown(self):
        print("instance tearDown")

    def test_show(self):
        print(show({"name":"new","type":"x"}))
        assert show({"name":"new","type":"x"}) == "x----new"


def submodule_suite():
    suite = unittest.TestSuite()
    suite.addTest(SubmoduletTest("test_show"))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = submodule_suite()
    runner.run(test_suite)