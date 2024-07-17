from pih.tools import j, jp
from pih.consts.names import USER_PROPERTIES

from enum import Enum, auto

class AD:
    
    ADMINISTRATOR_LOGIN: str = "Administrator"
    SPLITTER: str = "."
    OU: str = "OU="
    INCATIVE_OU_NAME: str = j((OU, "Inactive"))
    SEARCH_ATTRIBUTES: list[str] = [USER_PROPERTIES.LOGIN, USER_PROPERTIES.NAME]
    SEARCH_ATTRIBUTE_DEFAULT: str = SEARCH_ATTRIBUTES[0]
    USER_HOME_FOLDER_DISK: str = "U:"
    SEARCH_ALL_PATTERN: str = "*"
    LOCATION_JOINER: str = ":"
    TEMPLATED_USER_SERACH_TEMPLATE: str = j(("_", SEARCH_ALL_PATTERN, "_"))
    

    USER_ACCOUNT_CONTROL: list[str] = [
        "SCRIPT",
        "ACCOUNTDISABLE",
        "RESERVED",
        "HOMEDIR_REQUIRED",
        "LOCKOUT",
        "PASSWD_NOTREQD",
        "PASSWD_CANT_CHANGE",
        "ENCRYPTED_TEXT_PWD_ALLOWED",
        "TEMP_DUPLICATE_ACCOUNT",
        "NORMAL_ACCOUNT",
        "RESERVED",
        "INTERDOMAIN_TRUST_ACCOUNT",
        "WORKSTATION_TRUST_ACCOUNT",
        "SERVER_TRUST_ACCOUNT",
        "RESERVED",
        "RESERVED",
        "DONT_EXPIRE_PASSWORD",
        "MNS_LOGON_ACCOUNT",
        "SMARTCARD_REQUIRED",
        "TRUSTED_FOR_DELEGATION",
        "NOT_DELEGATED",
        "USE_DES_KEY_ONLY",
        "DONT_REQ_PREAUTH",
        "PASSWORD_EXPIRED",
        "TRUSTED_TO_AUTH_FOR_DELEGATION",
        "RESERVED",
        "PARTIAL_SECRETS_ACCOUNT",
    ]
    
    DOMAIN_NAME: str = "fmv"
    DOMAIN_ALIAS: str = "pih"
    DOMAIN_SUFFIX: str = "lan"
    DOMAIN_DNS: str = jp((DOMAIN_NAME, DOMAIN_SUFFIX))
    DOMAIN_MAIN: str = DOMAIN_DNS
    PATH_ROOT: str = j(("//", DOMAIN_MAIN))

    ROOT_CONTAINER_DN: str = f"{OU}Unit,DC={DOMAIN_NAME},DC={DOMAIN_SUFFIX}"
    WORKSTATIONS_CONTAINER_DN: str = f"{OU}Workstations,{ROOT_CONTAINER_DN}"
    SERVERS_CONTAINER_DN: str = f"{OU}Servers,{ROOT_CONTAINER_DN}"
    USERS_CONTAINER_DN_SUFFIX: str = f"Users,{ROOT_CONTAINER_DN}"
    ACTIVE_USERS_CONTAINER_DN: str = f"{OU}{USERS_CONTAINER_DN_SUFFIX}"
    INACTIVE_USERS_CONTAINER_DN: str = f"{OU}dead{USERS_CONTAINER_DN_SUFFIX}"
    GROUP_CONTAINER_DN: str = f"{OU}Groups,{ROOT_CONTAINER_DN}"
    PROPERTY_ROOT_DN: str = f"{OU}Property,{GROUP_CONTAINER_DN}"
    PROPERTY_COMPUTER_DN: str = f"{OU}Computer,{PROPERTY_ROOT_DN}"
    PROPERTY_USER_DN: str = f"{OU}User,{PROPERTY_ROOT_DN}"
    JOB_POSITION_CONTAINER_DN: str = f"{OU}Job positions,{GROUP_CONTAINER_DN}"

    WORKSTATION_PREFIX_LIST: list[str] = ["ws-", "nb-", "fmvulianna"]

    class USER:
        MARKETER_ADMINISTRATOR: str = "marketer_admin"
        CALL_CENTRE_ADMINISTRATOR: str = "callCentreAdmin"
        REGISTRATION_AND_CALL: str = "reg_and_call"
        CONTROL_SERVICE: str = "cctv"
        INDICATIONS_ALL: str = "indications_all"
        ADMINISTRATOR: str = "Administrator"

    class JobPositions(Enum):
        HR = auto()
        IT = auto()
        CALL_CENTRE = auto()
        REGISTRATOR = auto()
        RD = auto()
        MARKETER = auto()

    class Groups(Enum):
        TimeTrackingReport = auto()
        Inventory = auto()
        Polibase = auto()
        Admin = auto()
        ServiceAdmin = auto()
        CardRegistry = auto()
        PolibaseUsers = auto()
        RD = auto()
        IndicationWatcher = auto()
        FunctionalDiagnostics = auto()

    class ComputerProperties(Enum):
        Watchable = 1
        Shutdownable = 2
        Rebootable = 4
        DiskReportable = 8
        DiskReportableViaZabbix = 16
        
    class UserProperies(Enum):
        Jokeless = 1
        DoctorVisitless = 2
        HasLunchBreak = 4
        TimeTrackingless = 8