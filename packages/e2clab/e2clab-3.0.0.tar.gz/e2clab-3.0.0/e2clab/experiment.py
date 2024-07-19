import time
from pathlib import Path
from typing import Optional
from uuid import UUID

import yaml

from e2clab.app import App
from e2clab.constants import (
    CHAMELEON_CLOUD,
    LAYERS,
    LAYERS_SERVICES_CONF_FILE,
    LAYERS_SERVICES_VALIDATE_FILE,
    MONITORING_SERVICE_ROLE,
    MONITORING_SVC,
    MONITORING_SVC_PORT,
    MONITORING_SVC_PROVIDER,
    NAME,
    NETWORK_CONF_FILE,
    PROVENANCE_SERVICE_ROLE,
    PROVENANCE_SVC_PORT,
    ROLES_MONITORING,
    SERVICES,
    WORKFLOW_CONF_FILE,
    WORKFLOW_ENV_CONF_FILE,
    WORKFLOW_TASK_FINALIZE,
    WORKFLOW_TASK_LAUNCH,
    WORKFLOW_TASK_PREPARE,
)
from e2clab.infra import Infrastructure
from e2clab.log import config_file_logger, getLogger
from e2clab.network import Network


class Experiment:

    def __init__(
        self,
        scenario_dir: Path,
        artifacts_dir: Path,
        repeat: int = None,
        app_conf_list: list[str] = [],
        optimization_config=None,
        optimization_id: Optional[UUID] = None,
    ) -> None:

        self.id = time.strftime("%Y%m%d-%H%M%S")
        self.scenario_dir = scenario_dir.resolve()
        self.artifacts_dir = artifacts_dir.resolve()

        # 'Deploy' related
        self.app_conf_list = app_conf_list
        self.repeat = repeat

        # 'Optimization' related
        self.optimization_id = optimization_id
        self.optimization_config = optimization_config

        self.logger = getLogger(__name__, ["EXP"])

        # Experiment components
        self.infra = None
        self.net = None
        self.app = None

    def initiate(self) -> None:
        self.monitoring_remote_working_dir = (
            f"/builds/monitoring-{self.id}-{self.scenario_dir.stem}"
        )
        # FILE USED BY USERS TO DEPLOY THEIR APPLICATIONS
        self.experiment_dir = Path(f"{self.scenario_dir}/{self.id}")
        self.experiment_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Experiment directory is: {self.experiment_dir}")
        # Outputing e2clab logs into experiment dir
        log_file, error_file = config_file_logger(self.experiment_dir)
        self.logger.info(f"Logging file at {log_file}")
        self.logger.info(f"Error file at {error_file}")

        self.layers_services_val_file = (
            self.experiment_dir / LAYERS_SERVICES_VALIDATE_FILE
        )

    def infrastructure(self) -> int:
        """
        Deploy experiment infrastructure
        """
        self.logger.info("Deploying experiment inrastructure")

        conf_file = self.scenario_dir / LAYERS_SERVICES_CONF_FILE

        # Infrastructure
        self.logger.debug("Init infrastructure")
        self.infra = Infrastructure(conf_file, self.optimization_id)
        self.logger.debug("Preparing infrastructure")
        self.infra.prepare()
        self.logger.debug("Deploying infrastructure")
        roles, networks = self.infra.deploy(
            artifacts_dir=self.artifacts_dir,
            remote_working_dir=self.monitoring_remote_working_dir,
        )
        self.logger.info("Experiment infrastructure deployed")

        self.roles = roles
        self.networks = networks

        # Generate Layers Services validate file
        # application_parameters(app_param_dir, self.infra.roles, self.infra.config)
        self._dump_application_parameters()

        return self.id

    def network(self) -> None:
        """
        Deploy experiment network emulation
        """
        if not self.infra:
            self.logger.error(
                "Cannot deploy a network without a deployed infrastructure"
            )
            return

        self.logger.info("Deploying experiment network")

        conf_file = self.scenario_dir / NETWORK_CONF_FILE

        # Network
        self.logger.debug("Init network")
        self.net = Network(conf_file, self.roles, self.networks)
        self.logger.debug("Preparing network")
        self.net.prepare()
        self.logger.debug("Deploying network")
        self.net.deploy()
        self.logger.debug("Validating network")
        self.net.validate(self.experiment_dir)

        self.logger.info("Experiment network deployed")

    def application(self, task: str, app_conf: str = None) -> None:
        """
        Enforce workflow definition
        """
        if not self.infra:
            self.logger.error("Cannot run a workflow without a deployed infrastructure")
            return

        env_conf = None

        if app_conf:
            env_conf = self.scenario_dir / WORKFLOW_ENV_CONF_FILE

        conf_file = self.scenario_dir / WORKFLOW_CONF_FILE

        self.app = App(
            config=conf_file,
            experiment_dir=self.experiment_dir,
            scenario_dir=self.scenario_dir,
            artifacts_dir=self.artifacts_dir,
            roles=self.roles,
            all_serv_extra_inf=self.infra.all_serv_extra_inf,
            app_conf=app_conf,
            env_config=env_conf,
            optimization_config=self.optimization_config,
        )

        # Enforce task
        self.logger.info(f"Enforcing workflow:{task}")

        # If we defined a monitoring service, we deploy it at launch ?
        # TODO: Check this
        # if task == WORKFLOW_TASK_LAUNCH:
        # self.infra.deploy_monitoring_service(
        # self.artifacts_dir, self.monitoring_remote_working_dir
        # )
        #     self.logger.info(
        #         f"Deploying monitoring stack: {self.infra.monitoring_type}"
        #     )
        #     self.monitoring = self.infra.get_monitoring_service(
        #         artifacts_path=self.artifacts_dir,
        #         remote_working_dir=self.monitoring_remote_working_dir,
        #     )
        #     self.monitoring.deploy()
        #     self.logger.info("Monitoring stack deployed")

        self.app.run_task(task=task, current_repeat=self.repeat)
        self.logger.info(f"Done enforcing workflow:{task}")

    def finalize(self, app_conf: str = None) -> None:
        """
        Finalize experiment
        """
        if not self.infra or not self.app:
            self.logger.error(
                "Cannot finalize an experiment without "
                "an infrastructure or before running 'workflow'"
            )
            return

        # TODO: find a more elegant way to do this output dir thing
        output_dir = self.experiment_dir
        if app_conf:
            output_dir = self.experiment_dir / app_conf

        self.logger.info("Finalizing experiment")
        self.logger.info("Running workflow 'finalize'")
        self.app.run_task(WORKFLOW_TASK_FINALIZE, current_repeat=self.repeat)
        self.logger.info("Finalizing layers and services")
        self.infra.finalize(output_dir=output_dir)
        self.logger.info("Done finalizing experiment")

    def deploy(self, duration: int, is_prepare: bool = True) -> None:
        """
        Deploy E2Clab experiment
        """

        self.logger.info("Starting experiment deployment")
        self.initiate()
        self.infrastructure()
        self.network()

        self.logger.debug(f"[APPLICATION CONF LIST]: {self.app_conf_list}")

        self.logger.info("Starting experiment deployment")
        if self.app_conf_list:
            for app_conf in self.app_conf_list:
                self.logger.info(f"Running experiment configuraiton '{app_conf}'")
                is_prepare = self._run_deploy(duration, is_prepare, app_conf)
        else:
            is_prepare = self._run_deploy(duration, is_prepare, None)

        self.logger.info("Done experiment deployment")

    def _run_deploy(self, duration: int, is_prepare: bool, app_conf: str):
        if is_prepare:
            # No app_conf during prepare stage
            self.application(WORKFLOW_TASK_PREPARE)
            # We prepare our deployment only once
            is_prepare = False
        self.application(WORKFLOW_TASK_LAUNCH, app_conf)
        self.logger.info(f"Waiting for duration: {duration} seconds")
        time.sleep(duration)
        self.logger.info(f"Stopping experiment after {duration} seconds")
        self.finalize(app_conf=app_conf)
        return is_prepare

    def destroy(self) -> None:
        """
        Release (free) computing resources, e.g. kill G5k oar jobs
        """
        # raise NotImplementedError
        self.logger.info("Destroying provider computing resource")
        self.infra.destroy()
        self.logger.info("Destroyed computing resources")

    def get_exp_id(self) -> UUID:
        return self.id

    def get_exp_dir(self) -> Path:
        return self.experiment_dir

    def _dump_application_parameters(self) -> None:
        """
        Generates a file with a list of User-Defined Services to be used by the user in
        the network.yaml and workflow.yaml configuration files.
        """
        user_roles = {}
        user_roles.update(self.roles)

        # remove roles not needed by the users
        if ROLES_MONITORING in user_roles:
            user_roles.pop(ROLES_MONITORING)
        for layer in self.infra.config[LAYERS]:
            for service in layer[SERVICES]:
                if service["_id"] in user_roles:
                    user_roles.pop(service["_id"])
                if service[NAME] in user_roles:
                    user_roles.pop(service[NAME])

        role_data = {}
        with open(self.layers_services_val_file, "w") as f:
            if MONITORING_SERVICE_ROLE in user_roles:
                yaml.dump(
                    "* * * * * * * Monitoring Service (started during workflow "
                    "'launch' step)",
                    f,
                )
                monitoring_node = user_roles.pop(MONITORING_SERVICE_ROLE)[0].address
                yaml.dump(f"Available at: http://localhost:{MONITORING_SVC_PORT}", f)
                _access = (
                    f"Access from your local machine: "
                    f"ssh -NL {MONITORING_SVC_PORT}:localhost:{MONITORING_SVC_PORT}"
                )
                if (
                    self.infra.config[MONITORING_SVC][MONITORING_SVC_PROVIDER]
                    == CHAMELEON_CLOUD
                ):
                    yaml.dump(f"{_access} cc@<FLOATING_IP>", f)
                else:
                    yaml.dump(f"{_access} {monitoring_node}", f)
                yaml.dump("username: admin / password: admin", f)

            if PROVENANCE_SERVICE_ROLE in user_roles:
                yaml.dump("* * * * * * * Provenance Service", f)
                provenance_node = user_roles.pop(PROVENANCE_SERVICE_ROLE)[0].address
                yaml.dump(f"Available at: http://localhost:{PROVENANCE_SVC_PORT}", f)
                _access = (
                    f"Access from your local machine: "
                    f"ssh -NL {PROVENANCE_SVC_PORT}:localhost:{PROVENANCE_SVC_PORT}"
                )
                yaml.dump(f"{_access} {provenance_node}", f)

            yaml.dump(
                "* * * * * * * Configure network.yaml and workflow.yaml using the "
                "information below!",
                f,
            )

            for layer in self.infra.config[LAYERS]:
                roles = []
                for role in sorted(user_roles):
                    # filter roles per layer name
                    if len(role.split(".")) > 1 and role.split(".")[0] == layer[NAME]:
                        hosts = []
                        for host in user_roles[role]:
                            hosts.append(host.address)
                        roles.append({role: hosts})
                role_data.update({layer[NAME]: roles})

            yaml.dump(role_data, f)
