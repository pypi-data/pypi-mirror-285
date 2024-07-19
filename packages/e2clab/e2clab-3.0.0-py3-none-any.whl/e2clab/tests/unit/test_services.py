from enoslib import Host

import e2clab.services as e2cserv
from e2clab.constants import ENV, NAME, QUANTITY
from e2clab.services.errors import E2clabServiceImportError
from e2clab.tests.unit import TestE2cLab


class TestServices(TestE2cLab):
    def test_get_available_services(self):
        available_services = e2cserv.get_available_services()
        self.assertIn("Default", available_services)

    def test_load_services(self):
        services_to_load = ["Default"]
        loaded_services = e2cserv.load_services(services_to_load)
        self.assertIn("Default", loaded_services.keys())
        default_service = loaded_services["Default"](
            hosts={}, layer_name="test", service_metadata={}
        )
        self.assertIsInstance(default_service, e2cserv.Service)

        with self.assertRaises(E2clabServiceImportError):
            e2cserv.load_services(["notaservice"])

    def test_default_service(self):
        services_to_load = ["Default"]
        loaded_services = e2cserv.load_services(services_to_load)
        # default_serv = loaded_services["Default"](
        loaded_services["Default"](
            hosts=[Host("127.0.0.1")],
            layer_name="edge",
            service_metadata={
                NAME: "Producer",
                "_id": "1_1_1",
                QUANTITY: 1,
                ENV: {"number": 34},
            },
        )
        # default_serv.deploy()
