from typing import Any, List

from ..models.msg import MsgError

from proton.handlers import MessagingHandler
import proton


class _MsgClient(MessagingHandler):
    def __init__(self, errors: List[MsgError]) -> None:
        super().__init__()
        self.errors = errors

    def on_error(self, event: proton.Event, source: Any = None) -> None:
        self.errors.append(
            MsgError(
                name=event,
                description=source.condition or source.remote_condition,
                source=source,
            )
        )
        event.container.stop()

    def on_link_error(self, event: proton.Event) -> None:
        self.on_error(event, event.link)

    def on_session_error(self, event: proton.Event) -> None:
        self.on_error(event, event.session)

    def on_connection_error(self, event: proton.Event) -> None:
        self.on_error(event, event.connection)

    def on_transport_error(self, event: proton.Event) -> None:
        self.on_error(event, event.transport)
