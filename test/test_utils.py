import unittest
import argparse
from schema_entry.utils import get_parent_tree, parse_value_string_by_schema, parse_schema_as_cmd
from schema_entry.entrypoint import EntryPoint


def setUpModule() -> None:
    print("[SetUp Submodule schema_entry.utils test]")


def tearDownModule() -> None:
    print("[TearDown Submodule schema_entry.utils test]")


class GetParentTreeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp GetParentTree test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown GetParentTree test context")

    def test_get_parent_tree(self) -> None:
        class A(EntryPoint):
            pass

        class B(EntryPoint):
            pass

        class C(EntryPoint):
            pass
        a = A()
        c = a.regist_sub(B).regist_sub(C)

        assert get_parent_tree(c) == ["a", "b"]


class ParseValueStringBySchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp ParseValueStringBySchema test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown ParseValueStringBySchema test context")

    def test_parse_int(self) -> None:
        schema = {
            "type": "integer"
        }
        assert parse_value_string_by_schema(schema, "10") == 10

    def test_parse_float(self) -> None:
        schema = {
            "type": "number"
        }
        assert parse_value_string_by_schema(schema, "10.1") == 10.1

    def test_parse_string(self) -> None:
        schema = {
            "type": "string"
        }
        assert parse_value_string_by_schema(schema, "10a") == "10a"

    def test_parse_bool(self) -> None:
        schema = {
            "type": "boolean"
        }
        assert parse_value_string_by_schema(schema, "true") is True

    def test_parse_array_int(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "type": "integer"
            }
        }
        self.assertListEqual(parse_value_string_by_schema(schema, "10,3,4,2"), [10, 3, 4, 2])

    def test_parse_array_float(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "type": "number"
            }
        }
        self.assertListEqual(parse_value_string_by_schema(schema, "10.1,3.2,4.3,2.3"), [10.1, 3.2, 4.3, 2.3])

    def test_parse_array_str(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
        self.assertListEqual(parse_value_string_by_schema(schema, "a,b,c,d"), ["a", "b", "c", "d"])


class ParseSchemaAsCMDTest(unittest.TestCase):
    parser: argparse.ArgumentParser

    @classmethod
    def setUpClass(cls) -> None:
        print("setUp ParseSchemaAsCMD test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown ParseSchemaAsCMD test context")

    def setUp(self) -> None:
        self.parser = argparse.ArgumentParser()
        print("case self.parser setUp")

    def test_parse_int(self) -> None:
        schema = {
            "type": "integer"
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args(["--test-a", "10"])
        self.assertDictEqual(vars(args), {"test_a": 10})

    def test_parse_float(self) -> None:
        schema = {
            "type": "number"
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args(["--test-a", "10.1"])
        self.assertDictEqual(vars(args), {"test_a": 10.1})

    def test_parse_string(self) -> None:
        schema = {
            "type": "string"
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args(["--test-a", "10a"])
        self.assertDictEqual(vars(args), {"test_a": "10a"})

    def test_parse_bool_true(self) -> None:
        schema = {
            "type": "boolean"
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args(["--test-a"])
        self.assertDictEqual(vars(args), {"test_a": True})

    def test_parse_bool_false(self) -> None:
        schema = {
            "type": "boolean"
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args([])
        self.assertDictEqual(vars(args), {"test_a": False})

    def test_parse_array_int(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "type": "integer"
            }
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args(["--test-a=1", "--test-a=2", "--test-a=3"])
        self.assertDictEqual(vars(args), {"test_a": [1, 2, 3]})

    def test_parse_array_float(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "type": "number"
            }
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args(["--test-a=1.1", "--test-a=2.2", "--test-a=3.3"])
        self.assertDictEqual(vars(args), {"test_a": [1.1, 2.2, 3.3]})

    def test_parse_array_str(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser)
        args = p.parse_args(["--test-a=1.1", "--test-a=2.2", "--test-a=3.3"])
        self.assertDictEqual(vars(args), {"test_a": ["1.1", "2.2", "3.3"]})

    def test_parse_noflag(self) -> None:
        schema = {
            "type": "string"
        }
        p = parse_schema_as_cmd(key="test_a", schema=schema, parser=self.parser, noflag=True)
        args = p.parse_args(["noflag"])
        self.assertDictEqual(vars(args), {"test_a": "noflag"})
