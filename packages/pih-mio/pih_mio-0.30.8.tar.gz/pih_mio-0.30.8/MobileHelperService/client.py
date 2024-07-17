import ipih

from enum import Enum
from typing import Callable, Any
from collections import defaultdict

from pih import A, IClosable

from MobileHelperService.api import (
    Flags,
    mio_command,
    MobileOutput,
    MobileSession,
    format_given_name,
    MobileHelperUserSettiongsHolder,
)
from MobileHelperService.const import (
    SD,
    ADMIN_ALIAS,
    COMMAND_KEYWORDS,
    InterruptionTypes,
)
from pih.collections import WhatsAppMessage
from pih.tools import ne, n, j, nn, ParameterList
from pih.collections.service import ServiceDescription
from pih.consts.errors import OperationCanceled, OperationExit

ANSWER: dict[str, list[str]] = defaultdict(list)


class Client:
    class CT:
        S_UP = A.CT_AD.UserProperies

    @staticmethod
    def start(
        host: str,
        as_admin: bool = False,
        as_standalone: bool = False,
        version: str | None = None,
        pih_version: str | None = None,
        show_output: bool = True,
    ) -> bool:
        service_description: ServiceDescription = A.D.fill_data_from_source(
            ServiceDescription(), SD
        )  # type: ignore
        service_description.host = host or service_description.host
        service_description.parameters = (
            j((A.CT.ARGUMENT_PREFIX, ADMIN_ALIAS)) if as_admin else None
        )
        service_description.pih_version = pih_version or service_description.pih_version
        service_description.use_standalone = as_standalone
        service_description.version = version or service_description.version
        return A.SRV_A.start(
            service_role_or_description=service_description,
            check_if_started=False,
            show_output=show_output,
        )  # type: ignore

    @staticmethod
    def create_output(recipient: str | Enum) -> MobileOutput:
        recipient = A.D.get(recipient)
        session: MobileSession = MobileSession(recipient, A.D.get(Flags.SILENCE))  # type: ignore
        recipient_as_whatsapp_group: bool = recipient.endswith(A.CT_ME_WH.GROUP_SUFFIX)  # type: ignore
        output: MobileOutput = MobileOutput(session)
        session.output = output
        if not recipient_as_whatsapp_group:
            output.user.get_formatted_given_name = lambda: format_given_name(
                session, output  # type: ignore
            )  # type: ignore
            session.say_hello(recipient)  # type: ignore
        return output

    @staticmethod
    def waiting_for_result(
        command: str,
        recipient: str | Enum,
        chat_id: str | Enum | None = None,
        flags: int | None = None,
        args: tuple[Any] | None = None,
    ) -> Any | None:
        recipient = A.D.get(recipient)
        chat_id = A.D.get(chat_id)
        return_result_key: str = A.D.uuid()
        A.A_MIO.send(
            command, recipient, chat_id, flags, return_result_key, args
        )

        class DH:
            exception: BaseException | None = None

        def internal_handler(pl: ParameterList, listener: IClosable) -> None:
            event, parameters = A.D_Ex_E.with_parameters(pl)
            if event == A.CT_E.RESULT_WAS_RETURNED:
                if parameters[0] == return_result_key:
                    if parameters[2] == A.D.get(InterruptionTypes.CANCEL):
                        DH.exception = OperationCanceled()
                    if parameters[2] == A.D.get(InterruptionTypes.EXIT):
                        DH.exception = OperationExit()
                    ANSWER[j((recipient, chat_id), "-")].append(parameters[1])
                    listener.close()

        A.E.on_event(internal_handler)
        if nn(DH.exception):
            raise DH.exception  # type: ignore
        return ANSWER[j((recipient, chat_id), "-")][-1]

    @staticmethod
    def ask(
        title: str,
        recipient: str | Enum,
        chat_id: str | Enum | None = None,
        flags: int | None = None,
    ) -> Any | None:
        return Client.waiting_for_result(
            mio_command(COMMAND_KEYWORDS.ASK), recipient, chat_id, flags, (title,)
        )

    @staticmethod
    def ask_yes_no(
        title: str,
        recipient: str | Enum,
        chat_id: str | Enum | None = None,
        flags: int | None = None,
    ) -> bool | None:
        return Client.waiting_for_result(
            mio_command(COMMAND_KEYWORDS.ASK_YES_NO),
            recipient,
            chat_id,
            flags,
            (title,),
        )

    @staticmethod
    def waiting_for_answer_from(
        recipient: str,
        handler: Callable[[str, Callable[[], None]], None] | None = None,
    ) -> str | None:
        def internal_handler(message: str, close_handler: Callable[[], None]) -> None:
            ANSWER[recipient].append(message)
            if n(handler):
                close_handler()
            else:
                handler(message, close_handler)  # type: ignore

        Client.waiting_for_input_from(recipient, internal_handler)
        return ANSWER[recipient][-1]

    @staticmethod
    def waiting_for_input_from(
        recipient: str,
        handler: Callable[[str, Callable[[], None]], None] | None = None,
    ) -> None:
        def internal_handler(pl: ParameterList, listener: IClosable) -> None:
            message: WhatsAppMessage | None = A.D_Ex_E.whatsapp_message(pl)
            if ne(message) and A.D_F.telephone_number(
                message.sender  # type: ignore
            ) == A.D_F.telephone_number(recipient):
                if n(handler):
                    listener.close()
                else:
                    handler(message.message, listener.close)  # type: ignore

        A.E.on_event(internal_handler)

    class SETTINGS:
        class USER(MobileHelperUserSettiongsHolder):
            pass
