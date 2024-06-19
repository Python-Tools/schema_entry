import os
import json
import unittest
from pathlib import Path
from typing import Dict, Any
import jsonschema.exceptions

from schema_entry.entrypoint import EntryPoint


def setUpModule() -> None:
    print("[SetUp Submodule schema_entry.entrypoint basic test]")


def tearDownModule() -> None:
    print("[TearDown Submodule schema_entry.entrypoint basic test]")


class CMDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp CMDTest test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown CMDTest test context")

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
        def _(**kwargs: Any) -> None:
            pass

        root([])

        assert root.usage == "test_a [options]"

    def test_default_main(self) -> None:
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
        config = root(["--a-a=4.2"])
        target = {
            "caller": "test_a",
            "result": {
                "a_a": 4.2
            }
        }
        self.assertDictEqual(config, target)

    def test_main_return(self) -> None:
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

            def do_main(self) -> str:
                return "a test"
        root = Test_A()
        get_value = root(["--a-a=4.2"])
        target = {"caller": "test_a", "result": "a test"}
        assert get_value == target

    def test_override_do_main(self) -> None:
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

            def do_main(self) -> None:
                assert self.config["a_a"] == 33.3
        root = Test_A()
        root([])

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

    def test_subcmd_return(self) -> None:
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
        def _(a: int) -> int:
            return a
        os.environ['A_B_C_A'] = "2"
        call_result = root(["b", "c"])

        self.assertDictEqual(call_result, {
            "caller": "c",
            "result": 2
        })


class LoadConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp LoadConfigTest test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown LoadConfigTest test context")

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

    def test_load_json_configfile_onlyneed(self) -> None:
        class Test_A_onlyneed(EntryPoint):
            default_config_file_paths = [
                "/test_config1.json",
                str(Path.home().joinpath(".test_config1.json")),
                "./test_config1.json"
            ]
            config_file_only_get_need = True
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
        root = Test_A_onlyneed()

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

    def test_load_json_configfile_cmd(self) -> None:
        class Test_AC(EntryPoint):
            verify_schema = False
        root = Test_AC()

        @root.as_main
        def _(a: int) -> None:
            pass
        root(["-c", "test_config.json"])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_all_configfile(self) -> None:
        class Test_AC(EntryPoint):
            load_all_config_file = True
            default_config_file_paths = [
                "./test_config.json",
                "./test_config1.json",
                "./test_config2.json"
            ]
        root = Test_AC()

        @root.as_main
        def _(a: int, b: int, c: int, d: int) -> None:
            assert a == 1
            assert b == 2
            assert c == 13
            assert d == 43

        root([])

    def test_load_configfile_with_custom_parser(self) -> None:
        class Test_AC(EntryPoint):
            load_all_config_file = True
            default_config_file_paths = [
                "./test_config.json",
                "./test_config1.json",
                "./test_other_config2.json"
            ]
        root = Test_AC()

        @root.regist_config_file_parser("test_other_config2.json")
        def _1(p: Path) -> Dict[str, Any]:
            with open(p) as f:
                temp = json.load(f)
            return {k.lower(): v for k, v in temp.items()}

        @root.as_main
        def _2(a: int, b: int, c: int, d: int) -> None:
            assert a == 1
            assert b == 2
            assert c == 13
            assert d == 43

        root([])

    def test_load_configfile_with_custom_parser_in_class(self) -> None:
        def test_other_config2_parser(p: Path) -> Dict[str, Any]:
            with open(p) as f:
                temp = json.load(f)
            return {k.lower(): v for k, v in temp.items()}

        class Test_AC(EntryPoint):
            load_all_config_file = True
            default_config_file_paths = [
                "./test_config.json",
                "./test_config1.json",
                "./test_other_config2.json"
            ]
            _config_file_parser_map = {
                "test_other_config2.json": test_other_config2_parser
            }

        root = Test_AC()

        @root.as_main
        def _2(a: int, b: int, c: int, d: int) -> None:
            assert a == 1
            assert b == 2
            assert c == 13
            assert d == 43

        root([])

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

    def test_load_short_cmd_config(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "a_a": {
                        "type": "number",
                        "title": "a"
                    }
                },
                "required": ["a_a"]
            }
        root = Test_A()

        @root.as_main
        def _(a_a: float) -> None:
            pass

        root(["-a", "321.5"])
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

    def test_load_array_cmd_config(self) -> None:
        class Test_A(EntryPoint):
            argparse_noflag = "a_a"
            schema = {
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
            }
        root = Test_A()

        @root.as_main
        def _(a_a: float) -> None:
            pass

        root(["a", "b", "c"])
        self.assertDictEqual(root.config, {
            "a_a": ["a", "b", "c"]
        })
