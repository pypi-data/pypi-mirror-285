from enum import Enum, auto, IntEnum

from pih.tools import j, js
from pih.consts import *
from pih.consts.names import *
from pih.consts.paths import *
from pih.collections import (
    ActionDescription,
    ResourceDescription,
    MedicalResearchType,
    SiteResourceDescription,
    ZabbixResourceDescription,
    MinIntStorageVariableHolder,
    ResourceDescriptionDelegated,
    OrderedNameCaptionDescription,
    ZabbixResourceDescriptionDelegated,
    IconedOrderedNameCaptionDescription,
)
from pih.consts.password import *
from pih.consts.date_time import *
from pih.consts.service_commands import *

VERSION: str = "0.37.14"


class DATA:
    # deprecated
    class EXTRACTOR:
        USER_NAME_FULL: str = "user_name_full"
        USER_NAME: str = "user_name"
        AS_IS: str = "as_is"

    class FORMATTER(Enum):
        MY_DATETIME = "my_datetime"
        MY_DATE = "my_date"
        CHILLER_INDICATIONS_VALUE_INDICATORS = "chiller_indications_value_indicators"
        CHILLER_FILTER_COUNT = "chiller_filter_count"


class INDICATIONS:
    class CHILLER:
        ACTUAL_VALUES_TIME_DELTA_IN_MINUTES: int = 5

        INDICATOR_NAME: list[str] = [
            "Активный сигнал тревоги",
            "Работает нагреватель",
            "Замораживание включено",
            "Работает вентилятор конденсатора",
            "Работает насос/вытяжной вентилятор",
            "Работает компрессор",
        ]

        INDICATOR_EMPTY_DISPLAY: int = -1

    class MRI:
        # hours
        PERIOD: int = 2


class BARCODE:
    CODE128: str = "code128"
    I25: str = "i25"


class FONT:
    FOR_PDF: str = "DejaVuSerif"


class SessionFlags(IntEnum):
    CLI = 512
    OUTSIDE = 8192
    
class SESSION_TYPE:
    MOBILE: str = "mobile"
    OUTSIDE: str = "outside"


class URLS:
    PYPI: str = "https://pypi.python.org/pypi/pih/json"


class EmailVerificationMethods(IntEnum):
    NORMAL = auto()
    ABSTRACT_API = auto()
    DEFAULT = ABSTRACT_API


class ROBOCOPY:

    NAME: str = "robocopy"

    ERROR_CODE_START: int = 8

    STATUS_CODE: dict[int, str] = {
        0: "No errors occurred, and no copying was done. The source and destination directory trees are completely synchronized.",
        1: "One or more files were copied successfully (that is, new files have arrived).",
        2: "Some Extra files or directories were detected. No files were copied Examine the output log for details.",
        4: "Some Mismatched files or directories were detected. Examine the output log. Housekeeping might be required.",
        8: "Some files or directories could not be copied (copy errors occurred and the retry limit was exceeded). Check these errors further.",
        16: "Serious error. Robocopy did not copy any files. Either a usage error or an error due to insufficient access privileges on the source or destination directories.",
        3: "Some files were copied. Additional files were present. No failure was encountered.",
        5: "Some files were copied. Some files were mismatched. No failure was encountered.",
        6: "Additional files and mismatched files exist. No files were copied and no failures were encountered. This means that the files already exist in the destination directory",
        7: "Files were copied, a file mismatch was present, and additional files were present.",
    }


class CHARSETS:
    WINDOWS_ALTERNATIVE: str = "CP866"
    UTF8: str = "utf-8"
    
class INPUT_TYPE:
    NO: int = -1
    NORMAL: int = 0
    INDEX: int = 1
    QUESTION: int = 2


class WINDOWS:

    NAME: str = "Windows"

    class ENVIROMENT_VARIABLES:
        PATH: str = "PATH"

    ENVIROMENT_COMMAND: str = "$Env"

    class CHARSETS:
        ALTERNATIVE: str = CHARSETS.WINDOWS_ALTERNATIVE

    class SERVICES:
        WIA: str = (
            "stisvc"  # Обеспечивает службы получения изображений со сканеров и цифровых камер
        )
        TASK_SCHEDULER: str = "schtasks"

    class PROCESSES:
        POWER_SHELL_REMOTE_SESSION: str = "wsmprovhost.exe"

    class PORT:
        SMB: int = 445
        

class CONST(DATE_TIME):

    class ADDRESS:

        LOCATION: tuple[float, float] = (43.10077173904819, 131.90206595788635)
        TEXT: str = (
            "- г. Владивосток, ул. Запорожская, 7\n- Поликлиника: пн-сб с 8 до 20\n- Приемное отделение: круглосуточно, без праздников и выходных"
        )

    EMAIL_SPLITTER: str = "@"
    ISOLATED_ARG_NAME: str = "isolated"
    ARGUMENT_PREFIX: str = "--"
    SPLITTER: str = ":"
    NAME_SPLITTER: str = "_"
    UNKNOWN_VALUE: str = "?"

    class PORT:
        HTTP: int = 80
        HTTPS: int = 443
        SMTP: int = 587
        IMAP: int = 993
        SNMP: int = 161

    class FILES:
        SECTION: str = "Мобильные файлы"

    class NOTES:
        SECTION: str = "Мобильные заметки"

    class JOURNALS:
        SECTION: str = "Журналы"

    # in seconds
    HEART_BEAT_PERIOD: int = 60

    NEW_LINE: str = "\n"

    class TEST:
        WORKSTATION_MAME: str = Hosts.DEVELOPER.NAME
        USER: str | None = "nak"
        EMAIL_ADDRESS: str | None = "nak@pacifichosp.com"
        PIN: int = 100310
        NAME: str = "test"

    GROUP_PREFIX: str = "group:"

    SITE_PROTOCOL: str = "https://"
    UNTRUST_SITE_PROTOCOL: str = "http://"

    INTERNATIONAL_TELEPHONE_NUMBER_PREFIX: str = "7"
    TELEPHONE_NUMBER_PREFIX: str = j(("+", INTERNATIONAL_TELEPHONE_NUMBER_PREFIX))
    INTERNAL_TELEPHONE_NUMBER_PREFIX: str = "тел."

    class CACHE:
        class TTL:
            # in seconds
            WORKSTATIONS: int = 60
            USERS: int = 300

    class ERROR:
        class WAPPI:
            PROFILE_NOT_PAID: int = 402

    class TIME_TRACKING:
        REPORT_DAY_PERIOD_DEFAULT: int = 15

    class MESSAGE:
        class WHATSAPP:
            SITE_NAME: str = "https://wa.me/"
            SEND_MESSAGE_TO_TEMPLATE: str = SITE_NAME + "{}?text={}"
            GROUP_SUFFIX: str = "@g.us"
            OUTSIDE_SUFFIX: str = "@outside"
            CLI_SUFFIX: str = "@cli"

            class GROUP(Enum):
                PIH_CLI = "120363163438805316@g.us"
                REGISTRATOR_CLI = "120363212130686795@g.us"
                RD = "79146947050-1595848245@g.us"
                MAIN = "79644300470-1447044803@g.us"
                EMAIL_CONTROL = "120363159605715569@g.us"
                CT_INDICATIONS = "120363084280723039@g.us"
                DOCUMENTS_WORK_STACK = "120363115241877592@g.us"
                REGISTRATION_AND_CALL = "79242332784-1447983812@g.us"
                DOCUMENTS_WORK_STACK_TEST = "120363128816931482@g.us"
                CONTROL_SERVICE_INDICATIONS = "120363159210756301@g.us"
                SCANNED_DOCUMENT_HELPER_CLI = "120363220286578760@g.us"

            class WAPPI:

                DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
                NAME: str = "Wappi"
                DESCRIPTION: str = "Сервис по отправке сообщений"
                SEND: str = "send?"

                PROFILE_SUFFIX: str = "profile_id="
                URL_API: str = "https://wappi.pro/api"
                URL_API_SYNC: str = j((URL_API, "/sync"))
                URL_MESSAGE: str = j((URL_API_SYNC, "/message"))
                STATUS: str = j(
                    (j((URL_API_SYNC, "get", "status"), "/"), "?", PROFILE_SUFFIX)
                )
                URL_SEND_MESSAGE: str = j((URL_MESSAGE, "/", SEND, PROFILE_SUFFIX))
                URL_SEND_LOCATION: str = j(
                    (URL_MESSAGE, "/location/", SEND, PROFILE_SUFFIX)
                )
                URL_SEND_VIDEO: str = j((URL_MESSAGE, "/video/", SEND, PROFILE_SUFFIX))
                URL_SEND_IMAGE: str = j((URL_MESSAGE, "/img/", SEND, PROFILE_SUFFIX))
                URL_SEND_DOCUMENT: str = j(
                    (URL_MESSAGE, "/document/", SEND, PROFILE_SUFFIX)
                )
                URL_SEND_LIST_MESSAGE: str = j(
                    (URL_MESSAGE, "/list/", SEND, PROFILE_SUFFIX)
                )
                URL_SEND_BUTTONS_MESSAGE: str = j(
                    (URL_MESSAGE, "/buttons/", SEND, PROFILE_SUFFIX)
                )
                URL_GET_MESSAGES: str = j((URL_MESSAGE, "s/get?", PROFILE_SUFFIX))
                URL_GET_STATUS: str = j((URL_API_SYNC, "/get/status?", PROFILE_SUFFIX))
                CONTACT_SUFFIX: str = "@c.us"

                class Profiles(Enum):
                    IT = "e6706eaf-ae17"
                    CALL_CENTRE = "285c71a4-05f7"
                    MARKETER = "c31db01c-b6d6"
                    DEFAULT = CALL_CENTRE

                AUTHORIZATION: dict[Profiles, str] = {
                    Profiles.IT: "6b356d3f53124af3078707163fdaebca3580dc38",
                    Profiles.MARKETER: "6b356d3f53124af3078707163fdaebca3580dc38",
                    Profiles.CALL_CENTRE: "7d453de6fc17d3e6816b0abc46f2b192822130f5",
                }

    class SERVICE:
        NAME: str = "service"

    class VALENTA:
        NAME: str = "valenta"
        PROCESS_NAME: str = "Vlwin"

    class POWERSHELL:
        NAME: str = "powershell"

    class PSTOOLS:
        NAME: str = "pstools"
        PS_EXECUTOR: str = "psexec"
        PS_KILL_EXECUTOR: str = "pskill"
        PS_PING: str = "psping"

        COMMAND_LIST: list[str] = [
            PS_KILL_EXECUTOR,
            "psfile",
            "psgetsid",
            "psinfo",
            "pslist",
            "psloggedon",
            "psloglist",
            "pspasswd",
            PS_PING,
            "psservice",
            "psshutdown",
            "pssuspend",
        ]

        NO_BANNER: str = "-nobanner"
        ACCEPTEULA: str = "-accepteula"

    class MSG:
        NAME: str = "msg"
        EXECUTOR: str = NAME

    class BARCODE_READER:
        PREFIX: str = "("
        SUFFIX: str = ")"

    class NAME_POLICY:
        PARTS_LIST_MIN_LENGTH: int = 3
        PART_ITEM_MIN_LENGTH: int = 3

    HOST = Hosts

    class CARD_REGISTRY:
        PLACE_NAME: dict[str, str] = {"Т": "Приёмное отделение", "П": "Поликлиника"}
        PLACE_CARD_HOLDER_MAPPER: dict[str, str] = {"Т": "М-Я", "П": "А-Л"}
        MAX_CARD_PER_FOLDER: int = 60
        SUITABLE_FOLDER_NAME_SYMBOL = ("!", " ")

    class VISUAL:
        YES: str = "✅"
        NO: str = "❌"
        WARNING: str = "⚠️"
        WAIT: str = "⏳"
        NOTIFICATION: str = "🔔"
        ROBOT: str = "🤖"
        SAD: str = "😔"
        GOOD: str = YES
        ERROR: str = NO
        ORANGE_ROMB: str = "🔸"
        BLUE_ROMB: str = "🔹"
        TASK: str = "✳️"
        EYE: str = "👁️"
        HAND_INDICATE: str = "👉"
        HAND_DOWN: str = "👇"
        HAND_UP: str = "☝️"
        INFORMATION: str = "ℹ️"
        QUESTION: str = "❔"

        NUMBER_SYMBOLS: list[str] = [
            "0️⃣",
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🔟",
        ]

        TEMPERATURE_SYMBOL: str = "°C"

        ARROW: str = "➜"

        BULLET: str = "•"


class MATERIALIZED_RESOURCES:
    NAME: str = "MATERIALIZED_RESOURCES"
    ALIAS: str = "MR"

    class Types(Enum):

        CHILLER_FILTER = MinIntStorageVariableHolder(
            "CHF", description="Фильтры для чиллера", min_value=2
        )

        """
        OPTICAL_DISK_IN_STOCK = MinIntStorageVariableHolder(
            "ODS",
            description="Оптические диски для записи исследований на складе",
            min_value=50,
        )

        OPTICAL_DISK_IN_USE = MinIntStorageVariableHolder(
            "ODU",
            description="Оптические диски для записи исследований в пользовании",
            min_value=10,
        )
        """


class MedicalResearchTypes(Enum):
    MRI = MedicalResearchType(("Магнитно-резонансная томография",), "МРТ")
    CT = MedicalResearchType(("Компьютерная томография",), "КТ")
    ULTRASOUND = MedicalResearchType(("ультразвуковая допплерография",), "УЗИ")


from pih.consts.addresses import ADDRESSES


class RESOURCES:
    class DESCRIPTIONS:
        INTERNET: ResourceDescription = ResourceDescription(
            "77.88.55.242", "Интернет соединение"
        )

        VPN_PACS_SPB: ResourceDescriptionDelegated = ResourceDescriptionDelegated(
            "192.168.5.3", "VPN соединение для PACS SPB", (2, 100, 5), Hosts.WS255.NAME
        )

        PACS_SPB: ZabbixResourceDescriptionDelegated = (
            ZabbixResourceDescriptionDelegated(
                "10.76.12.124:4242",
                "Соединение PACS SPB",
                (2, 100, 5),
                Hosts.WS255.NAME,
                "PACS_SPB",
            )
        )

        POLIBASE1: ResourceDescription = ResourceDescription(
            Hosts.POLIBASE1.NAME,
            "Polibase",
            inaccessibility_check_values=(2, 10000, 15),
        )

        POLIBASE2: ResourceDescription = ResourceDescription(
            Hosts.POLIBASE2.NAME,
            "Polibase reserved",
            inaccessibility_check_values=(2, 10000, 15),
        )

        POLIBASE: ZabbixResourceDescription = ZabbixResourceDescription(
            POLIBASE1.address,
            POLIBASE1.name,
            POLIBASE1.inaccessibility_check_values,
            Hosts.POLIBASE1.ALIAS,
        )

        SITE_LIST: list[SiteResourceDescription] = [
            SiteResourceDescription(
                ADDRESSES.SITE_ADDRESS,
                js(("Сайт компании:", ADDRESSES.SITE_ADDRESS)),
                inaccessibility_check_values=(1, 20, 15),
                check_certificate_status=True,
                check_free_space_status=True,
                driver_name="/dev/mapper/centos-root",
            ),
            SiteResourceDescription(
                ADDRESSES.EMAIL_SERVER_ADDRESS,
                js(("Сайт корпоративной почты:", ADDRESSES.EMAIL_SERVER_ADDRESS)),
                check_certificate_status=True,
                check_free_space_status=True,
                driver_name="/dev/mapper/centos_tenant26--02-var",
            ),
            SiteResourceDescription(
                ADDRESSES.API_SITE_ADDRESS,
                js(
                    (
                        "Api сайта",
                        j((ADDRESSES.SITE_ADDRESS, ":")),
                        ADDRESSES.API_SITE_ADDRESS,
                    )
                ),
                check_certificate_status=True,
                check_free_space_status=False,
            ),
            SiteResourceDescription(
                ADDRESSES.BITRIX_SITE_URL,
                js(("Сайт ЦМРТ24:", ADDRESSES.BITRIX_SITE_URL)),
            ),
            SiteResourceDescription(
                ADDRESSES.OMS_SITE_ADDRESS,
                js(("Внутренний сайт омс:", ADDRESSES.OMS_SITE_ADDRESS)),
                internal=True,
            ),
            SiteResourceDescription(
                ADDRESSES.WIKI_SITE_ADDRESS,
                js(("Внутренний сайт Вики:", ADDRESSES.WIKI_SITE_ADDRESS)),
                internal=True,
            ),
        ]


class CheckableSections(IntEnum):
    RESOURCES = auto()
    WS = auto()
    PRINTERS = auto()
    INDICATIONS = auto()
    BACKUPS = auto()
    VALENTA = auto()
    SERVERS = auto()
    MATERIALIZED_RESOURCES = auto()
    TIMESTAMPS = auto()
    DISKS = auto()
    POLIBASE = auto()

    @staticmethod
    def all():
        return [item for item in CheckableSections]


class MarkType(IntEnum):
    NORMAL = auto()
    FREE = auto()
    GUEST = auto()
    TEMPORARY = auto()


class MARK_VARIANT:
    BRACELET: str = "-0-"
    CARD: str = ""


class PolibasePersonInformationQuestStatus(IntEnum):
    UNKNOWN = -1
    GOOD = 0
    EMAIL_IS_EMPTY = 1
    EMAIL_IS_WRONG = 2
    EMAIL_IS_NOT_ACCESSABLE = 4


class ResourceInaccessableReasons(Enum):
    CERTIFICATE_ERROR = "Ошибка проверки сертификата"
    SERVICE_UNAVAILABLE = "Ошибка 503: Сервис недоступен"


class PolibasePersonReviewQuestStep(IntEnum):
    BEGIN = auto()
    #
    ASK_GRADE = auto()
    ASK_FEEDBACK_CALL = auto()
    ASK_INFORMATION_WAY = auto()
    #
    COMPLETE = auto()


LINK_EXT = "lnk"


class CommandTypes(Enum):
    POLIBASE = (
        "Запрос к базе данный Polibase (Oracle)",
        "polibase",
        "полибейс",
        "oracle",
    )
    DATA_SOURCE = ("Запрос к базе данных DataSource (DS)", "ds")
    CMD = ("Консольную команду", "cmd")
    POWERSHELL = ("Powershell команду", "powershell")
    PYTHON = ("Скрипт Python", "py", "python")
    SSH = ("Команда SSH", "ssh")


class LogMessageChannels(IntEnum):
    BACKUP = auto()
    POLIBASE = auto()
    POLIBASE_BOT = auto()
    DEBUG = auto()
    DEBUG_BOT = auto()
    SERVICES = auto()
    SERVICES_BOT = auto()
    HR = auto()
    HR_BOT = auto()
    IT = auto()
    IT_BOT = auto()
    RESOURCES = auto()
    RESOURCES_BOT = auto()
    PRINTER = auto()
    POLIBASE_ERROR = auto()
    POLIBASE_ERROR_BOT = auto()
    CARD_REGISTRY = auto()
    CARD_REGISTRY_BOT = auto()
    NEW_EMAIL = auto()
    NEW_EMAIL_BOT = auto()
    TIME_TRACKING = auto()
    JOURNAL = auto()
    JOURNAL_BOT = auto()
    POLIBASE_DOCUMENT = auto()
    POLIBASE_DOCUMENT_BOT = auto()
    DEFAULT = DEBUG


class LogMessageFlags(IntEnum):
    NORMAL = 1
    ERROR = 2
    NOTIFICATION = 4
    DEBUG = 8
    SAVE = 16
    SILENCE = 32
    RESULT = 64
    WHATSAPP = 128
    ALERT = 256
    TASK = 512
    SAVE_ONCE = 1024
    SEND_ONCE = SAVE_ONCE | 2048
    DEFAULT = NORMAL


class SUBSCRIBTION_TYPE:
    ON_PARAMETERS: int = 1
    ON_RESULT: int = 2
    ON_RESULT_SEQUENTIALLY: int = 4


class WorkstationMessageMethodTypes(IntEnum):
    REMOTE = auto()
    LOCAL_MSG = auto()
    LOCAL_PSTOOL_MSG = auto()


class MessageTypes(IntEnum):
    WHATSAPP = auto()
    TELEGRAM = auto()
    WORKSTATION = auto()


class MessageStatuses(IntEnum):
    REGISTERED = 0
    COMPLETE = 1
    AT_WORK = 2
    ERROR = 3
    ABORT = 4


class SCAN:
    SPLITTER_DATA: str = "1"

    class Sources(Enum):
        POLICLINIC = ("poly", "Поликлиника", PATH_SCAN.VALUE)
        DIAGNOSTICS = (
            "diag",
            "Приёмное отделение",
            PATH_SCAN.VALUE,
        )
        TEST = ("test", "Тестовый", PATH_SCAN_TEST.VALUE)
        # Deprecated
        WS_816 = (
            "рисунок",
            "Дневной стационар",
            PATH_WS_816_SCAN.VALUE,
        )

        MEDICAL_DATA = (
            "рисунок",
            "Пересылка отсканированных документов с компьютера ws-816 (Дневной стационар)",
            PATH_MEDICAL_DATA.VALUE,
        )


class Actions(Enum):

    CHILLER_FILTER_CHANGING = ActionDescription(
        "CHILLER_FILTER_CHANGING",
        ("filter",),
        "Замена фильтра очистки воды",
        "Заменить фильтр очистки воды",
    )

    SWITCH_TO_EXTERNAL_WATER_SOURCE = ActionDescription(
        "SWITCH_TO_EXTERNAL_WATER_SOURCE",
        ("external_ws",),
        "Переход на внешнее (городское) водоснабжение",
        "Перейти на внешнее (городское) водоснабжение",
    )

    SWITCH_TO_INTERNAL_WATER_SOURCE = ActionDescription(
        "SWITCH_TO_INTERNAL_WATER_SOURCE",
        ("internal_ws",),
        "Переход на внутреннее водоснабжение",
        "Перейти на внутреннее водоснабжение",
    )

    VALENTA_SYNCHRONIZATION = ActionDescription(
        "VALENTA_SYNCHRONIZATION",
        (CONST.VALENTA.NAME, "валента"),
        "Синхронизация Валенты",
        "Совершить синхронизацию для Валенты",
        False,
        True,
        forcable=True,
    )

    TIME_TRACKING_REPORT = ActionDescription(
        "TIME_TRACKING_REPORT",
        ("tt", "урв"),
        "Отчеты по учёту рабочего времени",
        "Создать",
        False,
        False,
    )

    DOOR_OPEN = ActionDescription(
        "DOOR_OPEN",
        ("door_open",),
        "Открыть {name} дверь",
        "Открыть",
        False,
        False,
    )

    DOOR_CLOSE = ActionDescription(
        "DOOR_CLOSE",
        ("door_close",),
        "Закрыть {name} дверь",
        "Закрыть",
        False,
        False,
    )

    ATTACH_SHARED_DISKS = ActionDescription(
        "ATTACH_SHARED_DISKS",
        ("attach",),
        "Присоединить сетевые диски",
        "Присоединить",
        False,
        True,
    )

    ACTION = ActionDescription(
        "ACTION",
        ("action",),
        "Неспециализированное действие",
        None,
        False,
        True,
        forcable=False,
    )


class STATISTICS:
    class Types(Enum):
        CT = "CT"
        CT_DAY = "CT_DAY"
        CT_WEEK = "CT_WEEK"
        CT_MONTH = "CT_MONTH"
        CHILLER_FILTER = MATERIALIZED_RESOURCES.Types.CHILLER_FILTER.name
        MRI_COLDHEAD = "MRI_COLDHEAD"
        POLIBASE_DATABASE_DUMP = "POLIBASE_DATABASE_DUMP"
        POLIBASE_PERSON_REVIEW_NOTIFICATION = "POLIBASE_PERSON_REVIEW_NOTIFICATION"


class JournalType(tuple[int, OrderedNameCaptionDescription], Enum):
    GENERAL = (
        0,
        OrderedNameCaptionDescription("general", "Общий", order=1),
    )
    COMPUTER = (
        1,
        OrderedNameCaptionDescription("computer", "Компьютер", order=2),
    )
    MRI_CHILLER = (
        2,
        OrderedNameCaptionDescription("mri_chiller", "Чиллер МРТ", order=4),
    )
    MRI_GRADIENT_CHILLER = (
        3,
        OrderedNameCaptionDescription(
            "mri_gradient_chiller", "Чиллер градиентов МРТ", order=5
        ),
    )
    MRI_CLOSET_CHILLER = (
        4,
        OrderedNameCaptionDescription(
            "mri_closet_chiller", "Чиллер кабинета МРТ", order=6
        ),
    )
    CHILLER = (5, OrderedNameCaptionDescription("chiller", "Чиллер", order=3))
    COMMUNICATION_ROOM = (
        6,
        OrderedNameCaptionDescription(
            "communication_room", "Коммутационная комната", order=10
        ),
    )
    SERVER_ROOM = (
        7,
        OrderedNameCaptionDescription("server_room", "Серверная комната", order=9),
    )
    MRI_TECHNICAL_ROOM = (
        8,
        OrderedNameCaptionDescription(
            "mri_technical_room", "Техническая комната МРТ", order=7
        ),
    )
    MRI_PROCEDURAL_ROOM = (
        9,
        OrderedNameCaptionDescription(
            "mri_procedural_room", "Процедурная комната МРТ", order=9
        ),
    )
    PRINTER = (
        10,
        OrderedNameCaptionDescription("printer", "Принтер", order=11),
    )
    SERVER = (
        11,
        OrderedNameCaptionDescription("server", "Сервер", order=12),
    )
    OUTSIDE_SERVER = (
        12,
        OrderedNameCaptionDescription("outside_server", "Внешний сервер", order=13),
    )
    AGREEMENT = (
        13,
        OrderedNameCaptionDescription("agreement", "Договор и счет", order=14),
    )
    XRAY = (
        14,
        OrderedNameCaptionDescription("xray", "Рентген", order=15),
    )
    CASH_REGISTER = (
        15,
        OrderedNameCaptionDescription("cash_register", "Касса", order=16),
    )
    CT = (
        16,
        OrderedNameCaptionDescription("ct", "КТ", order=2),
    )


class Tags(tuple[int, IconedOrderedNameCaptionDescription], Enum):
    SERVICE = (
        1,
        IconedOrderedNameCaptionDescription(
            None, "Обслуживание", None, 4, CONST.VISUAL.GOOD
        ),
    )
    ERROR = (
        2,
        IconedOrderedNameCaptionDescription(
            None, "Ошибка", None, 2, CONST.VISUAL.ERROR
        ),
    )
    WARNING = (
        3,
        IconedOrderedNameCaptionDescription(
            None, "Внимание", None, 3, CONST.VISUAL.WARNING
        ),
    )
    NOTIFICATION = (
        4,
        IconedOrderedNameCaptionDescription(
            None, "Уведомление", None, 1, CONST.VISUAL.NOTIFICATION
        ),
    )
    TASK = (
        5,
        IconedOrderedNameCaptionDescription(
            None,
            "Задача",
            None,
            6,
            CONST.VISUAL.TASK,
        ),
    )
    INSPECTION = (
        6,
        IconedOrderedNameCaptionDescription(
            None,
            "Осмотр",
            None,
            5,
            CONST.VISUAL.EYE,
        ),
    )
    INFORMATION = (
        7,
        IconedOrderedNameCaptionDescription(
            None,
            "Информация",
            None,
            0,
            CONST.VISUAL.INFORMATION,
        ),
    )
