import enoslib as en

from e2clab.constants import NET_NETWORKS, NETWORK_CONF_FILE
from e2clab.errors import E2clabConfigError, E2clabFileError
from e2clab.network import Network
from e2clab.tests.unit import TestE2cLab


class TestUtils(TestE2cLab):

    def setUp(self) -> None:
        correct_conf = self.test_folder / NETWORK_CONF_FILE

        self.net = Network(config=correct_conf, roles=None, networks=None)

    def test_load_invalid_config(self):
        with self.assertRaises(E2clabConfigError):
            Network(
                config=self.test_folder / "invalid_network.yaml",
                roles=None,
                networks=None,
            )

        with self.assertRaises(E2clabFileError):
            Network(config="notafile", roles=None, networks=None)

    def test_check_edgeChameleonDevice(self):
        # Test normal case
        compss_hosts: en.Roles = en.Roles(
            {
                "cloud.compss.1.master.1 ": [en.Host(address="1.1.1.1")],
                "cloud.compss.1.worker.1 ": [en.Host(address="9.9.9.9")],
                "cloud.compss.1.worker.2 ": [en.Host(address="9.9.9.8")],
                "cloud.compss.1.worker.3 ": [en.Host(address="9.9.9.7")],
            }
        )

        compss_networks: en.Networks = en.Networks(
            dict(role=[en.DefaultNetwork(address="1.1.1.1/24")])
        )

        net = Network(
            config=self.test_folder / "network_compss.yaml",
            roles=compss_hosts,
            networks=compss_networks,
        )

        netconf = net.config[NET_NETWORKS][0]
        res = net._check_edgeChameleonDevice(netconf)
        self.assertFalse(res)

        # Case ChameleonDevices


#         compss_hosts: en.Roles = en.Roles(
#             {
#                 "cloud.compss.1.master.1 ": [en.Host(address="1.1.1.1")],
#                 "cloud.compss.1.worker.1 ": [
#                     ChameleonDevice(
#                         address="9.9.9.9", roles=["worker"], uuid="1234", rc_file="./"
#                     )
#                 ],
#                 "cloud.compss.1.worker.2 ": [
#                     ChameleonDevice(
#                         address="9.9.9.8", roles=["worker"], uuid="1234", rc_file="./"
#                     )
#                 ],
#                 "cloud.compss.1.worker.3 ": [
#                     ChameleonDevice(
#                         address="9.9.9.7", roles=["worker"], uuid="1234", rc_file="./"
#                     )
#                 ],
#             }
#         )

#         net = Network(
#             config=self.test_folder / "network_compss.yaml",
#             roles=compss_hosts,
#             networks=compss_networks,
#         )

#         netconf = net.config[NET_NETWORKS][0]
#         res = net._check_edgeChameleonDevice(netconf)
#         self.assertTrue(res)


# if __name__ == "__main__":
#     compss_hosts: en.Roles = en.Roles(
#         {
#             "cloud.compss.1.master.1 ": [en.Host(address="1.1.1.1")],
#             "cloud.compss.1.worker.1 ": [
#                 ChameleonDevice(
#                     address="9.9.9.9", roles=["worker"], uuid="1234", rc_file="./"
#                 )
#             ],
#             "cloud.compss.1.worker.2 ": [
#                 ChameleonDevice(
#                     address="9.9.9.8", roles=["worker"], uuid="1234", rc_file="./"
#                 )
#             ],
#             "cloud.compss.1.worker.3 ": [
#                 ChameleonDevice(
#                     address="9.9.9.7", roles=["worker"], uuid="1234", rc_file="./"
#                 )
#             ],
#         }
#     )

#     hosts = en.get_hosts(roles=compss_hosts, pattern_hosts="cloud.compss.1.worker.*")
#     print(hosts)
