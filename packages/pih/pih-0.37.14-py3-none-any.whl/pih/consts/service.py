EVENT_LISTENER_NAME_PREFIX: str = "_@@EventListener@@_"
SUPPORT_NAME_PREFIX: str = "_@@Support@@_"

SERVICE_DESCRIPTION_HOLDER_VARIABLE_NAME: str = "SD"

from enum import Enum
from pih.consts.hosts import Hosts
from pih.collections import Host
from pih.collections.service import ServiceDescription

class ServiceRoleBase(Enum):

    @property
    def value(self) -> ServiceDescription:
        return super().value

    @property
    def host(self) -> str | None:
        return self.value.host
    
    @property
    def standalone_name(self) -> str | None:
        return self.value.standalone_name

    @host.setter
    def host(self, value: str | Hosts | Host) -> None:
        if isinstance(value, str):
            self.value.host = value
        elif isinstance(value, Hosts):
            self.host = value.value
        elif isinstance(value, Host):
            self.host = value.name
            
    @property
    def NAME(self) -> str | None:
        return self.value.name