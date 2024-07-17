import ipih

from pih import A
from pih.tools import nn, ne

from MobileHelperService.service_api import MobileHelperService, is_outside


def checker(telephone_number: str, flags: int | None) -> bool:
    as_outside: bool = is_outside(flags)
    if ne(A.SRV.get_support_host_list(A.CT_SR.MOBILE_HELPER)):
        pih_cli_group_name: str = A.D.get(A.CT_ME_WH.GROUP.PIH_CLI)
        pih_cli_administator_login: str | None = A.S.get(
            A.CT_S.PIH_CLI_ADMINISTRATOR_LOGIN
        )
        
        serve: bool = (
            telephone_number == pih_cli_group_name
            or (
                nn(pih_cli_administator_login)
                and telephone_number == A.D_TN.by_login(pih_cli_administator_login)
            )
            or as_outside
        )
        if MobileHelperService.as_administator():
            return serve
        return not serve
    return True


if __name__ == "__main__":
    MobileHelperService(checker=checker).start()