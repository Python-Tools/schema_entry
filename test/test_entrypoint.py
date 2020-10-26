import os
import unittest
import argparse
from pathlib import Path
from typing import Dict, Any
from schema_entry.entrypoint import EntryPoint


def setUpModule() -> None:
    print("[SetUp Submodule schema_entry.entrypoint test]")


def tearDownModule() -> None:
    print("[TearDown Submodule schema_entry.entrypoint test]")


class LoadConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp GetParentTree test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown GetParentTree test context")

    def test_load_configfile(self) -> None:
        class Test_A(EntryPoint):
            default_config_file_paths = [
                "/test_config.json",
                str(Path.home().joinpath(".test_config.json")),
                "./test_config.json"
            ]
        root = Test_A()

        @root.as_main
        def f(_: Dict[str, Any]) -> None:
            pass
        root([])
        self.assertDictEqual(root.config, {
            "a": 1
        })

    def test_load_ENV_config(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "examples": [
                    {
                        "a": 123.1
                    },
                ],
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
        def f(_: Dict[str, Any]) -> None:
            pass
        os.environ['TEST_A_A'] = "123.1"
        root([])
        self.assertDictEqual(root.config, {
            "a": 123.1
        })

    def test_load_cmd_config(self) -> None:
        class Test_A(EntryPoint):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "examples": [
                    {
                        "a": 123.1
                    },
                ],
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
        def f(_: Dict[str, Any]) -> None:
            pass

        root(["--a=321.5"])
        self.assertDictEqual(root.config, {
            "a": 321.5
        })
