import enoslib as en
from enoslib.config import config_context
from enoslib.infra.enos_g5k.g5k_api_utils import get_cluster_site
from enoslib.objects import Host

from e2clab.constants import (
    CLUSTER,
    DEFAULT_JOB_NAME,
    DEFAULT_NODE_QUANTITY,
    DEFAULT_SSH_KEYFILE,
    DEFAULT_WALLTIME,
    ENV_NAME,
    ENVIRONMENT,
    FIREWALL_RULES,
    G5K,
    IPV,
    JOB_NAME,
    JOB_TYPE,
    JOB_TYPE_DEPLOY,
    KAVLAN,
    KAVLAN_GLOBAL,
    KEY_NAME,
    LAYERS,
    MONITORING_NETWORK_ROLE,
    MONITORING_SERVICE_ROLE,
    MONITORING_SVC,
    MONITORING_SVC_NETWORK,
    MONITORING_SVC_NETWORK_PRIVATE,
    MONITORING_SVC_PROVIDER,
    MONITORING_SVC_TIG,
    MONITORING_SVC_TPG,
    MONITORING_SVC_TYPE,
    NAME,
    PORTS,
    PROVENANCE_SERVICE_ROLE,
    PROVENANCE_SVC,
    PROVENANCE_SVC_PROVIDER,
    QUANTITY,
    RESERVATION,
    ROLES,
    ROLES_MONITORING,
    SERVERS,
    SERVICES,
    WALLTIME,
)
from e2clab.log import getLogger
from e2clab.providers import Provider

logger = getLogger(__name__, ["G5K"])


class G5k(Provider):
    """
    The provider to use when deploying on Grid'5000.
    """

    def init(self, testing: bool = False):
        """
        Take ownership over some Grid'5000 resources (compute and networks).
        :return: roles, networks
        """
        with config_context(g5k_cache=False):
            provider = self.__provider_g5k(self.infra_config, self.optimization_id)

        self.provider = provider

        if testing:
            return

        roles, networks = provider.init()
        en.wait_for(roles)

        if (
            MONITORING_SVC in self.infra_config
            and IPV in self.infra_config[MONITORING_SVC]
            and self.infra_config[MONITORING_SVC][IPV] == 6
        ) or (
            PROVENANCE_SVC in self.infra_config
            and IPV in self.infra_config[PROVENANCE_SVC]
            and self.infra_config[PROVENANCE_SVC][IPV] == 6
        ):
            roles = en.sync_info(roles, networks)
            _hosts = []
            for h in roles[G5K]:
                _hosts.append(h)
            self.__enable_ipv6_network(_hosts)

        roles = en.sync_info(roles, networks)

        if FIREWALL_RULES in self.infra_config[ENVIRONMENT]:
            self.__apply_firewall_rules(provider, roles)

        if None in (roles, networks):
            raise ValueError(f"Failed to get resources from: {G5K}.")

        self.roles = roles
        self.networks = networks
        self.log_roles_networks(G5K)

        return roles, networks

    def __provider_g5k(self, infra_config, optimization_id) -> en.G5k:
        self.refine_config_file(G5K)
        logger.debug(f" layers_services [{G5K}] = {self.infra_config}")

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
        _reservation = (
            infra_config[ENVIRONMENT][RESERVATION]
            if (RESERVATION in infra_config[ENVIRONMENT])
            else None
        )
        _job_type = (
            infra_config[ENVIRONMENT][JOB_TYPE]
            if (JOB_TYPE in infra_config[ENVIRONMENT])
            else [JOB_TYPE_DEPLOY]
        )
        _env_name = (
            infra_config[ENVIRONMENT][ENV_NAME]
            if (ENV_NAME in infra_config[ENVIRONMENT])
            else None
        )
        _cluster = (
            infra_config[ENVIRONMENT][CLUSTER]
            if (CLUSTER in infra_config[ENVIRONMENT])
            else None
        )
        _keyfile = (
            infra_config[ENVIRONMENT][KEY_NAME]
            if (KEY_NAME in infra_config[ENVIRONMENT])
            else DEFAULT_SSH_KEYFILE
        )

        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                add_cluster, add_servers = self.check_service_mapping(service)
                if add_cluster is None and add_servers is None and _cluster is None:
                    raise Exception(
                        "Fix your 'layers_services.yaml' file. "
                        "Specify a 'CLUSTER' or 'SERVERS' "
                        "for each 'service' or specify "
                        "a default 'CLUSTER' in 'g5k:'."
                    )

        config = en.G5kConf.from_settings(
            job_type=_job_type,
            env_name=_env_name,
            job_name=(
                f"{_job_name}_{optimization_id}"
                if optimization_id is not None
                else _job_name
            ),
            reservation=_reservation,
            walltime=_walltime,
            key=_keyfile,
        )

        # group all clusters
        clusters = self.__search_clusters_at_service_level(infra_config, _cluster)
        # create network (type="prod") for all clusters
        prod_network = self.__create_production_network_for_clusters(clusters)
        for site, network in prod_network.items():
            config.add_network_conf(network)

        """
            PROVENANCE
        """
        if PROVENANCE_SVC in infra_config:
            """Add G5k node as PROVENANCE provider: 1 machine"""
            if infra_config[PROVENANCE_SVC][PROVENANCE_SVC_PROVIDER] == G5K:
                self.provenance_provider = True
                # identify the cluster of the provenance provider
                if (
                    CLUSTER not in infra_config[PROVENANCE_SVC]
                    and SERVERS not in infra_config[PROVENANCE_SVC]
                ):
                    raise Exception("Specify a 'CLUSTER' or 'SERVER' in provenance")
                elif CLUSTER in infra_config[PROVENANCE_SVC]:
                    _provenance_cluster = infra_config[PROVENANCE_SVC][CLUSTER]
                else:
                    _provenance_cluster = self.__get_clusters_from_servers(
                        [infra_config[PROVENANCE_SVC][SERVERS][0]]
                    )[0]
                # create a production network (type="prod")
                if get_cluster_site(_provenance_cluster) not in prod_network:
                    prod_network.update(
                        self.__create_production_network_for_clusters(
                            [_provenance_cluster]
                        )
                    )
                    config.add_network_conf(
                        prod_network[get_cluster_site(_provenance_cluster)]
                    )

                if CLUSTER in infra_config[PROVENANCE_SVC]:
                    config.add_machine(
                        roles=[G5K, PROVENANCE_SERVICE_ROLE],
                        cluster=infra_config[PROVENANCE_SVC][CLUSTER],
                        primary_network=prod_network[
                            get_cluster_site(_provenance_cluster)
                        ],
                    )
                else:
                    config.add_machine(
                        roles=[G5K, PROVENANCE_SERVICE_ROLE],
                        servers=[infra_config[PROVENANCE_SVC][SERVERS][0]],
                        primary_network=prod_network[
                            get_cluster_site(_provenance_cluster)
                        ],
                    )

        """
            MONITORING
        """
        clusters_to_monitor = self.__check_monitoring_request(infra_config, _cluster)
        logger.info(f"clusters to monitor = {clusters_to_monitor}")
        is_monitoring_in_private_network = False

        """
            MONITORING NETWORK
            1 monitoring network[kavlan,kavlan-global]
            1 production network
        """
        if MONITORING_SVC in infra_config and infra_config[MONITORING_SVC][
            MONITORING_SVC_TYPE
        ] in [MONITORING_SVC_TIG, MONITORING_SVC_TPG]:
            """Add G5k node as monitoring provider: 1 machine[ui,collector]"""
            if infra_config[MONITORING_SVC][MONITORING_SVC_PROVIDER] == G5K:
                self.monitoring_provider = True
                # If "is_monitoring_in_private_network == False"
                # it will use just one NIC,
                # otherwise it will use 2 NICs
                is_monitoring_in_private_network = (
                    True
                    if (
                        infra_config[MONITORING_SVC][MONITORING_SVC_NETWORK]
                        == MONITORING_SVC_NETWORK_PRIVATE
                    )
                    else False
                )
                # identify the cluster of the monitoring provider
                if (
                    CLUSTER not in infra_config[MONITORING_SVC]
                    and SERVERS not in infra_config[MONITORING_SVC]
                ):
                    raise Exception("Specify a 'CLUSTER' or 'SERVER' in monitoring")
                elif CLUSTER in infra_config[MONITORING_SVC]:
                    _monitor_cluster = infra_config[MONITORING_SVC][CLUSTER]
                else:
                    _monitor_cluster = self.__get_clusters_from_servers(
                        [infra_config[MONITORING_SVC][SERVERS][0]]
                    )[0]
                # create a monitoring network (type=KAVLAN_GLOBAL or type=KAVLAN)
                if is_monitoring_in_private_network:
                    monitoring_network = self.__create_monitoring_network(
                        _monitor_cluster, clusters_to_monitor
                    )
                    config.add_network_conf(monitoring_network)
                # create a production network (type="prod")
                if get_cluster_site(_monitor_cluster) not in prod_network:
                    prod_network.update(
                        self.__create_production_network_for_clusters(
                            [_monitor_cluster]
                        )
                    )
                    config.add_network_conf(
                        prod_network[get_cluster_site(_monitor_cluster)]
                    )

                if CLUSTER in infra_config[MONITORING_SVC]:
                    config.add_machine(
                        roles=[G5K, MONITORING_SERVICE_ROLE],
                        cluster=infra_config[MONITORING_SVC][CLUSTER],
                        primary_network=prod_network[
                            get_cluster_site(_monitor_cluster)
                        ],
                        secondary_networks=(
                            [monitoring_network]
                            if is_monitoring_in_private_network
                            else None
                        ),
                    )
                else:
                    config.add_machine(
                        roles=[G5K, MONITORING_SERVICE_ROLE],
                        servers=[infra_config[MONITORING_SVC][SERVERS][0]],
                        primary_network=prod_network[
                            get_cluster_site(_monitor_cluster)
                        ],
                        secondary_networks=(
                            [monitoring_network]
                            if is_monitoring_in_private_network
                            else None
                        ),
                    )

        """
            REQUEST RESOURCES
        """
        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                add_cluster, add_servers = self.check_service_mapping(service)
                if add_cluster is None and add_servers is None:
                    add_cluster = _cluster
                if add_servers is not None:
                    for (
                        server_cluster,
                        servers_in_cluster,
                    ) in self.__separate_servers_per_cluster(add_servers).items():
                        config.add_machine(
                            roles=[G5K, service[NAME], layer[NAME], service["_id"]]
                            + service.get(ROLES, []),
                            servers=servers_in_cluster,
                            primary_network=prod_network[
                                get_cluster_site(server_cluster)
                            ],
                            secondary_networks=(
                                [monitoring_network]
                                if is_monitoring_in_private_network
                                and ROLES_MONITORING in service.get(ROLES, [])
                                else None
                            ),
                        )
                else:
                    config.add_machine(
                        roles=[G5K, service[NAME], layer[NAME], service["_id"]]
                        + service.get(ROLES, []),
                        cluster=add_cluster,
                        nodes=(
                            service[QUANTITY]
                            if QUANTITY in service
                            else DEFAULT_NODE_QUANTITY
                        ),
                        primary_network=prod_network[get_cluster_site(add_cluster)],
                        secondary_networks=(
                            [monitoring_network]
                            if is_monitoring_in_private_network
                            and ROLES_MONITORING in service.get(ROLES, [])
                            else None
                        ),
                    )

        conf = config.finalize()
        logger.debug(f"G5K [conf.to_dict()] = {conf.to_dict()}")
        provider = en.G5k(conf)
        return provider

    def __check_monitoring_request(self, infra_config, _cluster):
        """Checks if a Service should be monitored --> roles: ['monitoring']."""
        clusters_to_monitor = []
        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                roles_monitoring = service.get(ROLES, [])
                if ROLES_MONITORING in roles_monitoring:
                    self.__search_for_clusters(service, clusters_to_monitor, _cluster)
        return clusters_to_monitor

    def __search_clusters_at_service_level(self, infra_config, _cluster):
        """Searches the clusters a Service belongs to."""
        clusters = []
        for layer in infra_config[LAYERS]:
            for service in layer[SERVICES]:
                self.__search_for_clusters(service, clusters, _cluster)
        return clusters

    def __search_for_clusters(self, service, clusters, _cluster):
        """
        Checks the 'cluster' and 'servers' attributes of a Service to get its
        clusters.
        """
        if CLUSTER in service and service[CLUSTER] not in clusters:
            clusters.append(service[CLUSTER])
        elif SERVERS in service:
            for cluster_name in self.__get_clusters_from_servers(service[SERVERS]):
                if cluster_name not in clusters:
                    clusters.append(cluster_name)
        elif _cluster and _cluster not in clusters:
            clusters.append(_cluster)
        return clusters

    def __create_monitoring_network(self, _cluster, clusters_to_monitor):
        if _cluster not in clusters_to_monitor:
            clusters_to_monitor.append(_cluster)
        sites_to_monitor = self.__get_sites_from_clusters(clusters_to_monitor)
        _site = get_cluster_site(_cluster)
        monitoring_network_type = KAVLAN_GLOBAL if len(sites_to_monitor) > 1 else KAVLAN
        return en.G5kNetworkConf(
            id=f"monitoring_network_{_site}",
            type=monitoring_network_type,
            roles=[MONITORING_NETWORK_ROLE],
            site=_site,
        )

    def __apply_firewall_rules(self, provider, roles):
        """
        Reconfigurable firewall on G5K allows you to open some ports of some of your
        Services.
        Allows connections from other environments (e.g., FIT IoT, Chameleon, etc.)
        to G5K.
        """
        try:
            for fw_rule in self.infra_config[ENVIRONMENT][FIREWALL_RULES]:
                svcs = []
                for scv in fw_rule[SERVICES]:
                    svcs += roles[scv]
                try:
                    provider.fw_create(
                        hosts=svcs, port=fw_rule[PORTS], src_addr=None, proto="tcp+udp"
                    )
                except Exception as e:
                    if "already exists" not in str(e):
                        raise e
        except Exception as e:
            raise e

    @staticmethod
    def __create_production_network_for_clusters(clusters):
        """Creates site-level networks for clusters."""
        networks = {}
        for cluster in clusters:
            _site = get_cluster_site(cluster)
            if _site not in networks:
                networks[_site] = en.G5kNetworkConf(
                    id=f"network_{_site}",
                    type="prod",
                    roles=[f"my_{_site}_network"],
                    site=_site,
                )
        return networks

    @staticmethod
    def __get_clusters_from_servers(servers):
        """
        In G5k a server is named like: '<cluster>-<index>.<site>.grid5000.fr'.
        """
        clusters = []
        for server in servers:
            cluster_name = server.split("-")[0]
            if cluster_name not in clusters:
                clusters.append(cluster_name)
        return clusters

    @staticmethod
    def __separate_servers_per_cluster(servers):
        servers_per_cluster = {}
        clusters = []
        for server in servers:
            cluster_name = server.split("-")[0]
            if cluster_name not in clusters:
                clusters.append(cluster_name)
        for cl in clusters:
            servers_per_cluster.update({cl: []})
            for server in servers:
                if cl in server:
                    servers_per_cluster[cl].append(server)
        return servers_per_cluster

    @staticmethod
    def __get_sites_from_clusters(clusters):
        _sites = []
        for c in clusters:
            site = get_cluster_site(c)
            if site not in _sites:
                _sites.append(site)
        return _sites

    def __enable_ipv6_network(self, _hosts):
        for _host in _hosts:
            for routable_nic in self.get_host_routable_nic(_host):
                en.run(f"dhclient -6 {routable_nic}", roles=_host)
                break

    @staticmethod
    def get_host_routable_nic(host: Host):
        routable_nic = []
        for net_device in host.net_devices:
            for _address in net_device.addresses:
                if _address.network and _address.ip.version in [4]:
                    routable_nic.append(str(net_device.name))
                    break
        return routable_nic

    # Test freeing resources in
    def destroy(self):
        self.provider.destroy()
