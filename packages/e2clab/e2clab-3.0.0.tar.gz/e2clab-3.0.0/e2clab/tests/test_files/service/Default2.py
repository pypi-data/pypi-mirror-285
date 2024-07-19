from e2clab.services.service import Service


class Default2(Service):
    """
    A dummy service for unittest
    """

    def deploy(self):
        return self.register_service()
