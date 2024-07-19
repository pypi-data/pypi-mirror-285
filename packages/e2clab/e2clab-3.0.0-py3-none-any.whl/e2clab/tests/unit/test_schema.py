import jsonschema
import jsonschema.exceptions

import e2clab.schemas as e2cschema
from e2clab.constants import (
    LAYERS_SERVICES_CONF_FILE,
    NETWORK_CONF_FILE,
    WORKFLOW_CONF_FILE,
)
from e2clab.tests.unit import TestE2cLab
from e2clab.utils import load_yaml_file


class TestSchema(TestE2cLab):

    def test_is_valid_conf(self):
        netconf = load_yaml_file(self.test_folder / NETWORK_CONF_FILE)
        invalid_netconf = load_yaml_file(self.test_folder / "invalid_network.yaml")
        # Test correct configuration
        self.assertTrue(e2cschema.is_valid_conf(netconf, "network"))
        # Test an invalid netconf
        self.assertFalse(e2cschema.is_valid_conf(invalid_netconf, "network"))
        # Test an invalid "conference type input"
        self.assertFalse(e2cschema.is_valid_conf(netconf, "not_a_conf_type"))
        # Test an incorrect configuration match
        self.assertFalse(e2cschema.is_valid_conf(netconf, "workflow"))

    def test_network_schema(self):
        netconf = load_yaml_file(self.test_folder / NETWORK_CONF_FILE)
        invalid_netconf = load_yaml_file(self.test_folder / "invalid_network.yaml")
        # Test correct configuration
        try:
            result = e2cschema.is_valid_conf(netconf, "network")
        except jsonschema.exceptions.SchemaError as e:
            self.fail(f"Invalid schema definition : {e}")
        self.assertTrue(result)
        self.assertFalse(e2cschema.is_valid_conf(invalid_netconf, "network"))

    def test_workflow_schema(self):
        workconf = load_yaml_file(self.test_folder / WORKFLOW_CONF_FILE)
        invalid_workconf = load_yaml_file(self.test_folder / "invalid_workflow.yaml")
        try:
            result = e2cschema.is_valid_conf(workconf, "workflow")
        except jsonschema.exceptions.SchemaError as e:
            self.fail(f"Invalid schema definition : {e}")
        self.assertTrue(result)
        self.assertFalse(e2cschema.is_valid_conf(invalid_workconf, "workflow"))

    def test_layers_services_schema(self):
        layersconf = load_yaml_file(self.test_folder / LAYERS_SERVICES_CONF_FILE)
        invalid_kayersconf = load_yaml_file(
            self.test_folder / "invalid_layers_services.yaml"
        )
        try:
            result = e2cschema.is_valid_conf(layersconf, "layers_services")
        except jsonschema.exceptions.SchemaError as e:
            self.fail(f"Invalid schema definition : {e}")
        self.assertTrue(result)
        self.assertFalse(e2cschema.is_valid_conf(invalid_kayersconf, "layers_services"))
