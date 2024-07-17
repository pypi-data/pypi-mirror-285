from dataclasses import dataclass
from enum import Enum

import ipih

from pih.tools import BitMask as BM, EnumTool


@dataclass
class MobileHelperUserSettings:
    flags: int = 0
    
    def has_flag(self, value: int | Enum) -> bool:
        return BM.has(self.flags, EnumTool.get(value))