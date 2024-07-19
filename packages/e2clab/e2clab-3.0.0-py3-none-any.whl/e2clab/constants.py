from pathlib import Path

"""
    Default global parameters
"""
DEFAULT_G5K_CLUSTER = "paravance"  # Unused
DEFAULT_IOTLAB_CLUSTER = "saclay"
DEFAULT_CHAMELEON_CLOUD_CLUSTER = "gpu_rtx_6000"
DEFAULT_CHAMELEON_EDGE_CLUSTER = "jetson-nano"
DEFAULT_JOB_NAME = "E2Clab"
DEFAULT_WALLTIME = "01:00:00"
DEFAULT_NODE_QUANTITY = 1
DEFAULT_SSH_KEYFILE = str(Path.home() / ".ssh" / "id_rsa.pub")
DEFAULT_SERVICE_NAME = "Default"
QUANTITY = "quantity"

PATH_ROOT_E2CLAB = Path(__file__).parent.resolve()
PATH_SERVICES_PLUGINS = PATH_ROOT_E2CLAB / "services" / "plugins"


"""
    Environments yaml keys
"""
G5K = "g5k"
IOT_LAB = "iotlab"
CHAMELEON_CLOUD = "chameleoncloud"
CHAMELEON_EDGE = "chameleonedge"
SUPPORTED_ENVIRONMENTS = [G5K, CHAMELEON_CLOUD, CHAMELEON_EDGE, IOT_LAB]

"""
    CLI constants
"""

COMMAND_DEPLOY = "deploy"
COMMAND_LYR_SVC = "layers-services"
COMMAND_NETWORK = "network"
COMMAND_WORKFLOW = "workflow"
COMMAND_FINALIZE = "finalize"

COMMAND_RUN_LIST = [
    COMMAND_DEPLOY,
    COMMAND_LYR_SVC,
    COMMAND_NETWORK,
    COMMAND_WORKFLOW,
    COMMAND_FINALIZE,
]

"""
    Layers Services file definitions
"""
LAYERS_SERVICES_CONF_FILE = "layers_services.yaml"

ENVIRONMENT = "environment"
LAYERS = "layers"

KEY_NAME = "ssh_key"
FIREWALL_RULES = "firewall_rules"
PORTS = "ports"
CLUSTER = "cluster"
SERVERS = "servers"
JOB_TYPE_DEPLOY = "deploy"
JOB_NAME = "job_name"
JOB_TYPE = "job_type"
QUEUE = "queue"
WALLTIME = "walltime"
RESERVATION = "reservation"
ENV_NAME = "env_name"
SERVICES = "services"
NAME = "name"
IMAGE = "image"
ARCHI = "archi"
ROLES = "roles"
ENV = "env"
KEY_NAME = "key_name"
REPEAT = "repeat"
RC_FILE = "rc_file"
IPV = "ipv"
IPV_VERSIONS = [4, 6]

MONITORING_SVC_PROVIDER = "provider"
MONITORING_SVC = "monitoring"
MONITORING_DATA = "monitoring-data"
MONITORING_SVC_PORT = "3000"
MONITORING_SVC_TYPE = "type"
MONITORING_SVC_TIG = "tig"
MONITORING_SVC_TPG = "tpg"
MONITORING_SVC_DSTAT = "dstat"
DSTAT_OPTIONS = "options"
DSTAT_DEFAULT_OPTS = "-m -c -n"
MONITORING_SVC_NETWORK = "network"
MONITORING_SVC_NETWORK_PRIVATE = "private"
MONITORING_SVC_NETWORK_SHARED = "shared"
MONITORING_SVC_AGENT_CONF = "agent_conf"
MONITORING_REMOTE_WORKING_DIR = "monitoring_remote_working_dir"
ROLES_MONITORING = "monitoring"
MONITORING_NETWORK_ROLE = "my_monitoring_network"
MONITORING_NETWORK_ROLE_IP = MONITORING_NETWORK_ROLE + "_ip"
MONITORING_SERVICE_ROLE = "monitoring_service"

PROVENANCE_SVC = "provenance"
PROVENANCE_SVC_PARALLELISM = "parallelism"
PROVENANCE_SERVICE_ROLE = "provenance_service"
ROLES_PROVENANCE = "provenance"
PROVENANCE_SVC_PORT = "22000"
PROVENANCE_SVC_PROVIDER = "provider"
PROVENANCE_SVC_DATAFLOW_SPEC = "dataflow_spec"
DFA_CONTAINER_NAME = "dfanalyzer"
PROVENANCE_DATA = "provenance-data"


"""
    Network file definitions
"""
NETWORK_CONF_FILE = "network.yaml"
NET_NETWORKS = "networks"
NET_SRC = "src"
NET_DST = "dst"
NET_DELAY = "delay"
NET_RATE = "rate"
NET_LOSS = "loss"
NET_SYMMETRIC = "symmetric"

"""
    Workflow file configuration
"""
WORKFLOW_CONF_FILE = "workflow.yaml"

WORKFLOW_TARGET = "hosts"
WORKFLOW_DEPENDS_ON = "depends_on"
WORKFLOW_SERV_SELECT = "service_selector"
WORKFLOW_GROUPING = "grouping"
WORKFLOW_PREFIX = "prefix"

WORKFLOW_GROUPING_LIST = [
    "round_robin",
    "asarray",
    "aggregate",
    # used internally by e2clab, not meant to use for the user
    "address_match",
]

WORKFLOW_GROUPING_LIST_USER = [
    "round_robin",
    "asarray",
    "aggregate",
    # CCTV example
    "address_match",
]

WORKFLOW_DEFAULT_GROUPING = "round_robin"

WORKFLOW_TASK_LAUNCH = "launch"
WORKFLOW_TASK_PREPARE = "prepare"
WORKFLOW_TASK_FINALIZE = "finalize"

ANSIBLE_TASKS = "tasks"

WORKFLOW_TASKS = [WORKFLOW_TASK_PREPARE, WORKFLOW_TASK_LAUNCH, WORKFLOW_TASK_FINALIZE]

WORKFLOW_DEVICE_TASK = ["copy", "shell", "fetch"]

"""
    Workflow env file configuration
"""
WORKFLOW_ENV_CONF_FILE = "workflow_env.yaml"

WORKFLOW_ENV_PREFIX = "env_"

LAYERS_SERVICES_VALIDATE_FILE = "layers_services-validate.yaml"
NETWORK_VALIDATE_DIR = "network-validate"
WORKFLOW_VALIDATE_FILE = "workflow-validate.out"


DEFAULT_ENV_NAME = "debian11-x64-big"
DEFAULT_CHICLOUD_IMAGE = "CC-Ubuntu20.04"
DEFAULT_CHIEDGE_IMAGE = "ubuntu"
CONTAINER_NAME = "mycontainer"
CONTAINERS = "containers"

EXPOSED_PORTS = "exposed_ports"
START = "start"
START_TIMEOUT = "start_timeout"
DEVICE_PROFILES = "device_profiles"

KAVLAN_GLOBAL = "kavlan-global"
KAVLAN = "kavlan"

MONITORING_IOTLAB = "monitoring_iotlab"

MONITORING_IOTLAB_ARCHI = ["a8", "m3", "custom"]
MONITORING_IOTLAB_DATA = "iotlab-data"
PROFILES = "profiles"
CURRENT = "current"
POWER = "power"
VOLTAGE = "voltage"
PERIOD = "period"
PERIOD_VALS = [140, 204, 332, 588, 1100, 2116, 4156, 8244]
DEFAULT_PERIOD_VAL = PERIOD_VALS[-1]
AVERAGE = "average"
AVERAGE_VALUES = [1, 4, 16, 64, 128, 256, 512, 1024]

LOG_E2CLAB_PREFIX = "E2C"
LOG_WRITING_MODE = "a+"
LOG_INFO_FILENAME = "e2clab.log"
LOG_ERR_FILENAME = "e2clab.err"

VALID_LAYERS_SERVICES_KEYS = [
    ENVIRONMENT,
    LAYERS,
    PROVENANCE_SVC,
    MONITORING_SVC,
    MONITORING_IOTLAB,
]
