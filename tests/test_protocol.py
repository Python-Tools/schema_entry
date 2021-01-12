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
                    "items": {
                        "type": "number"
                    }
                },
                "b": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "c": {
                    "type": "array",
                    "items": {
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
                    "items": {
                        "type": "boolean"
                    }
                }
            }
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            validate(target, SUPPORT_SCHEMA)

    def test_array_enum(self) -> None:
        target = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "a": {
                    "type": "array",
                    "items": {
                        "type": "number",
                        "enum": [1.1, 2.2, 4.0]
                    }
                },
                "b": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["1.1", "2.2", "4.0"]
                    }
                },
                "c": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "enum": [1, 2, 4]
                    }
                }
            }
        }
        assert validate(target, SUPPORT_SCHEMA) is None
