
from pih.tools import nnt, one
from MobileHelperService.const import COMMAND_NAME_VARIANT_SPLITTER

def get_command_base_name(value: str) -> str:
    return value.split(COMMAND_NAME_VARIANT_SPLITTER)[0]


def mio_command(value: list[str] | str) -> str:
    if isinstance(value, str):
        return get_command_base_name(value)
    return mio_command(nnt(one(value)))
