from jsonschema import Draft7Validator

from e2clab.constants import (
    ARCHI,
    AVERAGE,
    AVERAGE_VALUES,
    CHAMELEON_CLOUD,
    CHAMELEON_EDGE,
    CLUSTER,
    CURRENT,
    DEFAULT_CHAMELEON_EDGE_CLUSTER,
    DEFAULT_CHICLOUD_IMAGE,
    DEFAULT_CHIEDGE_IMAGE,
    DEFAULT_IOTLAB_CLUSTER,
    DEFAULT_JOB_NAME,
    DEFAULT_PERIOD_VAL,
    DSTAT_DEFAULT_OPTS,
    DSTAT_OPTIONS,
    ENV,
    ENV_NAME,
    ENVIRONMENT,
    FIREWALL_RULES,
    G5K,
    IMAGE,
    IOT_LAB,
    IPV,
    IPV_VERSIONS,
    JOB_NAME,
    JOB_TYPE,
    JOB_TYPE_DEPLOY,
    KEY_NAME,
    LAYERS,
    MONITORING_IOTLAB,
    MONITORING_IOTLAB_ARCHI,
    MONITORING_SVC,
    MONITORING_SVC_AGENT_CONF,
    MONITORING_SVC_DSTAT,
    MONITORING_SVC_NETWORK,
    MONITORING_SVC_NETWORK_PRIVATE,
    MONITORING_SVC_NETWORK_SHARED,
    MONITORING_SVC_PROVIDER,
    MONITORING_SVC_TIG,
    MONITORING_SVC_TPG,
    MONITORING_SVC_TYPE,
    NAME,
    PERIOD,
    PERIOD_VALS,
    POWER,
    PROFILES,
    PROVENANCE_SVC,
    PROVENANCE_SVC_DATAFLOW_SPEC,
    PROVENANCE_SVC_PARALLELISM,
    PROVENANCE_SVC_PROVIDER,
    QUANTITY,
    RC_FILE,
    REPEAT,
    RESERVATION,
    ROLES,
    SERVERS,
    SERVICES,
    SUPPORTED_ENVIRONMENTS,
    VOLTAGE,
    WALLTIME,
)

walltime_schema: dict = {
    "description": "Walltime for our experiment, in format hh:mm:ss",
    "type": "string",
    "pattern": r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$",
}

service_schema: dict = {
    "descritpion": "E2clab service, other properties are service metedata",
    "type": "object",
    "properties": {
        NAME: {
            "description": (
                "Name of the service. "
                "If the name matches a user-defined service name, "
                "this service will be deployed. "
            ),
            "type": "string",
        },
        QUANTITY: {
            "description": "Number of nodes the service will be deployed on",
            "type": "number",
        },
        ROLES: {
            "type": "array",
        },
        REPEAT: {
            "description": (
                "Number of times the service " "definition will be duplicated."
            ),
            "type": "number",
        },
        ENV: {
            "description": "Service metadata.",
            "type": "object",
        },
        ENVIRONMENT: {
            "description": (
                "Environment on which the service will be deployed."
                "If set, you can specify other environment-specific properties"
                "from the environment you chose"
            ),
            "type": "string",
            "enum": SUPPORTED_ENVIRONMENTS,
        },
        SERVERS: {
            "description": "Server to deploy services, overwrites cluster definition",
            # "type": "array", can be array or string it seems
            "examples": [
                "chifflot-7.lille.grid5000.fr",
                "chifflot-8.lille.grid5000.fr",
            ],
        },
        # Other properties are service metadata, to configure per service.
    },
    "required": [NAME],
}

service_list: dict = {
    "description": "Description of the service to be deployed on our layer.",
    "type": "array",
    "items": service_schema,
}

job_name_schema: dict = {
    "description": "Name of the job on the testbed",
    "type": "string",
    "default": DEFAULT_JOB_NAME,
}

# see _provider_g5k in G5k.py
g5k_schema: dict = {
    "type": "object",
    "properties": {
        JOB_NAME: job_name_schema,
        WALLTIME: walltime_schema,
        RESERVATION: {
            "description": "reservation date in YYYY-mm-dd HH:MM:SS format",
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        },
        JOB_TYPE: {
            "description": "OAR job type",
            "type": "array",
            "default": [JOB_TYPE_DEPLOY],
        },
        ENV_NAME: {
            "description": "The kadeploy3 environment to use (deploy only)",
            "type": "string",
        },
        CLUSTER: {"description": "Which G5k cluster to use", "type": "string"},
        KEY_NAME: {
            "description": "SSH public key to use",
            "type": "string",
            "default": "~/.ssh/id_rsa.pub",
        },
        FIREWALL_RULES: {
            "description": "G5k firewall rules",
            "type": "array",
        },
    },
}

# see _provider_iotlab in Iotlab.py
iotlab_schema: dict = {
    "type": "object",
    "properties": {
        JOB_NAME: job_name_schema,
        WALLTIME: walltime_schema,
        CLUSTER: {
            "description": "Iotlab cluster to use",
            "type": "string",
            "default": DEFAULT_IOTLAB_CLUSTER,
        },
    },
}

# see _provider_chameleoncloud in Chameleoncloud.py
chameleon_cloud_schema: dict = {
    "type": "object",
    "properties": {
        JOB_NAME: job_name_schema,
        WALLTIME: walltime_schema,
        RC_FILE: {
            "description": "Openstack environment rc file path",
            "type": "string",
        },
        KEY_NAME: {
            "description": "SSH pub key",
            "type": "string",
        },
        IMAGE: {
            "description": "Cloud image to use",
            "type": "string",
            "default": DEFAULT_CHICLOUD_IMAGE,
        },
        CLUSTER: {
            "descruption": "Chameleon cloud machine flavour to use",
            "type": "string",
        },
    },
}

# see _provider_chameleonedge in Chameleonedge.py
chameleon_edge_schema: dict = {
    "type": "object",
    "properties": {
        JOB_NAME: job_name_schema,
        WALLTIME: walltime_schema,
        RC_FILE: {
            "description": "Openstack environment rc file path",
            "type": "string",
        },
        KEY_NAME: {
            "description": "SSH pub key",
            "type": "string",
        },
        IMAGE: {
            "description": "Chameleon edge image to use",
            "type": "string",
            "default": DEFAULT_CHIEDGE_IMAGE,
        },
        CLUSTER: {
            "description": "Chameleon edge machine flavour to use",
            "type": "string",
            "default": DEFAULT_CHAMELEON_EDGE_CLUSTER,
        },
    },
}

common_prov_properties: dict = {
    JOB_NAME: job_name_schema,
    WALLTIME: walltime_schema,
    CLUSTER: {"description": "Which cluster to deploy on", "type": "string"},
}

iotlab_monitoring_profile = {
    "description": "https://www.iot-lab.info/testbed/resources/monitoring",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            NAME: {
                "description": "Name of the monitoring profile.",
                "type": "string",
            },
            ARCHI: {
                "Description": "Type of architecture to monitor.",
                "type": "string",
                "enum": MONITORING_IOTLAB_ARCHI,
            },
            CURRENT: {
                "description": "Enable current monitoring",
                "type": "boolean",
                "default": False,
            },
            POWER: {
                "description": "Enable power monitoring",
                "type": "boolean",
                "default": False,
            },
            VOLTAGE: {
                "description": "Enable voltage monitoring",
                "type": "boolean",
                "default": False,
            },
            PERIOD: {
                "description": "Sampling period (µs)",
                "type": "number",
                "enum": PERIOD_VALS,
                "default": DEFAULT_PERIOD_VAL,
            },
            AVERAGE: {
                "description": "Monitoring samples averaging window.",
                "type": "number",
                "enum": AVERAGE_VALUES,
            },
        },
        "required": [NAME, ARCHI, PERIOD, AVERAGE],
    },
}

provenance_svc_schema = {
    "description": "Definition of the provenance data capture capabilities",
    "type": "object",
    "properties": {
        PROVENANCE_SVC_PROVIDER: {
            "description": "Testbed to deploy the provenance service: G5k only for now",
            "type": "string",
            "enum": SUPPORTED_ENVIRONMENTS,
        },
        CLUSTER: {
            "description": "Machine where the the provenence server will be running",
            "type": "string",
        },
        PROVENANCE_SVC_DATAFLOW_SPEC: {
            "description": "User-defined dataflow specifications",
            "type": "string",
        },
        IPV: {
            "description": "IP network version to transmit provenance data",
            "type": "number",
            "enum": IPV_VERSIONS,
            "default": 4,
        },
        PROVENANCE_SVC_PARALLELISM: {
            "description": "Parallelizes the prov data translator and broker topic",
            "type": "number",
            "default": 1,
        },
    },
    "required": [
        PROVENANCE_SVC_PROVIDER,
        CLUSTER,
        PROVENANCE_SVC_DATAFLOW_SPEC,
    ],
}

"""
    Main layers_services.yml schema
"""
monitoring_schema = {
    "description": "Definition of the monitoring capabilities",
    "type": "object",
    "properties": {
        MONITORING_SVC_TYPE: {
            "description": "Type of monitoring deployed on experiment",
            "type": "string",
            "enum": [
                MONITORING_SVC_DSTAT,
                MONITORING_SVC_TPG,
                MONITORING_SVC_TIG,
            ],
        },
        MONITORING_SVC_PROVIDER: {
            "description": "Dedicated machine hosting InfluxDB and Grafana",
            "type": "string",
        },
        CLUSTER: {
            "description": "Cluster on which to deploy the machine",
            "type": "string",
        },
        SERVERS: {
            "description": (
                f"Optional if {CLUSTER} defined. "
                "Machine on which to deploy the machine"
            ),
            "type": "array",
        },
        MONITORING_SVC_NETWORK: {
            "description": (
                "Define network for the monitoring service. "
                # "'public' -> a new network is created' "
                # "'private' -> 2 NICs is needed on the server."
            ),
            "type": "string",
            "enum": [
                MONITORING_SVC_NETWORK_SHARED,
                MONITORING_SVC_NETWORK_PRIVATE,
            ],
        },
        MONITORING_SVC_AGENT_CONF: {
            "description": "Config file in 'artifacts_dir' for the monitoring agent",
            "type": "string",
        },
        DSTAT_OPTIONS: {
            "description": "Dstat monitoring options",
            "type": "string",
            "default": DSTAT_DEFAULT_OPTS,
        },
        IPV: {
            "description": "Type of network the monitoring provider will use.",
            "type": "number",
            "enum": IPV_VERSIONS,
        },
    },
    "required": [MONITORING_SVC_TYPE],  # , MONITORING_SVC_PROVIDER],
}

env_schema = {
    "description": "Definition of experiment environments",
    "type": "object",
    "properties": {
        # Common provider properties can be defined at the top level
        **common_prov_properties,
        JOB_NAME: {
            "description": "Name of our experiment",
            "type": "string",
        },
        G5K: {
            "description": "Grid5000 configuration",
            "$ref": f"#/definitions/{G5K}",
        },
        IOT_LAB: {
            "description": "FIT IoT-LAB configuration",
            "$ref": f"#/definitions/{IOT_LAB}",
        },
        CHAMELEON_CLOUD: {
            "description": "ChameleonCloud configuration",
            "$ref": f"#/definitions/{CHAMELEON_CLOUD}",
        },
        CHAMELEON_EDGE: {
            "description": "ChameleonEdge configuration",
            "$ref": f"#/definitions/{CHAMELEON_EDGE}",
        },
    },
    "required": [],
    "anyOf": [
        {"required": [prov]} for prov in SUPPORTED_ENVIRONMENTS
    ],  # Need at least one environment
}

# Main jsonschema
SCHEMA: dict = {
    "description": "Experiment Layers & Services description",
    "type": "object",
    "properties": {
        ENVIRONMENT: {"$ref": "#/definitions/environment"},
        LAYERS: {
            "description": "Experiment layers definition.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    NAME: {
                        "description": "Name of the layer, e.g. edge, fog, cloud...",
                        "type": "string",
                    },
                    SERVICES: {"$ref": "#/definitions/service_list"},
                },
                "required": [
                    NAME,
                    SERVICES,
                ],  # Need at least one layer with one service
            },
        },
        MONITORING_SVC: {"$ref": "#/definitions/e2clab_monitoring"},
        MONITORING_IOTLAB: {
            "default": "FIT IoT-Lab monitoring profiles ",
            "type": "object",
            "properties": {
                PROFILES: {"$ref": "#/definitions/iotlab_monitoring_profile"},
            },
            "required": [PROFILES],
        },
        PROVENANCE_SVC: {"$ref": "#/definitions/provenance_schema"},
    },
    "required": [LAYERS, ENVIRONMENT],
    "additionalProperties": False,  # Only defined properties are allowed
    "definitions": {
        "e2clab_monitoring": monitoring_schema,
        "iotlab_monitoring_profile": iotlab_monitoring_profile,
        "provenance_schema": provenance_svc_schema,
        "service_list": service_list,
        "environment": env_schema,
        G5K: g5k_schema,
        IOT_LAB: iotlab_schema,
        CHAMELEON_CLOUD: chameleon_cloud_schema,
        CHAMELEON_EDGE: chameleon_edge_schema,
    },
}

LayersServicesValidator: Draft7Validator = Draft7Validator(SCHEMA)
