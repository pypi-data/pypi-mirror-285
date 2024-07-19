from pathlib import Path

import e2clab.infra as e2cinfra
from e2clab.constants import DEFAULT_SERVICE_NAME, G5K, LAYERS_SERVICES_CONF_FILE
from e2clab.providers.plugins.G5k import G5k
from e2clab.tests.unit import TestE2cLab

TEST_FILES_FOLDERS = Path(__file__).resolve().parent.parent / "test_files"
TEST_LAYERS_FILE = TEST_FILES_FOLDERS / LAYERS_SERVICES_CONF_FILE


class TestInfra(TestE2cLab):
    def setUp(self) -> None:
        self.config = self.test_folder / LAYERS_SERVICES_CONF_FILE

    def test_infra_init(self):
        infra = e2cinfra.Infrastructure(
            config=self.config,
            optimization_id=None,
        )
        self.assertIsInstance(infra, e2cinfra.Infrastructure)

    def test_infra_prepare(self):
        infra = e2cinfra.Infrastructure(
            config=self.config,
            optimization_id=None,
        )

        infra.prepare()

        self.assertEqual(infra.prov_to_load, [G5K])

        # true if no already imported services
        # self.assertEqual(infra.serv_to_load, [DEFAULT_SERVICE_NAME])
        self.assertIn(DEFAULT_SERVICE_NAME, infra.serv_to_load)

    def test_load_create_provider(self):
        infra = e2cinfra.Infrastructure(
            config=self.config,
            optimization_id=None,
        )
        infra.prepare()

        prov = infra._load_create_providers()
        self.assertEqual(len(prov), 1)
        self.assertIsInstance(prov[0], G5k)

    # def test_merge_dict(self):
    #     infra = e2cinfra.Infrastructure(
    #         config=self.config,
    #         optimization_id=None,
    #     )
    #     infra.prepare()

    #     infra._merge_dict()


# class TestInfra(TestE2cLab):
#     # TODO: redo test
#     def setUp(self):
#         self.config = e2cinfra.load_layers_conf(TEST_LAYERS_FILE)

#     def test_load_layers_conf(self):
#         config = e2cinfra.load_layers_conf(TEST_LAYERS_FILE)
#         self.assertIsInstance(config, dict)
#         self.assertIsInstance(config[LAYERS], list)
#         self.assertIsInstance(config[ENVIRONMENT], dict)
#         self.assertEqual(len(config[LAYERS]), 2)

#     def test_get_environments_to_load(self):
#         expected = ["g5k"]
#         output = e2cinfra.get_environments_to_load(self.config)
#         self.assertEqual(len(output), len(expected))
#         for env in output:
#             self.assertIn(env, expected)

#     def test_repeat_services(self):
#         configuration = f"""
#         {LAYERS}:
#         - {NAME}: cloud
#           {SERVICES}:
#           - {NAME}: Flink
#             quantity: 3
#           - {NAME}: Kafka
#             quantity: 3
#         - {NAME}: edge
#           {SERVICES}:
#           - {NAME}: Producer
#             quantity: 1
#             {REPEAT}: 1
#         """
#         local_config = yaml.safe_load(configuration)
#         num_expected_services = 4
#         e2cinfra.repeat_services(local_config)
#         num_services = 0
#         for layer in local_config[LAYERS]:
#             for _ in layer[SERVICES]:
#                 num_services += 1
#         self.assertEqual(num_services, num_expected_services)

#     def test_generate_service_id(self):
#         configuration = f"""
#         {LAYERS}:
#         - {NAME}: cloud
#           {SERVICES}:
#           - {NAME}: Flink
#           - {NAME}: Kafka
#         - {NAME}: edge
#           {SERVICES}:
#           - {NAME}: Producer
#           - {NAME}: Producer
#         """
#         local_config = yaml.safe_load(configuration)
#         e2cinfra.generate_service_id(infra_config=local_config)
#         self.assertEqual(local_config[LAYERS][0][SERVICES][1]["_id"], "1_2")
#         self.assertEqual(local_config[LAYERS][1][SERVICES][1]["_id"], "2_2")
#         self.assertEqual(local_config[LAYERS][1][SERVICES][0]["_id"], "2_1")

#     def test_create_providers_inst(self):
#         providers_to_create = SUPPORTED_ENVIRONMENTS
#         providers = e2cinfra.load_create_providers(
#             environments=providers_to_create,
#             infra_config={},
#             optimization_id=None,
#         )
#         for provider in providers:
#             self.assertIsInstance(provider, Provider)

#     def test_get_services_to_load(self):
#         configuration = f"""
#         {LAYERS}:
#         - {NAME}: cloud
#           {SERVICES}:
#           - {NAME}: Kafka
#           - {NAME}: Unknown2
#         - {NAME}: edge
#           {SERVICES}:
#           - {NAME}: Producer
#           - {NAME}: Producer
#         """
#         local_config = yaml.safe_load(configuration)
#         services_to_load, available_services = e2cinfra.get_services_to_load(
#             local_config
#         )
#         if "Kafka" in available_services:
#             self.assertEqual(services_to_load, ["Kafka", "Default"])
#         else:
#             self.assertEqual(services_to_load, ["Default"])
