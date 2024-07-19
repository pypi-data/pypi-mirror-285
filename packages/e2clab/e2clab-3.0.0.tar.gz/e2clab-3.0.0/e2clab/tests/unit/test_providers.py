import e2clab.providers as e2cprov
from e2clab.config import InfrastructureConfig
from e2clab.constants import (
    ARCHI,
    AVERAGE,
    CHAMELEON_CLOUD,
    CHAMELEON_EDGE,
    CLUSTER,
    CONTAINERS,
    CURRENT,
    ENV_NAME,
    ENVIRONMENT,
    G5K,
    IMAGE,
    IOT_LAB,
    JOB_NAME,
    JOB_TYPE,
    KEY_NAME,
    LAYERS,
    MONITORING_IOTLAB,
    MONITORING_SVC,
    MONITORING_SVC_NETWORK,
    MONITORING_SVC_NETWORK_PRIVATE,
    MONITORING_SVC_PROVIDER,
    MONITORING_SVC_TIG,
    MONITORING_SVC_TYPE,
    NAME,
    PERIOD,
    POWER,
    PROFILES,
    PROVENANCE_SVC,
    PROVENANCE_SVC_DATAFLOW_SPEC,
    PROVENANCE_SVC_PARALLELISM,
    PROVENANCE_SVC_PROVIDER,
    QUANTITY,
    RC_FILE,
    ROLES,
    SERVERS,
    SERVICES,
    SUPPORTED_ENVIRONMENTS,
    VOLTAGE,
    WALLTIME,
)
from e2clab.providers.errors import E2clabProviderImportError
from e2clab.providers.plugins.Chameleoncloud import Chameleoncloud
from e2clab.providers.plugins.Chameleonedge import Chameleonedge
from e2clab.providers.plugins.G5k import G5k
from e2clab.providers.plugins.Iotlab import Iotlab
from e2clab.tests.unit import TestE2cLab


# TODO: improve testing by checking default configurations
class TestProviders(TestE2cLab):
    def test_get_available_providers(self):
        available_providers = e2cprov.get_available_providers()
        for prov in SUPPORTED_ENVIRONMENTS:
            self.assertIn(prov.capitalize(), available_providers)

    def test_load_providers(self):
        providers_to_load = [prov.capitalize() for prov in SUPPORTED_ENVIRONMENTS]
        loaded_providers = e2cprov.load_providers(providers_to_load)
        self.assertEqual(set(providers_to_load), set(loaded_providers.keys()))
        for prov in providers_to_load:
            provider_inst = loaded_providers[prov](
                infra_config={}, optimization_id=None
            )
            self.assertIsInstance(provider_inst, e2cprov.Provider)

        with self.assertRaises(E2clabProviderImportError):
            e2cprov.load_providers(["notaprovider"])

    def test_G5k(self):
        """Tetsting a G5K setup"""
        loaded_prov = e2cprov.load_providers(["G5k"])
        g5k_class = loaded_prov["G5k"]

        g5k_config = {
            ENVIRONMENT: {
                JOB_NAME: "test",
                WALLTIME: "01:00:00",
                G5K: {
                    JOB_TYPE: ["deploy"],
                    CLUSTER: "parasilo",
                    ENV_NAME: "debian11-min",
                },
            },
            PROVENANCE_SVC: {
                PROVENANCE_SVC_PROVIDER: G5K,
                PROVENANCE_SVC_PARALLELISM: 1,
                CLUSTER: "parasilo",
                PROVENANCE_SVC_DATAFLOW_SPEC: "dataflow-spec.py",
            },
            MONITORING_SVC: {
                MONITORING_SVC_TYPE: MONITORING_SVC_TIG,
                MONITORING_SVC_PROVIDER: G5K,
                CLUSTER: "parasilo",
                MONITORING_SVC_NETWORK: MONITORING_SVC_NETWORK_PRIVATE,
            },
            LAYERS: [
                {
                    NAME: "cloud",
                    SERVICES: [{NAME: "Server", QUANTITY: 1, CLUSTER: "paravance"}],
                },
                {
                    NAME: "fog",
                    SERVICES: [
                        {
                            NAME: "Gateway",
                            QUANTITY: 1,
                            SERVERS: ["parasilo-14.rennes.grid5000.fr"],
                        }
                    ],
                },
                {
                    NAME: "edge",
                    SERVICES: [
                        {
                            NAME: "Producer",
                            QUANTITY: 1,
                            ENVIRONMENT: IOT_LAB,
                        }
                    ],
                },
            ],
        }

        g5k_config = InfrastructureConfig(g5k_config)
        g5k_config.prepare()

        g5k: G5k = g5k_class(infra_config=g5k_config, optimization_id=None)

        self.assertIsInstance(g5k, G5k)
        g5k.init(testing=True)

        prov_conf_dict = g5k.provider.provider_conf.to_dict()
        self.assertEqual(prov_conf_dict["job_name"], "test")
        self.assertEqual(prov_conf_dict["walltime"], "01:00:00")
        # 2 services + 1 monitor + 1 provider
        self.assertEqual(len(prov_conf_dict["resources"]["machines"]), 4)

    @TestE2cLab.skip_on_runner()
    def test_iot_lab(self):
        """Testing a IotLab setup"""
        loaded_prov = e2cprov.load_providers(["Iotlab"])
        iotlab_prov = loaded_prov["Iotlab"]

        iotlab_config = {
            ENVIRONMENT: {
                JOB_NAME: "test",
                WALLTIME: "01:00:00",
                IOT_LAB: {
                    CLUSTER: "grenoble",
                },
            },
            MONITORING_IOTLAB: {
                PROFILES: [
                    {
                        NAME: "test_capture",
                        ARCHI: "a8",
                        PERIOD: 1100,
                        AVERAGE: 512,
                        VOLTAGE: True,
                    }
                ]
            },
            LAYERS: [
                {
                    NAME: "cloud",
                    SERVICES: [{NAME: "Server", ENVIRONMENT: G5K}],
                },
                {NAME: "edge", SERVICES: [{NAME: "Producer", ARCHI: "a8:at86rf231"}]},
            ],
        }

        iotlab_config = InfrastructureConfig(iotlab_config)
        iotlab_config.prepare()

        iotlab: Iotlab = iotlab_prov(infra_config=iotlab_config, optimization_id=None)

        self.assertIsInstance(iotlab, Iotlab)
        iotlab.init(testing=True)

        prov_conf_dict = iotlab.provider.provider_conf.to_dict()
        self.assertEqual(prov_conf_dict["job_name"], "test")
        self.assertTrue(
            prov_conf_dict["monitoring"]["profiles"][0]["consumption"][VOLTAGE]
        )
        self.assertFalse(
            prov_conf_dict["monitoring"]["profiles"][0]["consumption"][CURRENT]
        )
        self.assertFalse(
            prov_conf_dict["monitoring"]["profiles"][0]["consumption"][POWER]
        )
        self.assertEqual(prov_conf_dict["walltime"], "01:00:00")
        self.assertEqual(len(prov_conf_dict["resources"]["machines"]), 1)

    @TestE2cLab.skip_on_runner()
    def test_chameleon_cloud(self):
        """Testing a Chameleon Cloud setup"""
        loaded_prov = e2cprov.load_providers(["Chameleoncloud"])
        chamcloud_prov = loaded_prov["Chameleoncloud"]

        chameleoncloud_config = {
            ENVIRONMENT: {
                JOB_NAME: "test",
                WALLTIME: "01:00:00",
                CHAMELEON_CLOUD: {
                    RC_FILE: "~/rc_file.sh",
                    IMAGE: "CC-Ubuntu20.04",
                    KEY_NAME: "id_rsa.pub",
                    CLUSTER: "compute_skylake",
                },
            },
            MONITORING_SVC: {
                MONITORING_SVC_TYPE: MONITORING_SVC_TIG,
                MONITORING_SVC_PROVIDER: CHAMELEON_CLOUD,
                CLUSTER: "compute_skylake",
            },
            LAYERS: [
                {NAME: "cloud", SERVICES: [{NAME: "server", ROLES: ["monitoring"]}]}
            ],
        }

        chameleoncloud_config = InfrastructureConfig(chameleoncloud_config)
        chameleoncloud_config.prepare()

        chameleon_cloud: Chameleoncloud = chamcloud_prov(
            infra_config=chameleoncloud_config, optimization_id=None
        )

        self.assertIsInstance(chameleon_cloud, Chameleoncloud)
        chameleon_cloud.init(testing=True)

        raw_provider = chameleon_cloud.provider
        prov_conf_dict = raw_provider.provider_conf.to_dict()

        # What is happening here ?
        # self.assertEqual(prov_conf_dict["lease_name"], "test")
        # self.assertEqual(prov_conf_dict["walltime"], "01:00:00")
        self.assertEqual(prov_conf_dict["rc_file"], "~/rc_file.sh")

        # 1 more machine for monitoring
        self.assertEqual(len(prov_conf_dict["resources"]["machines"]), 2)

    @TestE2cLab.skip_on_runner()
    def test_chameleon_edge(self):
        """Testing a Chameleon Edge setup"""
        loaded_prov = e2cprov.load_providers(["Chameleonedge"])
        chamedge_prov = loaded_prov["Chameleonedge"]

        chameleondege_config = {
            ENVIRONMENT: {
                JOB_NAME: "test",
                WALLTIME: "01:00:00",
                CHAMELEON_EDGE: {
                    RC_FILE: "~/rc_file.sh",
                    IMAGE: "CC-Ubuntu20.04",
                    KEY_NAME: "id_rsa.pub",
                },
            },
            LAYERS: [
                {
                    NAME: "edge",
                    SERVICES: [
                        {
                            NAME: "producer",
                            ENVIRONMENT: CHAMELEON_EDGE,
                            SERVERS: "iot-rpi4-02",
                            CONTAINERS: [
                                {NAME: "cli-container", IMAGE: "arm64v8/ubuntu"}
                            ],
                        }
                    ],
                }
            ],
        }

        chameleonedge_config = InfrastructureConfig(chameleondege_config)
        chameleonedge_config.prepare()

        chameleon_edge: Chameleonedge = chamedge_prov(
            infra_config=chameleonedge_config, optimization_id=None
        )

        self.assertIsInstance(chameleon_edge, Chameleonedge)
        chameleon_edge.init(testing=True)

        prov_conf_dict = chameleon_edge.provider.provider_conf.to_dict()
        self.assertEqual(prov_conf_dict["lease_name"], "test")
        self.assertEqual(prov_conf_dict["rc_file"], "~/rc_file.sh")
        self.assertEqual(prov_conf_dict["walltime"], "01:00:00")
        self.assertEqual(len(prov_conf_dict["resources"]["machines"]), 1)
