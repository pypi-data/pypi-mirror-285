from abc import ABCMeta, abstractmethod
from typing import Tuple

from enoslib import Networks, Roles

from e2clab.constants import (
    CLUSTER,
    ENVIRONMENT,
    LAYERS,
    MONITORING_SERVICE_ROLE,
    MONITORING_SVC,
    MONITORING_SVC_DSTAT,
    MONITORING_SVC_PORT,
    MONITORING_SVC_TIG,
    MONITORING_SVC_TPG,
    MONITORING_SVC_TYPE,
    PROVENANCE_SERVICE_ROLE,
    PROVENANCE_SVC_PORT,
    SERVERS,
    SERVICES,
    SUPPORTED_ENVIRONMENTS,
)
from e2clab.log import getLogger

logger = getLogger(__name__, ["PROV"])


class Provider:
    """
    Base class for the provider.
    """

    __metaclass__ = ABCMeta

    # Register for all loaded subclasses of 'Provider'
    _loaded_providers = {}

    def __init__(self, infra_config, optimization_id):
        self.infra_config = infra_config
        self.optimization_id = optimization_id
        self.roles = None
        self.networks = None
        self.monitoring_provider = False
        self.provenance_provider = False
        self.raw_provider = None

    def __init_subclass__(cls, **kwargs) -> None:
        """
        When a subclass of 'Provider' is defined, it is stored in a dict for easy
        programmatic imports and instanciation.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in cls._loaded_providers.keys():
            cls._loaded_providers[cls.__name__] = cls

    @classmethod
    def get_loaded_providers(cls):
        return cls._loaded_providers

    @abstractmethod
    def init(self) -> Tuple[Roles, Networks]:
        """
        (abstract) Implement the logic of your custom Provider.
        Must return roles and networks.
        """
        pass

    @abstractmethod
    def destroy(self):
        """
        (abstract) Implement the logic to destroy (free)
        the resources of your custom Provider.
        """

    def get_provenance(self):
        _provenance_extra_info = {}
        if None not in (self.roles, self.networks) and self.provenance_provider:
            ui_address = self.roles[PROVENANCE_SERVICE_ROLE][0].address
            _provenance_extra_info.update(
                {
                    PROVENANCE_SERVICE_ROLE: {
                        "__address__": f"{ui_address}",
                        "url": f"http://{ui_address}:{PROVENANCE_SVC_PORT}",
                    }
                }
            )
        return _provenance_extra_info

    def get_monitoring(self):
        _monitoring_extra_info = {}
        _monitoring_type = None
        if None not in (self.roles, self.networks) and self.monitoring_provider:
            if self.infra_config[MONITORING_SVC][MONITORING_SVC_TYPE] in [
                MONITORING_SVC_TIG,
                MONITORING_SVC_TPG,
            ]:
                _monitoring_type = (
                    MONITORING_SVC_TIG
                    if (
                        self.infra_config[MONITORING_SVC][MONITORING_SVC_TYPE]
                        in [MONITORING_SVC_TIG]
                    )
                    else MONITORING_SVC_TPG
                )
                ui_address = self.roles[MONITORING_SERVICE_ROLE][0].address
                _monitoring_extra_info.update(
                    {
                        MONITORING_SERVICE_ROLE: {
                            "__address__": f"{ui_address}",
                            "url": f"http://{ui_address}:{MONITORING_SVC_PORT}",
                        }
                    }
                )
            elif (
                self.infra_config[MONITORING_SVC][MONITORING_SVC_TYPE]
                == MONITORING_SVC_DSTAT
            ):
                _monitoring_type = MONITORING_SVC_DSTAT

        return _monitoring_type, _monitoring_extra_info

    def refine_config_file(self, target_environment):
        """
        Refines the 'layers_services.yaml' file to the target environment.
        """
        # TODO: move this method to InfrastructureConfig

        # Master environment defaults to first one defined in ENVIRONMENT
        master_environment = ""
        for environment_key in self.infra_config[ENVIRONMENT]:
            if environment_key in SUPPORTED_ENVIRONMENTS:
                master_environment = environment_key
                break

        if (
            target_environment in self.infra_config[ENVIRONMENT]
            and self.infra_config[ENVIRONMENT][target_environment] is not None
        ):
            self.infra_config[ENVIRONMENT].update(
                self.infra_config[ENVIRONMENT].pop(target_environment)
            )

        # Filter out services that aren't supposed to run on our target environmet
        for layer in list(self.infra_config[LAYERS]):
            for service in list(layer[SERVICES]):
                if (
                    ENVIRONMENT in service
                    and service[ENVIRONMENT] != target_environment
                ):
                    layer[SERVICES].remove(service)
                elif (
                    ENVIRONMENT not in service
                    and master_environment != target_environment
                ):
                    layer[SERVICES].remove(service)
            if not layer[SERVICES]:
                self.infra_config[LAYERS].remove(layer)

    def log_roles_networks(self, target_environment):
        logger.debug(f" Roles [{target_environment}] = {self.roles}")
        logger.debug(f" Networks [{target_environment}] = {self.networks}")

    @staticmethod
    def check_service_mapping(service):
        add_cluster = None
        add_servers = None
        if CLUSTER in service:
            add_cluster = service[CLUSTER]
        elif SERVERS in service:
            add_servers = service[SERVERS]
        return add_cluster, add_servers
