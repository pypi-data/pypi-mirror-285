from abc import ABCMeta, abstractmethod
from typing import Optional

import enoslib as en
from enoslib import Host
from enoslib.objects import Roles
from enoslib.service import Docker

from e2clab.constants import ENV
from e2clab.log import getLogger


class Service:
    """
    A Service represents any system that provides
    a specific functionality or action in the scenario workflow."
    """

    __metaclass__ = ABCMeta

    # Register for all loaded subclasses of 'Service'
    _loaded_subservices = {}

    def __init__(self, hosts, layer_name, service_metadata):
        self.hosts = hosts
        self.layer_name = layer_name
        self.roles = Roles({"all": self.hosts})
        self.service_metadata = service_metadata
        self.service_extra_info = {}
        self.service_roles = Roles({})
        if service_metadata is not None and ENV in service_metadata:
            self.env = service_metadata[ENV]
        else:
            self.env = {}

        self.logger = getLogger(__name__, ["SERV"])

    def __init_subclass__(cls, **kwargs) -> None:
        """
        When a subclass of 'Service' is defined, it is stored in a dict for easy
        programmatic imports and instanciation.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in cls._loaded_subservices.keys():
            cls._loaded_subservices[cls.__name__] = cls

    @classmethod
    def get_loaded_subservices(cls):
        return cls._loaded_subservices

    @abstractmethod
    def deploy(self):
        """
        (abstract) Implement the logic of your custom Service.
        Must register all services and return
            all of the service'sextra info and roles
        """
        pass

    @staticmethod
    def __service_key(
        layer_name: str,
        service_name: str,
        service_id: int,
        sub_service_name: Optional[str] = None,
        machine_id: Optional[int] = None,
    ):
        """
        Service ID (metadata['_id']) is: "LayerID_ServiceID_MachineID"
        e.g.: service_key = "layer.service.service_id.sub_service.machine_id"
                          = cloud.flink.1.job_manager.1
        e.g.: service_key = "layer.service.service_id.sub_service.machine_id"
                          = cloud.flink.1.task_manager.1

        In this example, Flink is the "Service" and Job_Manager
            and Task_Manager are the "sub Service(s)".

        e.g.: service_key = "layer.service.service_id.machine_id" = edge.producer.1.1
        In this example, Producer is the "Service" and it does not have a "sub Service".

        NOTE:
            "service_id" is generated in e2clab.infra.generate_service_id()"
            "machine_id" is generated in "register_service()"
        """

        service_key = f"{layer_name}.{service_name}.{service_id}"
        service_key += f".{sub_service_name}" if sub_service_name else ""
        service_key += f".{machine_id}" if machine_id else ""
        return service_key.lower()

    @staticmethod
    def __get_list_of_hosts(_roles):
        _hosts = []
        for role_key in _roles.keys():
            _hosts += _roles[role_key]
        return _hosts

    @staticmethod
    def __get_host_ip(host: Host, version: int):
        if version in [6]:
            _ip = en.run(
                "ip -6 addr show scope global | awk '/inet6/{print $2}'", roles=host
            )[0].stdout
        else:
            _ip = en.run(
                "ip -4 addr show scope global | awk '/inet/{print $2}'", roles=host
            )[0].stdout
        return _ip.split("/")[0] if "/" in _ip else None

    def register_service(
        self, _roles=None, service_port=None, sub_service=None, extra=None
    ):
        """
        Registers a Service.
        :param _roles: Roles containing the hosts attributed to the Service.
        :param service_port: Service port number.
        :param sub_service: Sub Service name e. g. 'master' 'worker'.
        :param extra: List[Dict]. List of dict with extra information.
        :return: service_extra_info
                    (Extra attributes in Services to access them in "workflow.yaml"
                    [avoids hard coding])
                 service_roles
                    (New Roles containing the hosts attributed to the Service).
        """
        if _roles is None:
            _hosts = self.hosts
        else:
            _hosts = self.__get_list_of_hosts(_roles)

        layer_id = int(self.service_metadata["_id"].split("_")[0])
        service_id = int(self.service_metadata["_id"].split("_")[1])

        service_name = self.service_metadata["name"]

        if len(_hosts) == 0:
            return self.service_extra_info, self.service_roles
        for i, host in enumerate(_hosts):
            machine_id = i + 1
            # default Service info:
            # Service ID (service_key) is: "LayerID_ServiceID_MachineID".
            service_key = self.__service_key(
                layer_name=self.layer_name,
                service_name=service_name,
                service_id=service_id,
                sub_service_name=sub_service,
                machine_id=machine_id,
            )
            self.service_extra_info.update(
                {
                    service_key: {
                        "_id": f"{self.service_metadata['_id']}_{machine_id}",
                        "layer_id": str(layer_id),
                        "service_id": str(service_id),
                        "host_id": str(machine_id),
                        "__address__": f"{host.address}",
                        "url": f"{host.address}"
                        + (f":{service_port}" if service_port else ""),
                    }
                }
            )
            if isinstance(host, Host):
                _ipv6 = self.__get_host_ip(host, 6)
                if _ipv6:
                    self.service_extra_info[service_key].update(
                        {
                            "__address6__": f"{_ipv6}",
                            "url6": f"[{_ipv6}]"
                            + (f":{service_port}" if service_port else ""),
                        }
                    )
                _ipv4 = self.__get_host_ip(host, 4)
                if _ipv4:
                    self.service_extra_info[service_key].update(
                        {
                            "__address4__": f"{_ipv4}",
                            "url4": f"{_ipv4}"
                            + (f":{service_port}" if service_port else ""),
                        }
                    )
                # For chameleon cloud instances
                gateway = host.extra.get("gateway")
                if gateway:
                    self.service_extra_info[service_key].update({"gateway": gateway})
            # user-defined Service info
            # TODO: Change this stuff
            if extra is not None and len(extra) >= machine_id and extra[i] is not None:
                self.service_extra_info[service_key].update(extra[i])
            # new roles after Service registration
            self.service_roles.update({service_key: [host]})

        return self.service_extra_info, self.service_roles

    def deploy_docker(
        self,
        _roles=None,
        registry=None,
        registry_opts=None,
        bind_var_docker=None,
        swarm=False,
    ):
        if _roles is None:
            _hosts = self.hosts
        else:
            _hosts = self.__get_list_of_hosts(_roles)
        d = Docker(
            agent=_hosts,
            registry=registry,
            registry_opts=registry_opts,
            bind_var_docker=(
                "/tmp/docker" if bind_var_docker is None else bind_var_docker
            ),
            swarm=swarm,
        )
        ############################
        # Temp Solution
        # self.logger.warning("Quick fix 'docker<7.1.0' and 'requests<3.32'")
        # with en.actions(roles=_hosts) as a:
        #     a.pip(name="docker<7.1.0", state="present")
        #     a.pip(name="requests<2.32", state="present")
        ############################
        d.deploy()
