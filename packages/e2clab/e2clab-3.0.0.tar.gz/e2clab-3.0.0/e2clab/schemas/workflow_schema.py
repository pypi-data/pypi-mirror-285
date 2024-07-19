from jsonschema import Draft7Validator

from e2clab.constants import (
    WORKFLOW_DEPENDS_ON,
    WORKFLOW_GROUPING,
    WORKFLOW_GROUPING_LIST_USER,
    WORKFLOW_PREFIX,
    WORKFLOW_SERV_SELECT,
    WORKFLOW_TARGET,
    WORKFLOW_TASKS,
)

task_schema: dict = {
    "description": "Ansible task definition.",
    "type": "array",
}

workflow_schema_tasks: dict = {TASK: task_schema for TASK in WORKFLOW_TASKS}

# TODO: finish workflow schema
depends_on_schema = {
    "description": "Description of hosts interconnections",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            WORKFLOW_SERV_SELECT: {
                "description": "",
                "type": "string",
            },
            WORKFLOW_GROUPING: {
                "description": "Grouping strategy between hosts, defaults: round_robin",
                "type": "string",
                "enum": WORKFLOW_GROUPING_LIST_USER,
            },
            WORKFLOW_PREFIX: {
                "description": "Prefix to access linked hosts parameters",
                "type": "string",
            },
        },
        "required": [WORKFLOW_SERV_SELECT, WORKFLOW_PREFIX],
    },
}

SCHEMA: dict = {
    "description": "Non-described properties will be passed to ansible in a play.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            WORKFLOW_TARGET: {
                "description": "hosts description on which to execute workflow",
                "type": "string",
            },
            WORKFLOW_DEPENDS_ON: {"$ref": "#/definitions/depends_on"},
            **workflow_schema_tasks,
        },
        "required": [WORKFLOW_TARGET],
        # "additionalProperties": False,
    },
    "definitions": {"depends_on": depends_on_schema},
}

WorkflowValidator: Draft7Validator = Draft7Validator(SCHEMA)
