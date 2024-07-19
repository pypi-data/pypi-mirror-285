"""
This file defines all functions and utilities needded to enforce
the 'networking' of our experiment
"""

from pathlib import Path
from typing import Iterable

import enoslib as en
from enoslib.infra.enos_chameleonedge.objects import ChameleonDevice

from e2clab.config import NetworkConfig
from e2clab.constants import (
    MONITORING_NETWORK_ROLE,
    NET_DELAY,
    NET_DST,
    NET_LOSS,
    NET_NETWORKS,
    NET_RATE,
    NET_SRC,
    NET_SYMMETRIC,
    NETWORK_VALIDATE_DIR,
)
from e2clab.log import getLogger
from e2clab.utils import load_yaml_file


class Network:
    """
    Enforce network definition
    a.k.a. Network manager
    """

    def __init__(self, config: Path, roles, networks) -> None:
        """Create a new experiment network emulation

        Args:
            config (Path): Path to 'network.yaml' configuration file
            roles (en.Roles): EnOSlib Roles associated with the experiment
            networks (en.Networks): EnOSlib Networks associated with the experiment
        """
        self.logger = getLogger(__name__, ["NET"])
        self.config = self._load_config(config)
        self.roles = roles
        self.networks = networks

    def _load_config(self, config_path: Path) -> NetworkConfig:
        c = load_yaml_file(config_path)
        return NetworkConfig(c)

    # User Methods

    def prepare(self) -> None:
        """Prepare network emulation"""
        self.networks_to_em = self._get_filtered_networks()

        self.logger.debug(f"[NETWORK TO EMMULATE] {self.networks_to_em}")

    def deploy(self) -> None:
        """Deploy configured network emulation"""
        self.netems = {}

        if self.config[NET_NETWORKS] is None:
            self.logger.info("No network emulation to deploy")
            return

        self.logger.info("Deploying network emulation")

        for net_config in self.config[NET_NETWORKS]:
            if self._check_edgeChameleonDevice(net_config):
                netem = self._configure_netem(net_config)
            else:
                netem = self._configure_netemhtb(net_config)

            self.logger.debug(f"[NETEM CONFIG] {net_config}")
            self.logger.debug(f"[NETEM] {netem}")

            netem.deploy()

            key = self._get_netem_key(net_config)
            self.netems.update({key: netem})

            self.logger.info(f"Network emulation {key} deployed")
        self.logger.info("Done deploying network emulations")

    def validate(self, experiment_dir: Path) -> None:
        """Validate network emmulation deployment

        Args:
            experiment_dir (Path): Path to output validation file
        """
        if self.netems:
            self.logger.info(
                f"Network emulation validation files sotred in {experiment_dir}"
            )
        for key, netem in self.netems.items():
            # Creating dir to store validation files
            netem_validate_dir: Path = experiment_dir / NETWORK_VALIDATE_DIR / key
            netem_validate_dir.mkdir(parents=True, exist_ok=True)

            netem.validate(output_dir=netem_validate_dir)
            self.logger.debug(f"Validated netem {key} in {netem_validate_dir}")

    def destroy(self):
        raise NotImplementedError

    # End User methods

    def _get_filtered_networks(self) -> Iterable[en.Network]:
        # TODO: Check the purpose of this function
        networks_to_em = []
        for key, value in self.networks.items():
            if key not in [MONITORING_NETWORK_ROLE]:
                networks_to_em.extend(value)
        return networks_to_em

    def _configure_netem(self, net_config: dict) -> en.Netem:
        netem = en.Netem()

        command = ""
        if NET_DELAY in net_config:
            command += f"{NET_DELAY} {net_config[NET_DELAY]} "
        if NET_RATE in net_config:
            command += f"{NET_RATE} {net_config[NET_RATE]} "
        if NET_LOSS in net_config:
            command += f"{NET_LOSS} {net_config[NET_LOSS]} "
        netem = en.Netem()
        netem.add_constraints(
            command,
            en.get_hosts(roles=self.roles, pattern_hosts=net_config[NET_SRC]),
            symmetric=False,
        )
        return netem

    def _configure_netemhtb(self, net_config: dict) -> en.NetemHTB:
        netem = en.NetemHTB()

        sym = net_config.get(NET_SYMMETRIC, False)
        delay = net_config.get(NET_DELAY, "")
        rate = net_config.get(NET_RATE, "")
        loss = net_config.get(NET_LOSS, None)

        src = en.get_hosts(roles=self.roles, pattern_hosts=net_config[NET_SRC])
        dest = en.get_hosts(roles=self.roles, pattern_hosts=net_config[NET_DST])

        netem.add_constraints(
            src=src,
            dest=dest,
            delay=delay,
            rate=rate,
            loss=loss,
            symetric=sym,
            networks=self.networks_to_em,
        )
        return netem

    def _get_netem_key(self, net_config: dict) -> str:
        src = net_config[NET_SRC]
        dst = net_config[NET_DST]
        symmetric = net_config.get(NET_SYMMETRIC, False)
        sym = "symmetric" if symmetric else "asymmetric"
        key = f"{src}-{dst}-{sym}"
        return key

    def _check_edgeChameleonDevice(self, net_config) -> bool:
        hosts = self.roles[net_config[NET_DST]]
        # hosts = en.get_hosts(roles=self.roles, pattern_hosts=net_config[NET_DST])
        for host in hosts:
            if isinstance(host, ChameleonDevice):
                self.logger.debug(f"Network ChameleonDevice: {host}")
                return True
        return False
