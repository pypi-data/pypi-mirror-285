from pathlib import Path
from typing import Union

import yaml

from e2clab.constants import (
    COMMAND_DEPLOY,
    COMMAND_FINALIZE,
    COMMAND_LYR_SVC,
    COMMAND_NETWORK,
    COMMAND_WORKFLOW,
    LAYERS_SERVICES_CONF_FILE,
    NETWORK_CONF_FILE,
    WORKFLOW_CONF_FILE,
    WORKFLOW_ENV_CONF_FILE,
    WORKFLOW_TASKS,
)
from e2clab.errors import E2clabFileError
from e2clab.log import getLogger
from e2clab.schemas import is_valid_conf

logger = getLogger(__name__, ["UTILS"])


def is_valid_setup(
    scenario_dir: Path,
    artifacts_dir: Union[Path, None],
    command_type: str,
    is_app_conf: bool = False,
) -> bool:
    """Checks if E2cLab configuration files follow the right schema.

    Args:
        scenario_dir (Path):
            Path to folder containing experiment configuration files
        artifacts_dir (Union[Path, None]):
            Path to folder containing experiment artifacts
        command_type (str):
            E2clab command you intend to run (e.g. 'network' or 'layer-services')
        is_app_conf (bool, optional):
            Are we going to use an 'app_conf' parameter. Defaults to False.

    Returns:
        bool: Validity of the experiment setup
    """

    is_valid = True

    # CHECK SCENARIO_DIR
    if not scenario_dir.exists():
        logger.error(f"Scenario dir path does not exist: {scenario_dir}")
        return False

    # CHECK IF CONFIG FILES EXIST AND ARE VALID IN SCENARIO_DIR
    if command_type == COMMAND_LYR_SVC or command_type == COMMAND_DEPLOY:
        res = validate_conf(
            conf_file=scenario_dir / LAYERS_SERVICES_CONF_FILE, type="layers_services"
        )
        is_valid = res and is_valid

    if command_type == COMMAND_NETWORK or command_type == COMMAND_DEPLOY:
        res = validate_conf(conf_file=scenario_dir / NETWORK_CONF_FILE, type="network")
        is_valid = res and is_valid

    if (
        command_type == COMMAND_WORKFLOW
        or command_type == COMMAND_DEPLOY
        or command_type == COMMAND_FINALIZE
    ):
        res = validate_conf(
            conf_file=scenario_dir / WORKFLOW_CONF_FILE, type="workflow"
        )
        is_valid = res and is_valid

        # CHECK "workflow_env.yaml"
        if is_app_conf:
            res = validate_conf(
                conf_file=scenario_dir / WORKFLOW_ENV_CONF_FILE, type="workflow_env"
            )
            is_valid = res and is_valid

    # CHECK ARTIFACTS_DIR
    if artifacts_dir is not None and not artifacts_dir.exists():
        logger.error(f"Artifact path does not exist: {artifacts_dir}")
        return False

    return is_valid


def is_valid_task(task: str) -> bool:
    is_valid = True
    if task.lower() not in WORKFLOW_TASKS:
        logger.error(
            f"Task {task.lower()} is not valid, "
            "choose one of the following [prepare, launch, finalize]"
        )
        is_valid = False
    return is_valid


def load_yaml_file(file: Path) -> dict[str, str]:
    """Loads an E2clab yaml configuration file

    Args:
        file (Path): Yaml configuration file

    Raises:
        E2clabFileError: if file does not exist
        E2clabFileError: if there is a yaml syntax error
        E2clabFileError: if there is any other unexpected error

    Returns:
        dict[str, str]: python object containing configuration description
    """
    try:
        with open(file, "r") as f:
            content = yaml.safe_load(f)
            return content
    except FileNotFoundError:
        raise E2clabFileError(file, "File does not exist")
    except yaml.YAMLError as e:
        raise E2clabFileError(file, f"Yaml syntax error in file -> {e}")
    except Exception as e:
        raise E2clabFileError(file, e)


def validate_conf(conf_file: Path, type: str) -> bool:
    """Validate if the configuration file follows the right syntax

    Args:
        conf_file (Path): path to the file
        type (str): "layers_services" | "network" | "workflow" | "workflow_env"

    Returns:
        bool: is the configuration valid
    """
    try:
        conf = load_yaml_file(conf_file)
    except E2clabFileError as e:
        logger.error(e)
        return False
    return is_valid_conf(conf, type)
