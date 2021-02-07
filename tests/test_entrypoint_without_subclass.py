import os
import json
import unittest
from pathlib import Path
from typing import Dict, Any
import jsonschema.exceptions

from schema_entry.entrypoint import EntryPoint


def setUpModule() -> None:
    print("[SetUp Submodule schema_entry.entrypoint test]")


def tearDownModule() -> None:
    print("[TearDown Submodule schema_entry.entrypoint test]")


class CMDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp CMDTest test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown CMDTest test context")

    def test_set_name_when_init(self) -> None:
        root = EntryPoint(name="test_a")
        assert root.name == "test_a"

    def test_default_entry_usage(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number",
                        "default": 33.3
                    }
                },
                "required": ["a_a"]
            },
            main=lambda **kwargs: None)
        root([])
        assert root.usage == "test_a [options]"

    def test_default_subcmd_usage(self) -> None:
        root = EntryPoint(name="a")
        root.regist_sub(
            EntryPoint,
            name="b",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "default": 1
                    }
                },
                "required": ["a"]
            },
            main=lambda **kwargs: None)
        root(["b"])
        assert root.usage == "a [subcmd]"

    def test_subcmd(self) -> None:
        root = EntryPoint(name="a")
        a_b_c = root.regist_sub(
            EntryPoint,
            name="b").regist_sub(
                EntryPoint,
                name="c",
                schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "integer"
                        }
                    },
                    "required": ["a"]
                }, main=lambda a: None)

        os.environ['A_B_C_A'] = "2"
        root(["b", "c"])
        self.assertDictEqual(a_b_c.config, {
            "a": 2
        })


class LoadConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp LoadConfigTest test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown LoadConfigTest test context")

    def test_load_default_config(self) -> None:
        root = EntryPoint(
            name="a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number",
                        "default": 33.3
                    }
                },
                "required": ["a_a"]
            },
            main=lambda a_a: None
        )
        root([])
        self.assertDictEqual(root.config, {
            "a_a": 33.3
        })

    def test_load_json_configfile(self) -> None:
        root = EntryPoint(
            name="test_a",
            default_config_file_paths=[
                "/test_config.json",
                str(Path.home().joinpath(".test_config.json")),
                "./test_config.json"
            ],
            main=lambda a: None)
        root([])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_json_configfile_onlyneed(self) -> None:
        root = EntryPoint(
            name="test_a_onlyneed",
            default_config_file_paths=[
                "/test_config1.json",
                str(Path.home().joinpath(".test_config1.json")),
                "./test_config1.json"
            ],
            config_file_only_get_need=True,
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number"
                    }
                },
                "required": ["a"]
            },
            main=lambda a: None
        )
        root([])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_yaml_configfile(self) -> None:
        root = EntryPoint(
            name="test_a",
            default_config_file_paths=[
                "/test_config.yml",
                str(Path.home().joinpath(".test_config.yml")),
                "./test_config.yml"
            ],
            main=lambda a: None
        )

        root([])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_json_configfile_cmd(self) -> None:
        root = EntryPoint(
            name="test_ac",
            verify_schema=False,
            main=lambda a: None
        )

        root(["-c", "test_config.json"])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_all_configfile(self) -> None:
        def _(a: int, b: int, c: int, d: int) -> None:
            assert a == 1
            assert b == 2
            assert c == 13
            assert d == 43
        root = EntryPoint(
            name="test_ac",
            load_all_config_file=True,
            default_config_file_paths=[
                "./test_config.json",
                "./test_config1.json",
                "./test_config2.json"
            ],
            main=_
        )
        root([])

    def test_load_configfile_with_custom_parser_in_class(self) -> None:
        def test_other_config2_parser(p: Path) -> Dict[str, Any]:
            with open(p) as f:
                temp = json.load(f)
            return {k.lower(): v for k, v in temp.items()}

        def _2(a: int, b: int, c: int, d: int) -> None:
            assert a == 1
            assert b == 2
            assert c == 13
            assert d == 43

        root = EntryPoint(
            name="test_ac",
            load_all_config_file=True,
            default_config_file_paths=[
                "./test_config.json",
                "./test_config1.json",
                "./test_other_config2.json"
            ],
            config_file_parser_map={
                "test_other_config2.json": test_other_config2_parser
            },
            main=_2)

        root([])

    def test_load_ENV_config(self) -> None:
        root = EntryPoint(
            name="test_a",
            env_prefix="app",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number"
                    }
                },
                "required": ["a_a"]
            },
            main=lambda a_a: None
        )

        os.environ['APP_A_A'] = "123.1"
        root([])
        self.assertDictEqual(root.config, {
            "a_a": 123.1
        })

    def test_schema_check(self) -> None:
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            EntryPoint(name="test_a", schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a-a": {
                        "type": "number"
                    }
                },
                "required": ["a-a"]
            })

    def test_load_cmd_config(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number"
                    }
                },
                "required": ["a_a"]
            },
            main=lambda a_a: None
        )

        root(["--a-a=321.5"])
        self.assertDictEqual(root.config, {
            "a_a": 321.5
        })

    def test_load_short_cmd_config(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                 "$schema": "http://json-schema.org/draft-07/schema#",
                 "type": "object",
                 "properties": {
                     "a_a": {
                         "type": "number",
                         "title": "a"
                     }
                 },
                "required": ["a_a"]
            },
            main=lambda a_a: None
        )
        root(["-a", "321.5"])
        self.assertDictEqual(root.config, {
            "a_a": 321.5
        })

    def test_load_not_required_boolean_cmd_config(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "boolean",
                        "default": True
                    }
                }
                # "required": ["a_a"]
            },
            main=lambda a_a: None
        )
        root([])
        self.assertDictEqual(root.config, {
            "a_a": True
        })

    def test_load_not_required_boolean_cmd_config2(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "boolean",
                        "default": True
                    },
                    "b_b": {
                        "type": "string",
                        "default": "1234"
                    }
                },
                "required": ["b_b"]
            },
            main=lambda a_a, b_b: None
        )
        root([])
        self.assertDictEqual(root.config, {
            "a_a": True,
            "b_b": "1234"
        })

    def test_load_not_required_boolean_cmd_config3(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "boolean",
                        "default": True
                    },
                    "b_b": {
                        "type": "string",
                        "default": "1234"
                    }
                },
                "required": ["a_a"]
            },
            main=lambda a_a, b_b: None
        )
        root([])
        self.assertDictEqual(root.config, {
            "a_a": False,
            "b_b": "1234"
        })

    def test_load_cmd_noflag_config(self) -> None:
        root = EntryPoint(
            name="test_a",
            default_config_file_paths=[
                "/test_config.json",
                str(Path.home().joinpath(".test_config.json")),
                "./test_config.json"
            ],
            argparse_noflag="a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number"
                    }
                },
                "required": ["a"]
            },
            main=lambda a: None
        )
        root(["321.5"])
        self.assertDictEqual(root.config, {
            "a": 321.5
        })

    def test_load_config_order1(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer"
                    }
                },
                "required": ["a"]
            },
            main=lambda a: None
        )
        os.environ['TEST_A_A'] = "2"
        root(["--a=3"])
        self.assertDictEqual(root.config, {
            "a": 3
        })

    def test_load_config_order2(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer"
                    }
                },
                "required": ["a"]
            },
            main=lambda a: None
        )
        root(["--a=3"])
        self.assertDictEqual(root.config, {
            "a": 3
        })

    def test_load_config_order3(self) -> None:
        root = EntryPoint(
            name="test_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer"
                    }
                },
                "required": ["a"]
            },
            main=lambda a: None
        )
        os.environ['TEST_A_A'] = "2"
        root([])
        self.assertDictEqual(root.config, {
            "a": 2
        })

    def test_load_array_cmd_config(self) -> None:
        root = EntryPoint(
            name="test_a",
            argparse_noflag="a_a",
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["a_a"]
            },
            main=lambda a_a: None
        )
        root(["a", "b", "c"])
        self.assertDictEqual(root.config, {
            "a_a": ["a", "b", "c"]
        })
