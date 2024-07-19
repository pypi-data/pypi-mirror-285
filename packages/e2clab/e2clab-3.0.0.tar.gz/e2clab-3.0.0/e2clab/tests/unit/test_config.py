import e2clab.config as e2cconf
from e2clab.constants import (
    ANSIBLE_TASKS,
    CLUSTER,
    DSTAT_DEFAULT_OPTS,
    DSTAT_OPTIONS,
    ENVIRONMENT,
    G5K,
    JOB_NAME,
    LAYERS,
    MONITORING_SVC,
    MONITORING_SVC_AGENT_CONF,
    MONITORING_SVC_TIG,
    MONITORING_SVC_TYPE,
    NAME,
    NET_NETWORKS,
    PROVENANCE_SVC,
    PROVENANCE_SVC_DATAFLOW_SPEC,
    PROVENANCE_SVC_PROVIDER,
    REPEAT,
    SERVICES,
    WALLTIME,
    WORKFLOW_DEPENDS_ON,
    WORKFLOW_TARGET,
    WORKFLOW_TASK_FINALIZE,
    WORKFLOW_TASK_LAUNCH,
    WORKFLOW_TASK_PREPARE,
)
from e2clab.errors import E2clabConfigError
from e2clab.tests.unit import TestE2cLab


class TestConfig(TestE2cLab):

    def test_infra_config(self):
        with self.assertRaises(E2clabConfigError):
            not_a_conf = {"not_a_key": []}
            e2cconf.InfrastructureConfig(not_a_conf)

        df_spec = "dataflow_spec_file"

        valid_conf = {
            ENVIRONMENT: {
                JOB_NAME: "test",
                WALLTIME: "01:00:00",
                G5K: {CLUSTER: "parasilo"},
            },
            LAYERS: [
                {NAME: "cloud", SERVICES: [{NAME: "Exp", REPEAT: 3}]},
                {NAME: "edge", SERVICES: [{NAME: "Prod", REPEAT: 1}]},
            ],
            PROVENANCE_SVC: {
                PROVENANCE_SVC_PROVIDER: G5K,
                CLUSTER: "parasilo",
                PROVENANCE_SVC_DATAFLOW_SPEC: df_spec,
            },
            MONITORING_SVC: {MONITORING_SVC_TYPE: MONITORING_SVC_TIG},
        }
        conf = e2cconf.InfrastructureConfig(valid_conf)
        self.assertIsInstance(conf, dict)
        # Testing prepare method
        conf.prepare()
        self.assertEqual(len(conf[LAYERS][0][SERVICES]), 4)
        self.assertEqual(len(conf[LAYERS][1][SERVICES]), 2)
        self.assertEqual(conf[LAYERS][0][SERVICES][1]["_id"], "1_2")
        self.assertEqual(conf[LAYERS][1][SERVICES][0]["_id"], "2_1")

        # Testing default options
        self.assertTrue(conf.is_provenance_def())
        self.assertAlmostEqual(conf.get_provenance_parallelism(), 1)
        self.assertEqual(conf.get_dstat_options(), DSTAT_DEFAULT_OPTS)
        self.assertIsNone(conf.get_monitoring_agent_conf())

        valid_conf2 = {
            ENVIRONMENT: {
                JOB_NAME: "test",
                WALLTIME: "01:00:00",
                G5K: {CLUSTER: "parasilo"},
            },
            LAYERS: [
                {NAME: "cloud", SERVICES: [{NAME: "Exp", REPEAT: 3}]},
                {NAME: "edge", SERVICES: [{NAME: "Prod", REPEAT: 1}]},
            ],
            PROVENANCE_SVC: {
                PROVENANCE_SVC_PROVIDER: G5K,
                CLUSTER: "parasilo",
                PROVENANCE_SVC_DATAFLOW_SPEC: df_spec,
            },
            MONITORING_SVC: {
                MONITORING_SVC_TYPE: MONITORING_SVC_TIG,
                DSTAT_OPTIONS: "-m -c",
                MONITORING_SVC_AGENT_CONF: "conf",
            },
        }
        conf2 = e2cconf.InfrastructureConfig(valid_conf2)
        self.assertEqual(conf2.get_provenance_dataflow_spec(), df_spec)
        self.assertEqual(conf2.get_monitoring_agent_conf(), "conf")
        self.assertEqual(conf2.get_dstat_options(), "-m -c")

    def test_network_config(self):
        with self.assertRaises(E2clabConfigError):
            not_a_conf = {"notanetwork": []}
            e2cconf.NetworkConfig(not_a_conf)

        valid_conf = {NET_NETWORKS: None}
        conf = e2cconf.NetworkConfig(valid_conf)
        self.assertIsInstance(conf, dict)

    def test_workflow_config(self):
        with self.assertRaises(E2clabConfigError):
            not_a_conf = [{"notaworkflow": 0}]
            e2cconf.WorkflowConfig(not_a_conf)

        workflow_conf = [
            {
                WORKFLOW_TARGET: "cloud",
                WORKFLOW_DEPENDS_ON: [],
                WORKFLOW_TASK_PREPARE: [{"debug": {"msg": "test prepare"}}],
                WORKFLOW_TASK_LAUNCH: [{"debug": {"msg": "test launch"}}],
                WORKFLOW_TASK_FINALIZE: [{"debug": {"msg": "test finalize"}}],
            },
            {
                WORKFLOW_TARGET: "fog",
                WORKFLOW_DEPENDS_ON: [],
                WORKFLOW_TASK_PREPARE: [{"debug": {"msg": "test prepare"}}],
                WORKFLOW_TASK_FINALIZE: [{"debug": {"msg": "test finalize"}}],
            },
            {
                WORKFLOW_TARGET: "edge",
                WORKFLOW_DEPENDS_ON: [],
                WORKFLOW_TASK_PREPARE: [{"debug": {"msg": "test prepare"}}],
                WORKFLOW_TASK_LAUNCH: [{"debug": {"msg": "test launch"}}],
                WORKFLOW_TASK_FINALIZE: [{"debug": {"msg": "test finalize"}}],
            },
        ]

        conf = e2cconf.WorkflowConfig(workflow_conf)
        prepare_filtered = conf.get_task_filtered_host_config(WORKFLOW_TASK_PREPARE)
        launch_filtered = conf.get_task_filtered_host_config(WORKFLOW_TASK_LAUNCH)

        self.assertEqual(len(prepare_filtered), 3)
        self.assertEqual(len(launch_filtered), 2)
        self.assertIn(ANSIBLE_TASKS, prepare_filtered[0])
        self.assertIn(ANSIBLE_TASKS, launch_filtered[0])

        # Test can't filter a conf twice
        with self.assertRaises(Exception):
            launch_filtered.get_task_filtered_host_config(WORKFLOW_TASK_FINALIZE)

    def test_workflow_env_config(self):
        invalid_conf = {"base": {"A": {"B": 4}}}
        valid_conf = {
            "base": {"A": 5, "B": "hello"},
            "custom": {"A": 5, "B": "hello", "C": 4.2},
        }
        conf = e2cconf.WorkflowEnvConfig(valid_conf)
        with self.assertRaises(E2clabConfigError):
            e2cconf.WorkflowEnvConfig(invalid_conf)

        base_env = conf.get_env("base")
        no_env = conf.get_env("not_a_conf", {})

        self.assertEqual(no_env, {})
        self.assertEqual(base_env, {"env_A": 5, "env_B": "hello"})
