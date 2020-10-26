"""protocol.

用于定义模块支持的可以用于解析的json schema的模式.
"""
SUPPORT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "properties": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                r"^\w+$": {
                    "oneOf": [
                        {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "boolean"
                                },
                                "default": {
                                    "type": "boolean",
                                },
                                "const": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            }
                        },
                        {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "string"
                                },
                                "default": {
                                    "type": "string",
                                },
                                "const": {
                                    "type": "string"
                                },
                                "enum": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "maxLength": {
                                    "type": "integer",
                                    "minimum": 0
                                },
                                "minLength": {
                                    "type": "integer",
                                    "minimum": 0
                                },
                                "pattern": {
                                    "type": "string"
                                },
                                "format": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            }
                        }, {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "number"
                                },
                                "default": {
                                    "type": "number",
                                },
                                "const": {
                                    "type": "number"
                                },
                                "enum": {
                                    "type": "array",
                                    "items": {
                                        "type": "number"
                                    }
                                },
                                "maximum": {
                                    "type": "number",
                                },
                                "exclusiveMaximum": {
                                    "type": "number",
                                },
                                "minimum": {
                                    "type": "number",

                                },
                                "exclusiveMinimum": {
                                    "type": "number",

                                },
                                "description": {
                                    "type": "string"
                                }
                            }
                        }, {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "integer"
                                },
                                "default": {
                                    "type": "integer",
                                },
                                "const": {
                                    "type": "integer"
                                },
                                "enum": {
                                    "type": "array",
                                    "items": {
                                        "type": "integer"
                                    }
                                },
                                "maximum": {
                                    "type": "integer",
                                },
                                "exclusiveMaximum": {
                                    "type": "integer",
                                },
                                "minimum": {
                                    "type": "integer",

                                },
                                "exclusiveMinimum": {
                                    "type": "integer",

                                },
                                "description": {
                                    "type": "string"
                                }
                            }
                        }, {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "array"
                                },
                                "item": {
                                    "type": "object",
                                    "required": ["type"],
                                    "additionalProperties":False,
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["string", "number", "integer"]
                                        }
                                    }
                                },
                                "description":{
                                    "type": "string"
                                }
                            }
                        }
                    ]

                }
            }
        },
        "type": {
            "type": "string",
            "const": "object"
        },
        "required": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }

    },
    "required": ["properties", "type"]
}