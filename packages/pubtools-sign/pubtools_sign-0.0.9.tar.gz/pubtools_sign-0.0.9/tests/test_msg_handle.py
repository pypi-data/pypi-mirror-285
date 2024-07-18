from unittest.mock import Mock


from pubtools.sign.clients.msg import _MsgClient
from pubtools.sign.models.msg import MsgError


def test_msg_handler_errors():
    mock_error = Mock()

    errors = []
    msgsc = _MsgClient(errors)
    msgsc.on_link_error(mock_error)
    assert errors == [
        MsgError(name=mock_error, description=mock_error.link.condition, source=mock_error.link)
    ]

    errors = []
    msgsc = _MsgClient(errors)
    msgsc.on_session_error(mock_error)
    assert errors == [
        MsgError(
            name=mock_error, description=mock_error.session.condition, source=mock_error.session
        )
    ]

    errors = []
    msgsc = _MsgClient(errors)
    msgsc.on_connection_error(mock_error)
    assert errors == [
        MsgError(
            name=mock_error,
            description=mock_error.connection.condition,
            source=mock_error.connection,
        )
    ]
