from pathlib import Path
from typing import Optional
from uuid import UUID

from enoslib.task import enostask

from e2clab.experiment import Experiment
from e2clab.log import getLogger

logger = getLogger(__name__, ["TASK"])


@enostask(new=True)
def infra(
    scenario_dir: Path,
    artifacts_dir: Path,
    env=None,
    optimization_config=None,
    optimization_id: Optional[UUID] = None,
    # env_symlink=False,
) -> None:
    exp = Experiment(
        scenario_dir=scenario_dir,
        artifacts_dir=artifacts_dir,
        optimization_config=optimization_config,
        optimization_id=optimization_id,
    )
    exp.initiate()
    exp.infrastructure()
    env["experiment"] = exp


@enostask()
def network(env=None) -> None:
    if not isinstance(env["experiment"], Experiment):
        logger.error("Error in env, exiting...")
        return
    exp: Experiment = env["experiment"]
    exp.network()
    env["experiment"] = exp


@enostask()
def app(task: str, app_conf: str = None, env=None) -> None:
    if not isinstance(env["experiment"], Experiment):
        logger.error("Error in env, exiting...")
        return
    exp: Experiment = env["experiment"]
    exp.application(task=task, app_conf=app_conf)
    env["experiment"] = exp


@enostask()
def finalize(env=None):
    if not isinstance(env["experiment"], Experiment):
        logger.error("Error in env, exiting...")
        return
    exp: Experiment = env["experiment"]
    exp.finalize()
    env["experiment"] = exp


@enostask()
def destroy(env=None):
    if not isinstance(env["experiment"], Experiment):
        logger.error("Error in env, exiting...")
        return
    exp: Experiment = env["experiment"]
    exp.destroy()


@enostask(new=True)
def deploy(
    scenario_dir: Path,
    artifacts_dir: Path,
    duration: int,
    repeat: int = 0,
    app_conf_list: list[str] = [],
    is_prepare: bool = True,
    optimization_id: UUID = None,
    env=None,
):
    for current_repeat in range(repeat + 1):
        exp = Experiment(
            scenario_dir=scenario_dir,
            artifacts_dir=artifacts_dir,
            optimization_id=optimization_id,
            app_conf_list=app_conf_list,
            repeat=current_repeat,
        )
        exp.deploy(duration=duration, is_prepare=is_prepare)
        env["experiment"] = exp
