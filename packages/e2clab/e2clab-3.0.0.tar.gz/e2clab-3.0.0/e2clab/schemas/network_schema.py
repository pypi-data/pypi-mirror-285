from jsonschema import Draft7Validator

from e2clab.constants import (
    NET_DELAY,
    NET_DST,
    NET_LOSS,
    NET_NETWORKS,
    NET_RATE,
    NET_SRC,
    NET_SYMMETRIC,
)

SCHEMA: dict = {
    "description": "Experiment Network description",
    "type": "object",
    "properties": {
        NET_NETWORKS: {
            "type": ["array", "null"],
            "items": {"$ref": "#/definitions/network"},
        }
    },
    "required": [NET_NETWORKS],
    "additionalProperties": False,
    "definitions": {
        "network": {
            "title": "Network emulation",
            # "$$target": "#/definitons/network",
            "type": "object",
            "properties": {
                NET_SRC: {
                    "description": "Source layer name",
                    "type": "string",
                },
                NET_DST: {
                    "description": "Destination layer name",
                    "type": "string",
                },
                NET_DELAY: {
                    "description": "The delay to apply",
                    "type": "string",
                    "examples": ["10ms", "1ms"],
                },
                NET_RATE: {
                    "description": "The rate to apply",
                    "type": "string",
                    "examples": ["1gbit", "100mbit"],
                },
                NET_LOSS: {
                    "description": "The percentage of loss",
                    "type": "string",
                    "pattern": r"\d*.?\d*%",
                    "examples": ["1%", "5%"],
                },
                NET_SYMMETRIC: {
                    "description": "True for symmetric rules to be applied",
                    "type": "boolean",
                },
            },
            "required": [NET_SRC, NET_DST],
            "additionalProperties": False,
        }
    },
}

NetworkValidator: Draft7Validator = Draft7Validator(SCHEMA)
