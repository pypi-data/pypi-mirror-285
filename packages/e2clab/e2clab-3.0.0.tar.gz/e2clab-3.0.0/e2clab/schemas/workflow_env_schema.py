from jsonschema import Draft7Validator

SCHEMA: dict = {
    "type": "object",
    "patternProperties": {
        ".*": {
            "type": "object",
            "additionalProperties": {
                "type": ["string", "number", "boolean", "object"],
                "additionalProperties": False,
                "properties": {},
            },
        }
    },
}

WorkflowEnvValidator: Draft7Validator = Draft7Validator(SCHEMA)
