from enum import Enum
from pih.collections import Host


class Hosts(Enum):

    @property
    def NAME(self) -> str:
        return self.value.name

    @property
    def IP(self) -> str | None:
        return self.value.ip

    @property
    def ALIAS(self) -> str:
        return self.value.alias

    ORION = Host("orion", ip="192.168.100.90")

    SERVICES = Host("svshost", "zabbix", "192.168.100.95")

    BACKUP_WORKER = Host("backup_worker", "backup_worker", "192.168.100.11")

    WS255 = Host("ws-255", ip="192.168.100.138")

    WS816 = Host("ws-816", ip="192.168.254.81")

    WS735 = Host("ws-735", "shared_disk_owner", "192.168.254.102")

    DEVELOPER = WS735

    DC1 = Host("fmvdc1.fmv.lan", "dc1", "192.168.100.4")

    DC2 = Host("fmvdc2.fmv.lan", "dc2", "192.168.100.23")

    PRINTER_SERVER = DC1

    POLIBASE1 = Host(
        # shit - cause polibase is not accessable
        "polibase1.fmv.lan",
        "polibase1",
        "192.168.100.3",
    )

    POLIBASE2 = Host("polibase2.fmv.lan", "polibase2", "192.168.110.3")

    POLIBASE = POLIBASE1

    POLIBASE_TEST = POLIBASE2

    POLIBASE_RESERVE = POLIBASE2

    _1C = Host("fmv1c2", "1c", "192.168.100.22")

    NAS = Host("nas", "nas", "192.168.100.200")

    PACS_ARCHIVE = Host("pacs_archive", "ea_archive", "192.168.110.108")
