import os
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
        print("setUp GetParentTree test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown GetParentTree test context")

    def test_default_name(self) -> None:
        class Test_A(EntryPoint):
            pass
        root = Test_A()
        assert root.name == "test_a"

    def test_setting_name(self) -> None:
        class Test_A(EntryPoint):
            _name = "test_b"

        root = Test_A()
        assert root.name == "test_b"

    def test_default_entry_usage(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number",
                        "default": 33.3
                    }
                },
                "required": ["a_a"]
            }
        root = Test_A()

        @root.as_main
        def _(a_a: float) -> None:
            pass

        root([])

        assert root.usage == "test_a [options]"

    def test_default_subcmd_usage(self) -> None:
        class A(EntryPoint):
            pass

        class B(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "default": 1
                    }
                },
                "required": ["a"]
            }
        root = A()
        a_b = root.regist_sub(B)

        @a_b.as_main
        def _(a: int) -> None:
            pass
        root(["b"])

        assert root.usage == "a [subcmd]"

    def test_subcmd(self) -> None:
        class A(EntryPoint):
            pass

        class B(EntryPoint):
            pass

        class C(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer"
                    }
                },
                "required": ["a"]
            }
        root = A()
        a_b_c = root.regist_sub(B).regist_sub(C)

        @a_b_c.as_main
        def _(a: int) -> None:
            pass
        os.environ['A_B_C_A'] = "2"
        root(["b", "c"])
        self.assertDictEqual(a_b_c.config, {
            "a": 2
        })


class LoadConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp GetParentTree test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown GetParentTree test context")

    def test_load_default_config(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number",
                        "default": 33.3
                    }
                },
                "required": ["a_a"]
            }
        root = Test_A()

        @root.as_main
        def _(a_a: float) -> None:
            pass

        root([])
        self.assertDictEqual(root.config, {
            "a_a": 33.3
        })

    def test_load_json_configfile(self) -> None:
        class Test_A(EntryPoint):
            default_config_file_paths = [
                "/test_config.json",
                str(Path.home().joinpath(".test_config.json")),
                "./test_config.json"
            ]
        root = Test_A()

        @root.as_main
        def _(a: int) -> None:
            pass
        root([])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_yaml_configfile(self) -> None:
        class Test_A(EntryPoint):
            default_config_file_paths = [
                "/test_config.yml",
                str(Path.home().joinpath(".test_config.yml")),
                "./test_config.yml"
            ]
        root = Test_A()

        @root.as_main
        def _(a: int) -> None:
            pass
        root([])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_ENV_config(self) -> None:
        class Test_A(EntryPoint):
            env_prefix = "app"
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number"
                    }
                },
                "required": ["a_a"]
            }
        root = Test_A()

        @root.as_main
        def _(a_a: float) -> None:
            pass
        os.environ['APP_A_A'] = "123.1"
        root([])
        self.assertDictEqual(root.config, {
            "a_a": 123.1
        })

    def test_schema_check(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a-a": {
                        "type": "number"
                    }
                },
                "required": ["a-a"]
            }

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            Test_A()

    def test_load_cmd_config(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number"
                    }
                },
                "required": ["a_a"]
            }
        root = Test_A()

        @root.as_main
        def _(a_a: float) -> None:
            pass

        root(["--a-a=321.5"])
        self.assertDictEqual(root.config, {
            "a_a": 321.5
        })

    def test_load_cmd_noflag_config(self) -> None:
        class Test_A(EntryPoint):
            default_config_file_paths = [
                "/test_config.json",
                str(Path.home().joinpath(".test_config.json")),
                "./test_config.json"
            ]
            argparse_noflag = "a"
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number"
                    }
                },
                "required": ["a"]
            }
        root = Test_A()

        @root.as_main
        def _(a: int) -> None:
            pass

        root(["321.5"])
        self.assertDictEqual(root.config, {
            "a": 321.5
        })

    def test_load_config_order1(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer"
                    }
                },
                "required": ["a"]
            }
        root = Test_A()

        @root.as_main
        def _(a: int) -> None:
            pass
        os.environ['TEST_A_A'] = "2"
        root(["--a=3"])
        self.assertDictEqual(root.config, {
            "a": 3
        })

    def test_load_config_order2(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer"
                    }
                },
                "required": ["a"]
            }
        root = Test_A()

        @root.as_main
        def _(a: int) -> None:
            pass
        root(["--a=3"])
        self.assertDictEqual(root.config, {
            "a": 3
        })

    def test_load_config_order3(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer"
                    }
                },
                "required": ["a"]
            }
        root = Test_A()

        @root.as_main
        def _(a: int) -> None:
            pass
        os.environ['TEST_A_A'] = "2"
        root([])
        self.assertDictEqual(root.config, {
            "a": 2
        })