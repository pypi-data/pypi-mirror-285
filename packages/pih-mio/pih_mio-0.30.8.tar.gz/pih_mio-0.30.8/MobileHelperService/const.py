from enum import Enum, auto

import ipih

from pih import A
from pih.tools import j, js
from pih.consts.hosts import Hosts
from pih.consts import CONST, SessionFlags
from pih.collections.service import ServiceDescription
from pih.collections import StorageVariableHolder, IntStorageVariableHolder


NAME: str = "MobileHelper"

DEFAULT_COUNT = 100
ADMIN_ALIAS: str = "admin"
COUNT_ALIAS: str = "count"
VERSION: str = "0.30.8"

HOST = Hosts.WS255

SD: ServiceDescription = ServiceDescription(
    name=NAME,
    description="Mobile helper service",
    host=HOST.NAME,
    standalone_name=A.CT_SR.MOBILE_HELPER.standalone_name,
    use_standalone=True,
    version=VERSION,
)

MOBILE_HELPER_USER_SETTINGS_NAME: str = "mobile_helper_user_settings"

USER_DATA_INPUT_TIMEOUT: int = 180

MOBILE_HELPER_USER_DATA_INPUT_TIMEOUT: StorageVariableHolder = IntStorageVariableHolder(
    "MOBILE_HELPER_USER_DATA_INPUT_TIMEOUT",
    USER_DATA_INPUT_TIMEOUT,
)


class InterruptionTypes:
    NEW_COMMAND = 1
    TIMEOUT = 2
    EXIT = 3
    BACK = 4
    CANCEL = 5


FROM_FILE_REDIRECT_SYMBOL: str = "<"
FILE_PATTERN_LIST: tuple[str, ...] = (
    j(("file", CONST.SPLITTER)),
    FROM_FILE_REDIRECT_SYMBOL,
    "file=",
)  # type: ignore
PARAMETER_PATTERN: str = r"\B(\$[\w+а-яА-Я]+)(:[\w \(\)\.\,а-яА-Я]+)?"
PARAMETER_PATTERN_FOR_CMD: str = r"\B(@[\w+а-яА-Я]+)(:[\w \(\)\.\,а-яА-Я]+)?"
Groups = A.CT_AD.Groups

MAX_MESSAGE_LINE_LENGTH = 12


class MessageType(Enum):
    SEPARATE_ONCE = auto()
    SEPARATED = auto()


class COMMAND_KEYWORDS:
    PIH: tuple[str, ...] = (A.root.NAME, A.root.NAME_ALT)  # type: ignore
    EXIT: list[str] = ["exit", "выход"]
    BACK: list[str] = ["back", "назад"]
    FIND: list[str] = ["find", "поиск", "search", "найти"]
    CREATE: list[str] = ["create", "создать", "+"]
    CHECK: list[str] = ["check", "проверить"]
    ADD: list[str] = ["add", "добавить", "+"]
    PASSWORD: list[str] = ["password", "пароль"]
    USER: list[str] = ["user|s", "пользовател|ь"]
    POLIBASE: list[str] = ["polibase", "полибейс"]
    NOTES: list[str] = ["note|s", "заметк|и"]
    JOURNALS: list[str] = ["journal|s", "журнал|ы"]
    RUN: list[str] = ["run", "запуск"]
    PATIENT: list[str] = ["patient", "пациент"]
    DOCTOR: list[str] = ["doc|tor", "доктор", "врач"]
    JOKE: list[str] = ["joke", "шутка", "анекдот"]
    ASK: list[str] = ["ask"]
    ASK_YES_NO: list[str] = ["ask_yes_no"]
    SCAN: list[str] = ["scan|ed"]
    REGISTRY: list[str] = ["registry", "реестр"]
    CARD: list[str] = ["card", "карт"]


YES_VARIANTS: tuple[str, ...] = ("1", "yes", "ok", "да")
YES_LABEL: str = js(("", A.CT.VISUAL.BULLET, A.D.bold("Да"), "- отправьте", A.O.get_number(1)))
NO_LABEL: str = js(("", A.CT.VISUAL.BULLET, A.D.bold("Нет"), "- отправьте", A.O.get_number(0)))


class Flags(Enum):
    CYCLIC = 1
    ADDRESS = 2
    ALL = 4
    ADDRESS_AS_LINK = 8
    FORCED = 16
    SILENCE = 32
    HELP = 64
    SILENCE_NO = 128
    SILENCE_YES = 256
    CLI = SessionFlags.CLI.value
    ONLY_RESULT = 1024
    TEST = 2048
    SETTINGS = 4096
    OUTSIDE = SessionFlags.OUTSIDE.value


class FLAG_KEYWORDS:
    ALL_SYMBOL: str = "*"
    ADDRESS_SYMBOL: str = ">"
    LINK_SYMBOL: str = ADDRESS_SYMBOL * 2
    SILENCE: str = "_"
    ONLY_RESULT: str = SILENCE * 2
    COMMENT: str = "#"


COMMAND_LINK_SYMBOL: str = "@"

FLAG_MAP: dict[str, Flags] = {
    "-0": Flags.CYCLIC,
    "-t": Flags.TEST,
    "to": Flags.ADDRESS,
    FLAG_KEYWORDS.ADDRESS_SYMBOL: Flags.ADDRESS,
    "!": Flags.FORCED,
    FLAG_KEYWORDS.SILENCE: Flags.SILENCE,
    "_0": Flags.SILENCE_NO,
    "_1": Flags.SILENCE_YES,
    "-n": Flags.SILENCE_NO,
    "-y": Flags.SILENCE_YES,
    FLAG_KEYWORDS.ALL_SYMBOL: Flags.ALL,
    FLAG_KEYWORDS.ONLY_RESULT: Flags.ONLY_RESULT,
    "all": Flags.ALL,
    "все": Flags.ALL,
    "всё": Flags.ALL,
    "link": Flags.ADDRESS_AS_LINK,
    FLAG_KEYWORDS.LINK_SYMBOL: Flags.ADDRESS_AS_LINK,
    "?": Flags.HELP,
    "-s": Flags.SETTINGS,
}

#ADMIN_GROUPS: list[Groups] = [Groups.Admin]

COMMAND_NAME_VARIANT_SPLITTER: str = "|"

WORKSTATION_CHECK_WORD: str = "Workstation"

VERSION_STRING: str = js((VERSION, "🌫️"))
MODULE_NAME: str = j((A.root.NAME, "mio"), "-")
