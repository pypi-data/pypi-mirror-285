from copy import deepcopy

from e2clab.constants import (
    ANSIBLE_TASKS,
    DSTAT_DEFAULT_OPTS,
    DSTAT_OPTIONS,
    LAYERS,
    MONITORING_SVC,
    MONITORING_SVC_AGENT_CONF,
    PROVENANCE_SVC,
    PROVENANCE_SVC_DATAFLOW_SPEC,
    PROVENANCE_SVC_PARALLELISM,
    REPEAT,
    SERVICES,
    WORKFLOW_ENV_PREFIX,
    WORKFLOW_TASKS,
)
from e2clab.errors import E2clabConfigError
from e2clab.log import getLogger
from e2clab.schemas import is_valid_conf


class E2clabConfig:
    pass


class InfrastructureConfig(dict, E2clabConfig):
    """
    Class to manage infrastructure configuration
    """

    def __init__(self, data) -> None:
        super().__init__(data)
        if not is_valid_conf(self, "layers_services"):
            raise E2clabConfigError
        self.logger = getLogger(__name__, ["INF_CONF"])

    def prepare(self):
        """
        Repeats services and generates services ids
        """
        self._repeat_services()
        self._generate_service_id()

    def is_provenance_def(self):
        return PROVENANCE_SVC in self.keys()

    def get_provenance_parallelism(self):
        # No parallelism defined defaults to 1
        parallelism = self[PROVENANCE_SVC].get(PROVENANCE_SVC_PARALLELISM, 1)
        return parallelism

    def get_provenance_dataflow_spec(self):
        dataflow_spec = self[PROVENANCE_SVC].get(PROVENANCE_SVC_DATAFLOW_SPEC, "")
        return dataflow_spec

    def get_monitoring_agent_conf(self) -> str:
        try:
            conf = self[MONITORING_SVC][MONITORING_SVC_AGENT_CONF]
        except KeyError:
            return None
        return conf

    def get_dstat_options(self) -> str:
        try:
            opt = self[MONITORING_SVC][DSTAT_OPTIONS]
        except KeyError:
            self.logger.info(f"DSTAT options defaulting to: {DSTAT_DEFAULT_OPTS}")
            return DSTAT_DEFAULT_OPTS
        return opt

    def _repeat_services(self):
        """Repeats the Service configuration in the 'layers_services.yaml' file.
        :param infra_config: refers to the 'layers_services.yaml' file.
        """
        for layer in self[LAYERS]:
            for service in layer[SERVICES]:
                if REPEAT in service:
                    for i in range(service.pop(REPEAT)):
                        layer[SERVICES].append(deepcopy(service))

    def _generate_service_id(self):
        """
        Updates infra_config (layers_services.yaml file defined by users) with
        the _id at the service level.
        An INITIAL (incomplete) Service ID is defined as: "LayerID_ServiceID".
            For example: a Service with ID = "1_1", means first Layer and first
            Service in that layer (as defined in "layers_services.yaml")

        NOTE: The FINAL (complete) "ServiceID" is: "LayerID_ServiceID_MachineID"
            and is generated after Service registration
            (see e2clab.services.Service.__service_key()).
        :param infra_config: refers to the 'layers_services.yaml' file.
        """
        layer_id = 0
        for layer in self[LAYERS]:
            layer_id += 1
            service_id = 0
            for service in layer[SERVICES]:
                service_id += 1
                service["_id"] = str(layer_id) + "_" + str(service_id)


class NetworkConfig(dict, E2clabConfig):
    """
    Class to manage network configuration
    """

    def __init__(self, data) -> None:
        super().__init__(data)
        if not is_valid_conf(self, "network"):
            raise E2clabConfigError


class WorkflowConfig(list, E2clabConfig):
    """
    Class to manage workflow configuration
    """

    def __init__(self, data: list, is_filtered: bool = False) -> None:
        super().__init__(data)
        if not is_valid_conf(self, "workflow"):
            raise E2clabConfigError
        self.is_filtered = is_filtered

    def get_task_filtered_host_config(self, task: str):
        """
            Returns a list of hosts in workflow.yaml (-hosts:)
        with a single task [prepare, launch, finalize] defined in task_filter
        :param task: prepare, or launch, or finalize
        :return: A filtered WorkflowConfig
        """
        if self.is_filtered:
            raise Exception("Cannot filter a Workflow config twice !")
        filtered_host = []
        for host in deepcopy(self):
            if task in host:
                host[ANSIBLE_TASKS] = host.pop(task)
                for other_task in WORKFLOW_TASKS:
                    host.pop(other_task, None)
                filtered_host.append(host)
        return WorkflowConfig(filtered_host, True)


class WorkflowEnvConfig(dict, E2clabConfig):
    """
    Class to manage workflow environment configuration
    """

    def __init__(self, data) -> None:
        super().__init__(data)
        if not is_valid_conf(data, "workflow_env"):
            raise E2clabConfigError
        # TODO: Add a configuration schema validation stage
        self._prefix_env_variables()

    def get_env(self, key: str, default=None) -> None:
        return super(WorkflowEnvConfig, self).get(key, default)

    def _prefix_env_variables(self):
        """Prefixes workflow environment variables"""
        _prefix = WORKFLOW_ENV_PREFIX
        for k, v in self.items():
            self[k] = {f"{_prefix}{key}": val for key, val in v.items()}
