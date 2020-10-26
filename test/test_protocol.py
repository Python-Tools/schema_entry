import unittest
import jsonschema
from jsonschema import validate

from schema_entry.protocol import SUPPORT_SCHEMA


def setUpModule() -> None:
    print("[SetUp Submodule schema_entry.protocol test]")


def tearDownModule() -> None:
    print("[TearDown Submodule schema_entry.protocol test]")


class ProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp SUPPORT_SCHEMA test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown SUPPORT_SCHEMA test context")

    def setUp(self) -> None:
        print("case setUp")

    def tearDown(self) -> None:
        print("case tearDown")

    def test_base_type(self) -> None:
        target = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "a": {
                    "type": "string"
                },
                "b": {
                    "type": "number"
                },
                "c": {
                    "type": "boolean"
                },
                "d": {
                    "type": "integer"
                }
            }
        }
        assert validate(target, SUPPORT_SCHEMA) is None

    def test_array_type(self) -> None:
        target = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "a": {
                    "type": "array",
                    "item": {
                        "type": "number"
                    }
                },
                "b": {
                    "type": "array",
                    "item": {
                        "type": "string"
                    }
                },
                "c": {
                    "type": "array",
                    "item": {
                        "type": "integer"
                    }
                }
            }
        }
        assert validate(target, SUPPORT_SCHEMA) is None

    def test_array_boolean(self) -> None:
        target = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "a": {
                    "type": "array",
                    "item": {
                        "type": "boolean"
                    }
                }
            }
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            validate(target, SUPPORT_SCHEMA)
