import os
import json
import unittest
from pathlib import Path
from typing import Dict, Any, List
import jsonschema.exceptions

from schema_entry.entrypoint import EntryPoint
from pydantic import BaseModel, Field
from enum import Enum


def setUpModule() -> None:
    print("[SetUp Submodule schema_entry.entrypoint with_schema test]")


def tearDownModule() -> None:
    print("[TearDown Submodule schema_entry.entrypoint with_schema test]")


class CMDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("setUp CMDTest with_schema test context")

    @classmethod
    def tearDownClass(cls) -> None:
        print("tearDown CMDTest with_schema test context")

    def test_without_schema_jsonstring(self) -> None:
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

        root = EntryPoint(name="test_a")
        root.with_schema(json.dumps(schema))
        assert root.name == "test_a"
        root([])
        self.assertDictEqual(root.config, {
            "a_a": 33.3
        })

    def test_without_schema_jsondict(self) -> None:
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

        root = EntryPoint(name="test_a")
        root.with_schema(schema)
        assert root.name == "test_a"
        root([])
        self.assertDictEqual(root.config, {
            "a_a": 33.3
        })

    def test_without_schema_pydantic(self) -> None:
        class Gender(str, Enum):
            male = 'male'
            female = 'female'
            other = 'other'
            not_given = 'not_given'
        root = EntryPoint()

        @root.with_schema
        class GenderTest(BaseModel):
            """测试description."""
            gender: Gender = Field(
                Gender.male,
                title='g',
                description='this is the value of snap'
            )
            gender_list: List[Gender] = Field(
                ...,
                title='l',
                description='this is the value of snap'
            )

        assert root.name == "gendertest"
        assert root.__doc__ == "测试description."
        print(root.schema)
        root(["-l", "male", "-l", "other"])
        self.assertDictEqual(root.config, {
            "gender": "male",
            "gender_list": ["male", "other"]
        })
