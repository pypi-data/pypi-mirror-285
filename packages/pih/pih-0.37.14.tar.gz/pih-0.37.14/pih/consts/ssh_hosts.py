from pih.consts.hosts import Hosts
from pih.consts.addresses import ADDRESSES
from enum import Enum

class SSHHosts(Enum):
    EMAIL_SERVER = ADDRESSES.EMAIL_SERVER_ADDRESS
    SITE_API = ADDRESSES.API_SITE_ADDRESS
    SITE = ADDRESSES.SITE_ADDRESS
    SERVICES = Hosts.SERVICES.NAME