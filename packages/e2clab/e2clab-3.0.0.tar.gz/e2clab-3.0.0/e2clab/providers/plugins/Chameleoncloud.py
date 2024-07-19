import enoslib as en

from e2clab.constants import (
    CHAMELEON_CLOUD,
    CLUSTER,
    DEFAULT_CHICLOUD_IMAGE,
    DEFAULT_JOB_NAME,
    DEFAULT_NODE_QUANTITY,
    DEFAULT_WALLTIME,
    ENVIRONMENT,
    IMAGE,
    JOB_NAME,
    KEY_NAME,
    LAYERS,
    MONITORING_SERVICE_ROLE,
    MONITORING_SVC,
    MONITORING_SVC_PROVIDER,
    MONITORING_SVC_TIG,
    MONITORING_SVC_TPG,
    MONITORING_SVC_TYPE,
    NAME,
    QUANTITY,
    RC_FILE,
    ROLES,
    ROLES_MONITORING,
    SERVICES,
    WALLTIME,
)
from e2clab.log import getLogger
from e2clab.providers import Provider

logger = getLogger(__name__, ["CHAM"])


class Chameleoncloud(Provider):
    """
    The provider to use when deploying on Chameleon Cloud.
    """

    def init(self, testing: bool = False):
        """
        Take ownership over some Chameleon Cloud resources (compute and networks).
        :return: roles, networks
        """
        self.provider = self.__provider_chameleoncloud(
            infra_config=self.infra_config, optimization_id=self.optimization_id
        )

        if testing:
            return

        roles, networks = self.provider.init()
        roles = en.sync_info(roles, networks)

        if None in (roles, networks):
            raise ValueError(f"Failed to get resources from: {CHAMELEON_CLOUD}.")

        self.roles = roles
        self.networks = networks
        self.log_roles_networks(CHAMELEON_CLOUD)

        return roles, networks

    def destroy(self):
        self.provider.destroy()
        # raise NotImplementedError

    def __provider_chameleoncloud(self, infra_config, optimization_id):
        self.refine_config_file(CHAMELEON_CLOUD)
        logger.info(f" layers_services [{CHAMELEON_CLOUD}] = {self.infra_config}")

        _job_name = (
            infra_config[ENVIRONMENT][JOB_NAME]
            if (JOB_NAME in infra_config[ENVIRONMENT])
            else DEFAULT_JOB_NAME
        )
        _walltime = (
            infra_config[ENVIRONMENT][WALLTIME]
            if (WALLTIME in infra_config[ENVIRONMENT])
            else DEFAULT_WALLTIME
        )
        _rc_file = (
            infra_config[ENVIRONMENT][RC_FILE]
            if (RC_FILE in infra_config[ENVIRONMENT])
            else None
        )
        _key_name = (
            infra_config[ENVIRONMENT][KEY_NAME]
            if (KEY_NAME in infra_config[ENVIRONMENT])
            else None
        )
        _image = (
            infra_config[ENVIRONMENT][IMAGE]
            if (IMAGE in infra_config[ENVIRONMENT])
            else DEFAULT_CHICLOUD_IMAGE
        )
        _cluster = (
            infra_config[ENVIRONMENT][CLUSTER]
            if (CLUSTER in infra_config[ENVIRONMENT])
            else None
        )
        # TODO: Why not default cluster ?

        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                add_cluster, add_servers = self.check_service_mapping(service)
                if add_cluster is None and add_servers is None and _cluster is None:
                    raise Exception(
                        "Fix your 'layers_services.yaml' file. "
                        "Especify a 'CLUSTER' for each 'service' "
                        "or specify a default 'CLUSTER' "
                        "in 'chameleoncloud:'."
                    )

        if optimization_id is not None:
            lease_name = f"{_job_name}_{optimization_id}"
        else:
            lease_name = _job_name

        config = en.CBMConf.from_settings(
            lease_name=lease_name,
            walltime=_walltime,
            rc_file=_rc_file,
            key_name=_key_name,
            image=_image,
        )

        """
            MONITORING
        """
        if (MONITORING_SVC in infra_config) and (
            infra_config[MONITORING_SVC][MONITORING_SVC_TYPE]
            in [MONITORING_SVC_TIG, MONITORING_SVC_TPG]
        ):
            """Add Chameleon node as monitoring provider: 1 machine[ui,collector]"""
            if infra_config[MONITORING_SVC][MONITORING_SVC_PROVIDER] == CHAMELEON_CLOUD:
                self.monitoring_provider = True
                if CLUSTER not in infra_config[MONITORING_SVC]:
                    raise Exception("Specify a 'CLUSTER' in monitoring")
                elif CLUSTER in infra_config[MONITORING_SVC]:
                    _monitor_cluster = infra_config[MONITORING_SVC][CLUSTER]
                    config.add_machine(
                        roles=[MONITORING_SERVICE_ROLE],
                        flavour=_monitor_cluster,
                        number=DEFAULT_NODE_QUANTITY,
                    )

        """
            REQUEST RESOURCES
        """
        config.add_network_conf("network_interface")

        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                add_cluster, add_servers = self.check_service_mapping(service)
                if add_cluster is None:
                    add_cluster = _cluster
                config.add_machine(
                    roles=[service[NAME], layer[NAME], service["_id"]]
                    + service.get(ROLES, []),
                    flavour=add_cluster,
                    number=(
                        service[QUANTITY]
                        if QUANTITY in service
                        else DEFAULT_NODE_QUANTITY
                    ),
                )

        conf = config.finalize()
        logger.debug(f"CHAMELEON CLOUD [conf.to_dict()] = {conf.to_dict()}")
        provider = en.CBM(conf)
        return provider

    @staticmethod
    def __check_monitoring_request(infra_config):
        """Checks if a Service should be monitored --> roles: ['monitoring']."""
        services_to_monitor = []
        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                roles_monitoring = service.get(ROLES, [])
                if ROLES_MONITORING in roles_monitoring:
                    services_to_monitor.append(service[NAME])
        return services_to_monitor
