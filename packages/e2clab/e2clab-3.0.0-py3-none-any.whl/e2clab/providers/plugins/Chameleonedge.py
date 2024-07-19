import enoslib as en
from enoslib.infra.enos_chameleonedge.configuration import Container

from e2clab.constants import (
    CHAMELEON_EDGE,
    CLUSTER,
    CONTAINER_NAME,
    CONTAINERS,
    DEFAULT_CHAMELEON_EDGE_CLUSTER,
    DEFAULT_CHIEDGE_IMAGE,
    DEFAULT_JOB_NAME,
    DEFAULT_NODE_QUANTITY,
    DEFAULT_WALLTIME,
    DEVICE_PROFILES,
    ENVIRONMENT,
    EXPOSED_PORTS,
    IMAGE,
    JOB_NAME,
    LAYERS,
    NAME,
    QUANTITY,
    RC_FILE,
    ROLES,
    SERVICES,
    START,
    START_TIMEOUT,
    WALLTIME,
)
from e2clab.log import getLogger
from e2clab.providers import Provider

logger = getLogger(__name__, ["CHAM_EDGE"])


class Chameleonedge(Provider):
    """
    The provider to use when deploying on Chameleon Edge.
    """

    def init(self, testing: bool = False):
        """
        Take ownership over some Chameleon Edge resources (compute).
        :return: roles, networks
        """
        self.provider = self.__provider_chameleonedge(
            infra_config=self.infra_config, optimization_id=self.optimization_id
        )

        if testing:
            return

        roles, networks = self.provider.init()
        # en.wait_for(roles)  # FIXME: Is it needed?

        # roles = en.sync_info(roles, networks)

        if None in (roles):
            raise ValueError(f"Failed to get resources from: {CHAMELEON_EDGE}.")

        self.roles = roles
        self.networks = networks
        self.log_roles_networks(CHAMELEON_EDGE)

        return roles, networks

    def destroy(self):
        self.provider.destroy()
        # raise NotImplementedError

    def __provider_chameleonedge(self, infra_config, optimization_id):
        self.refine_config_file(CHAMELEON_EDGE)
        logger.info(f" layers_services [{CHAMELEON_EDGE}] = {self.infra_config}")

        _job_name = (
            infra_config[ENVIRONMENT][JOB_NAME]
            if JOB_NAME in infra_config[ENVIRONMENT]
            else DEFAULT_JOB_NAME
        )
        _walltime = (
            infra_config[ENVIRONMENT][WALLTIME]
            if WALLTIME in infra_config[ENVIRONMENT]
            else DEFAULT_WALLTIME
        )
        _rc_file = (
            infra_config[ENVIRONMENT][RC_FILE]
            if RC_FILE in infra_config[ENVIRONMENT]
            else None
        )
        _image = (
            infra_config[ENVIRONMENT][IMAGE]
            if IMAGE in infra_config[ENVIRONMENT]
            else DEFAULT_CHIEDGE_IMAGE
        )
        _cluster = (
            infra_config[ENVIRONMENT][CLUSTER]
            if CLUSTER in infra_config[ENVIRONMENT]
            else DEFAULT_CHAMELEON_EDGE_CLUSTER
        )

        config = en.ChameleonEdgeConf.from_settings(
            lease_name=(
                f"{_job_name}_{optimization_id}"
                if optimization_id is not None
                else _job_name
            ),
            walltime=_walltime,
            rc_file=_rc_file,
        )

        """
            MONITORING
        """
        # clusters_to_monitor = check_monitoring_request(infra_config)

        """
            REQUEST RESOURCES
        """
        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                # containers
                _containers = service[CONTAINERS].copy()
                for _container in _containers:
                    container = Container(
                        name=_container.pop(NAME, CONTAINER_NAME),
                        image=_container.pop(IMAGE, _image),
                        exposed_ports=_container.pop(EXPOSED_PORTS, None),
                        start=_container.pop(START, True),
                        start_timeout=_container.pop(START_TIMEOUT, None),
                        device_profiles=_container.pop(DEVICE_PROFILES, None),
                        **_container,
                    )
                # devices
                add_cluster, add_servers = self.check_service_mapping(service)
                if add_cluster is None and add_servers is None:
                    add_cluster = _cluster
                if add_servers is not None:
                    config.add_machine(
                        roles=[service[NAME], layer[NAME], service["_id"]]
                        + service.get(ROLES, []),
                        device_name=add_servers,
                        container=container,
                    )
                else:
                    config.add_machine(
                        roles=[service[NAME], layer[NAME], service["_id"]]
                        + service.get(ROLES, []),
                        machine_name=add_cluster,
                        count=(
                            service[QUANTITY]
                            if QUANTITY in service
                            else DEFAULT_NODE_QUANTITY
                        ),
                        container=container,
                    )

        conf = config.finalize()
        logger.debug(f"CHAMELEON EDGE [conf.to_dict()] = {conf.to_dict()}")
        provider = en.ChameleonEdge(conf)
        return provider
