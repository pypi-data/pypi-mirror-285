from MobileHelperService.api import (
    Flags,
    Output,
    OutsideOutput,
    MobileInput,
    MobileOutput,
    MobileSession,
    MobileUserInput,
    MobileMarkInput,
    get_wappi_status,
    InternalInterrupt,
    MobileHelper as Api,
    AddressedInterruption,
)
from pih.console_api import LINE
from pih.consts.errors import NotFound
from MobileHelperService.const import *
from pih import A, PIH, Stdin, PIHThread, send_message, isolate
from pih.tools import (
    j,
    n,
    e,
    nn,
    nl,
    js,
    ne,
    lw,
    one,
    nnt,
    if_else,
    ParameterList,
    BitMask as BM,
)
from pih.collections import WhatsAppMessage, User, Message
from pih.collections.service import ServiceDescription, SubscribtionResult


from collections import defaultdict
from typing import Callable, Any

SC = A.CT_SC

ISOLATED: bool = False


def is_cli(value: str | None) -> bool:
    return not e(value) and value in A.D.map(
        lambda item: item[1],
        A.D.filter(
            lambda item: lw(item[0]).endswith("cli"),
            A.D.to_list(A.CT_ME_WH.GROUP, None),  # type: ignore
        ),
    )


def is_outside(flags: int | None) -> bool:
    return BM.has(flags, Flags.OUTSIDE)


class MobileHelperService:

    is_administrator: bool = False
    max_client_count: int | None = None

    @staticmethod
    def as_administator() -> bool:
        return MobileHelperService.is_administrator or not A.D.contains(A.SYS.host(), SD.host)  # type: ignore

    @staticmethod
    def count() -> int:
        return A.SE.named_arg(COUNT_ALIAS)  # type: ignore

    client_map: dict[str, Api] = {}

    def __init__(
        self,
        max_client_count: int | None = None,
        checker: Callable[[str, int | None], bool] | None = None,
    ):
        MobileHelperService.max_client_count = max_client_count or DEFAULT_COUNT
        self.checker: Callable[[str, int | None], bool] | None = checker
        self.service_description: ServiceDescription = SD
        self.allow_send_to_next_service_in_chain: dict[str, bool] = defaultdict(bool)

    def start(self, as_standalone: bool = False) -> bool:
        A.SE.add_isolated_arg()
        A.SE.add_arg(ADMIN_ALIAS, nargs="?", const="True", type=str, default="False")
        A.SE.add_arg(COUNT_ALIAS, nargs="?", const=1, type=int, default=DEFAULT_COUNT)
        service_desctiption: ServiceDescription | None = (
            A.SRV_A.create_support_service_or_master_service_description(
                self.service_description
            )
        )
        if A.SRV.is_service_as_support(service_desctiption):
            MobileHelperService.is_administrator = lw(A.SE.named_arg(ADMIN_ALIAS)) in [
                "1",
                "true",
                "yes",
            ]
        else:
            MobileHelperService.is_administrator = False

        def service_starts_handler() -> None:
            if MobileHelperService.as_administator():
                self.create_mobile_helper(
                    recipient=A.D_TN.by_login(A.S.get(A.CT_S.PIH_CLI_ADMINISTRATOR_LOGIN)),
                    sender=A.CT_ME_WH_G.PIH_CLI,
                )
            MobileHelperService.service_starts_handler()

        if ne(service_desctiption):
            A.SRV_A.serve(
                service_desctiption,
                self.service_call_handler,  # type: ignore
                service_starts_handler,
                as_standalone=as_standalone,
                isolate=ISOLATED,
            )
            return True
        return False

    def create_mobile_helper(
        self,
        sender: str | A.CT_ME_WH_G,
        external_flags: int | None = None,
        recipient: str | None = None,
    ) -> Api:
        sender_value: str = A.D.get(sender)
        sender = sender_value
        send_from_cli: bool = is_cli(sender_value)
        if send_from_cli:
            external_flags = BM.add(external_flags, Flags.CLI)
        stdin: Stdin = Stdin()
        session: MobileSession = MobileSession(sender_value, external_flags)
        output: Output = (
            OutsideOutput(session)
            if is_outside(external_flags)
            else MobileOutput(session)
        )
        try:
            session.say_hello(recipient)
            if not send_from_cli:
                output.write_line(
                    j(
                        (
                            (
                                j(
                                    (
                                        "Добро пожаловать, ",
                                        nl(
                                            j(
                                                (
                                                    output.user.get_formatted_given_name(
                                                        session.user_given_name
                                                    ),
                                                    "!",
                                                )
                                            )
                                        ),
                                    )
                                )
                                if not BM.has(session.flags, Flags.ONLY_RESULT)
                                else None
                            ),
                            " ",
                            A.CT_V.WAIT,
                            " ",
                            A.D_F.italics("Ожидайте..."),
                        )
                    )
                )
        except NotFound as error:
            output.error(
                "К сожалению, не могу идентифицировать Вас. ИТ отдел добавит Вас после окончания процедуры идентификации."
            )
            raise error
        as_administrator: bool = send_from_cli
        if not as_administrator:
            try:
                as_administrator = A.C_U.by_group(
                    nnt(A.R_U.by_telephone_number(sender_value).data),
                    A.CT_AD.Groups.Admin,
                )
            except NotFound as _:
                pass
        input: MobileInput = MobileInput(
            stdin,
            MobileUserInput(),
            MobileMarkInput(),
            output,
            session,
            [None, -1][as_administrator],
        )
        api: Api = Api(PIH(input, output, session), stdin)
        if send_from_cli:
            api.external_flags = external_flags
        MobileHelperService.client_map[sender] = api
        return api

    @staticmethod
    def good_bye(api: Api, with_error: bool = False) -> None:
        api.say_good_bye(with_error=with_error)
        api.show_good_bye = False

    def pih_handler(
        self,
        sender: str,
        line: str | None = None,
        sender_user: User | None = None,
        external_flags: int | None = None,
        chat_id: str | None = None,
        return_result_key: str | None = None,
        args: tuple[Any] | None = None,
    ) -> None:
        send_from_cli: bool = is_cli(chat_id)
        recipient: str = sender
        if send_from_cli:
            sender = nnt(chat_id)
        mobile_helper: Api | None = None
        no_need_for_pih_keyword: bool = send_from_cli or is_outside(
            external_flags
        )
        if  sender in MobileHelperService.client_map:
            mobile_helper = MobileHelperService.client_map[sender]
            if send_from_cli:
                mobile_helper.session.say_hello(recipient)
        while True:
            try:
                if MobileHelperService.is_client_new(sender):
                    A.IW.remove(A.CT_P.NAMES.PERSON_PIN, sender)
                    if (
                        no_need_for_pih_keyword
                        or Api.check_for_starts_with_pih_keyword(line)
                    ):
                        self.allow_send_to_next_service_in_chain[sender] = (
                            MobileHelperService.is_client_list_full()
                        )
                        if not self.allow_send_to_next_service_in_chain[sender]:
                            mobile_helper = self.create_mobile_helper(sender, external_flags, recipient)
                    else:
                        self.allow_send_to_next_service_in_chain[sender] = False
                else:
                    self.allow_send_to_next_service_in_chain[sender] = False
                if sender in MobileHelperService.client_map:
                    #mobile_helper = MobileHelperService.client_map[sender]
                    if no_need_for_pih_keyword and not mobile_helper.wait_for_input():
                        if not Api.check_for_starts_with_pih_keyword(line):
                            line = js((PIH.NAME, line))
                    try:
                        if mobile_helper.do_pih(
                            line, sender_user, external_flags, return_result_key, args  # type: ignore
                        ):
                            if mobile_helper.show_good_bye:
                                if not mobile_helper.is_only_result:
                                    MobileHelperService.good_bye(mobile_helper)
                    except BaseException as error:
                        is_error: bool = not isinstance(error, InternalInterrupt)
                        if not mobile_helper.is_only_result and is_error:
                            MobileHelperService.good_bye(
                                mobile_helper, with_error=is_error
                            )
                        raise error
                break
            except NotFound:
                break
            except InternalInterrupt as interruption:
                if interruption.type == InterruptionTypes.NEW_COMMAND:
                    line = nnt(mobile_helper).line
                    if not Api.check_for_starts_with_pih_keyword(line):
                        MobileHelperService.good_bye(nnt(mobile_helper))
                        break
                elif interruption.type in (
                    InterruptionTypes.TIMEOUT,
                    InterruptionTypes.EXIT,
                ):
                    MobileHelperService.good_bye(nnt(mobile_helper))
                    break

    @staticmethod
    def is_client_list_full() -> bool:
        max_client_count: int | None = MobileHelperService.max_client_count
        if n(max_client_count):
            max_client_count = MobileHelperService.count()
        return len(MobileHelperService.client_map) == max_client_count

    @staticmethod
    def is_client_new(value: str) -> bool:
        return value not in MobileHelperService.client_map

    def receive_message_handler(
        self,
        value: str,
        sender: str,
        external_flags: int | None = None,
        chat_id: str | None = None,
        return_result_key: str | None = None,
        args: tuple[Any] | None = None,
    ) -> None:
        interruption_src: AddressedInterruption | None = None
        while True:
            try:
                if e(interruption_src):
                    self.pih_handler(
                        sender,
                        value,
                        None,
                        external_flags,
                        chat_id,
                        return_result_key,
                        args,
                    )
                else:
                    interruption: AddressedInterruption = nnt(interruption_src)
                    for recipient_user in interruption_src.recipient_user_list:  # type: ignore
                        recipient_user: User = recipient_user
                        self.pih_handler(
                            nnt(recipient_user.telephoneNumber),
                            js((PIH.NAME, interruption.command_name)),
                            interruption.sender_user,
                            interruption.flags,
                        )
                    interruption_src = None
                break
            except AddressedInterruption as local_interruption:
                interruption_src = local_interruption

    def receive_message_handler_thread_handler(self, message: WhatsAppMessage) -> None:
        self.receive_message_handler(
            nnt(message.message),
            nnt(message.sender),
            message.flags,
            message.chatId,
            message.return_result_key,
            message.args,
        )

    def service_call_handler(
        self,
        sc: SC,
        parameter_list: ParameterList,
        subscribtion_result: SubscribtionResult | None,
    ) -> Any:
        if sc == A.CT_SC.send_event:
            if nn(subscribtion_result) and nnt(subscribtion_result).result:
                if nnt(subscribtion_result).type == A.CT_SubT.ON_RESULT_SEQUENTIALLY:
                    message_src: WhatsAppMessage | None = A.D_Ex_E.whatsapp_message(
                        parameter_list
                    )

                    if nn(message_src):
                        message: WhatsAppMessage = nnt(message_src)
                        if nn(message.message) and message.message.strip().startswith(FLAG_KEYWORDS.COMMENT):
                            return
                        if (
                            A.D.get_by_value(
                                A.CT_ME_WH_W.Profiles, message.profile_id  # type: ignore
                            )
                            == A.CT_ME_WH_W.Profiles.IT
                        ):
                            flags: int | None = message.flags
                            sender_as_cli: bool = is_cli(message.chatId)
                            telephone_number: str = if_else(
                                sender_as_cli,
                                message.chatId,
                                message.sender,
                            )
                            #if sender_as_cli:
                            #    nn_message.chatId = nn_message.sender
                            #    nn_message.sender = telephone_number
                            if n(self.checker) or nnt(self.checker)(
                                telephone_number, flags
                            ):
                                if MobileHelperService.is_client_list_full():
                                    return True
                                else:
                                    if (
                                        telephone_number
                                        in self.allow_send_to_next_service_in_chain
                                    ):
                                        del self.allow_send_to_next_service_in_chain[
                                            telephone_number
                                        ]
                                    PIHThread(
                                        self.receive_message_handler_thread_handler,
                                        args=[message],
                                        name="receive_message_handler_thread_handler",
                                    )
                                    while (
                                        telephone_number
                                        not in self.allow_send_to_next_service_in_chain
                                    ):
                                        pass
                                    return self.allow_send_to_next_service_in_chain[
                                        telephone_number
                                    ]
                            else:
                                if (
                                    telephone_number
                                    in MobileHelperService.client_map
                                ):
                                    del MobileHelperService.client_map[
                                        telephone_number
                                    ]
                                return True
            return False
        return None

    @staticmethod
    def service_starts_handler() -> None:
        isolate(A.CT_SR.GATEWAY, A.CT_SR.POLIBASE_DATABASE)
        
        A.O.write_line(nl())
        A.O.blue("Configuration:")
        as_administrator: bool = MobileHelperService.as_administator()
        with A.O.make_indent(1):
            A.O.value("As admin", str(as_administrator))
            if not as_administrator:
                A.O.value("Count", str(MobileHelperService.count()))
        A.SRV_A.subscribe_on(
            A.CT_SC.send_event,
            A.CT_SubT.ON_RESULT_SEQUENTIALLY,
            SD.name,
        )
        profile = A.CT_ME_WH_W.Profiles
        if as_administrator:
            space: str = "     "

            send_message(
                j(
                    (
                        " ",
                        A.CT_V.ROBOT,
                        " ",
                        nl(A.D.bold("Pih cli запущен...")),
                        nl(js((space, A.D.bold("Сервер:"), A.SYS.host()))),
                        js((space, A.D.bold("Версия:"), VERSION_STRING)),
                        nl(),
                        space,
                        LINE,
                        nl(),
                        get_wappi_status(space, profile.IT),
                        nl() * 2,
                        get_wappi_status(space, profile.CALL_CENTRE),
                        nl() * 2,
                        get_wappi_status(space, profile.MARKETER),
                    )
                ),
                A.D.get(A.CT_ME_WH.GROUP.PIH_CLI),
                profile.IT,
                
            )

        for item in one(A.R_F.find("@mobile_helper_import_module_list")).text.splitlines():  # type: ignore
            A.R_F.execute(item)
