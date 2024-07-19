import enoslib as en
from enoslib.infra.enos_iotlab.configuration import ConsumptionConfiguration

from e2clab.constants import (
    ARCHI,
    AVERAGE,
    AVERAGE_VALUES,
    CLUSTER,
    CURRENT,
    DEFAULT_IOTLAB_CLUSTER,
    DEFAULT_JOB_NAME,
    DEFAULT_NODE_QUANTITY,
    DEFAULT_PERIOD_VAL,
    DEFAULT_WALLTIME,
    ENVIRONMENT,
    IMAGE,
    IOT_LAB,
    JOB_NAME,
    LAYERS,
    MONITORING_IOTLAB,
    NAME,
    PERIOD,
    PERIOD_VALS,
    POWER,
    PROFILES,
    QUANTITY,
    ROLES,
    SERVICES,
    VOLTAGE,
    WALLTIME,
)
from e2clab.log import getLogger
from e2clab.providers import Provider

logger = getLogger(__name__, ["IOTLAB"])


class Iotlab(Provider):
    """
    The provider to use when deploying on FIT IoT LAB.
    """

    def init(self, testing: bool = False):
        """
        Take ownership over some FIT IoT LAB resources (compute and networks).
        :return: roles, networks
        """
        self.provider = self.__provider_iotlab(self.infra_config, self.optimization_id)

        if testing:
            return

        roles, networks = self.provider.init()
        en.wait_for(roles)

        roles = en.sync_info(roles, networks)

        if None in (roles, networks):
            raise ValueError(f"Failed to get resources from: {IOT_LAB}.")

        self.roles = roles
        self.networks = networks
        self.log_roles_networks(IOT_LAB)

        return roles, networks

    def destroy(self):
        # raise NotImplementedError
        self.provider.destroy()

    def __provider_iotlab(self, infra_config, optimization_id):
        self.refine_config_file(IOT_LAB)
        logger.info(f" layers_services [{IOT_LAB}] = {self.infra_config}")

        # _job_name = infra_config[ENVIRONMENT][JOB_NAME]
        #   if JOB_NAME in infra_config[ENVIRONMENT] else DEFAULT_JOB_NAME
        # _walltime = infra_config[ENVIRONMENT][WALLTIME]
        #   if WALLTIME in infra_config[ENVIRONMENT] else DEFAULT_WALLTIME
        # _cluster = infra_config[ENVIRONMENT][CLUSTER]
        #   if CLUSTER in infra_config[ENVIRONMENT] else DEFAULT_IOTLAB_CLUSTER

        _job_name = infra_config[ENVIRONMENT].get(JOB_NAME, DEFAULT_JOB_NAME)
        _walltime = infra_config[ENVIRONMENT].get(WALLTIME, DEFAULT_WALLTIME)
        _cluster = infra_config[ENVIRONMENT].get(CLUSTER, DEFAULT_IOTLAB_CLUSTER)

        config = en.IotlabConf.from_settings(
            job_name=(
                f"{_job_name}_{optimization_id}"
                if optimization_id is not None
                else _job_name
            ),
            walltime=_walltime,
        )

        """
            MONITORING
        """
        if MONITORING_IOTLAB in infra_config:
            for profile in infra_config[MONITORING_IOTLAB][PROFILES]:
                period = profile[PERIOD]
                average = profile[AVERAGE]
                if profile not in PERIOD_VALS:
                    def_period = DEFAULT_PERIOD_VAL
                    logger.warning(
                        "Invalid Iotlab monitor period: "
                        f"{period} defaulted to: {def_period}"
                    )
                    period = def_period
                if average not in AVERAGE_VALUES:
                    def_average = AVERAGE_VALUES[1]
                    logger.warning(
                        "Invalid Iotlab monitor average: "
                        f"{average} defaulted to: {def_average}"
                    )
                    average = def_average
                config.add_profile(
                    name=profile[NAME],
                    archi=profile[ARCHI],
                    consumption=ConsumptionConfiguration(
                        current=(
                            True if CURRENT in profile and profile[CURRENT] else False
                        ),
                        power=True if POWER in profile and profile[POWER] else False,
                        voltage=(
                            True if VOLTAGE in profile and profile[VOLTAGE] else False
                        ),
                        period=period,
                        average=average,
                    ),
                )

        """
            REQUEST RESOURCES
        """
        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                if not self.monitoring_provider:
                    self.monitoring_provider = True if "profile" in service else False
                add_cluster, add_servers = self.check_service_mapping(service)
                if add_cluster is None and add_servers is None:
                    add_cluster = _cluster
                if add_servers is not None:
                    config.add_machine(
                        roles=[service[NAME], layer[NAME], service["_id"]]
                        + service.get(ROLES, []),
                        hostname=add_servers,
                        image=service[IMAGE] if IMAGE in service else None,
                        profile=service["profile"] if "profile" in service else None,
                    )
                else:
                    config.add_machine(
                        roles=[service[NAME], layer[NAME], service["_id"]]
                        + service.get(ROLES, []),
                        archi=service[ARCHI],
                        site=add_cluster,
                        number=(
                            service[QUANTITY]
                            if QUANTITY in service
                            else DEFAULT_NODE_QUANTITY
                        ),
                        image=service[IMAGE] if IMAGE in service else None,
                        profile=service["profile"] if "profile" in service else None,
                    )

        conf = config.finalize()
        logger.debug(f"IOT LAB [conf.to_dict()] = {conf.to_dict()}")
        provider = en.Iotlab(conf)
        return provider
