import asyncio
from collections.abc import AsyncGenerator, Coroutine
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, Self
from unittest import mock

import pytest

import stompman.client
from stompman import (
    AbortFrame,
    AbstractConnection,
    AckFrame,
    AnyClientFrame,
    AnyServerFrame,
    BeginFrame,
    Client,
    CommitFrame,
    ConnectedFrame,
    ConnectFrame,
    ConnectionConfirmationTimeoutError,
    ConnectionParameters,
    DisconnectFrame,
    ErrorEvent,
    ErrorFrame,
    FailedAllConnectAttemptsError,
    HeartbeatEvent,
    HeartbeatFrame,
    MessageEvent,
    MessageFrame,
    NackFrame,
    ReceiptFrame,
    SendFrame,
    SubscribeFrame,
    UnsubscribeFrame,
    UnsupportedProtocolVersionError,
)
from stompman.errors import ConnectionLostError

pytestmark = pytest.mark.anyio


class BaseMockConnection(AbstractConnection):
    @classmethod
    async def connect(cls, host: str, port: int, timeout: int) -> Self | None:
        return cls()

    async def close(self) -> None: ...
    def write_heartbeat(self) -> None: ...
    async def write_frame(self, frame: AnyClientFrame) -> None: ...
    @staticmethod
    async def read_frames(
        max_chunk_size: int, timeout: int
    ) -> AsyncGenerator[AnyServerFrame, None]:  # pragma: no cover
        await asyncio.Future()
        yield  # type: ignore[misc]


def create_spying_connection(
    read_frames_yields: list[list[AnyServerFrame]],
) -> tuple[type[AbstractConnection], list[AnyClientFrame | AnyServerFrame | HeartbeatFrame]]:
    class BaseCollectingConnection(BaseMockConnection):
        @staticmethod
        async def write_frame(frame: AnyClientFrame) -> None:
            collected_frames.append(frame)

        @staticmethod
        async def read_frames(max_chunk_size: int, timeout: int) -> AsyncGenerator[AnyServerFrame, None]:
            for frame in next(read_frames_iterator):
                collected_frames.append(frame)
                yield frame

    read_frames_iterator = iter(read_frames_yields)
    collected_frames: list[AnyClientFrame | AnyServerFrame | HeartbeatFrame] = []
    return BaseCollectingConnection, collected_frames


def get_read_frames_with_lifespan(read_frames: list[list[AnyServerFrame]]) -> list[list[AnyServerFrame]]:
    return [
        [ConnectedFrame(headers={"version": Client.PROTOCOL_VERSION, "heart-beat": "1,1"})],
        *read_frames,
        [ReceiptFrame(headers={"receipt-id": "whatever"})],
    ]


def assert_frames_between_lifespan_match(
    collected_frames: list[AnyClientFrame | AnyServerFrame | HeartbeatFrame],
    expected_frames: list[AnyClientFrame | AnyServerFrame | HeartbeatFrame],
) -> None:
    assert collected_frames[2:-2] == expected_frames


@dataclass(kw_only=True, slots=True)
class EnrichedClient(Client):
    servers: list[ConnectionParameters] = field(
        default_factory=lambda: [ConnectionParameters("localhost", 12345, "login", "passcode")], kw_only=False
    )


@pytest.fixture()
def mock_sleep(monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: PT004
    monkeypatch.setattr("asyncio.sleep", mock.AsyncMock())


def test_connection_parameters_from_pydantic_multihost_hosts() -> None:
    full_host: dict[str, Any] = {"username": "me", "password": "pass", "host": "localhost", "port": 1234}
    assert ConnectionParameters.from_pydantic_multihost_hosts([{**full_host, "port": index} for index in range(5)]) == [  # type: ignore[typeddict-item]
        ConnectionParameters(full_host["host"], index, full_host["username"], full_host["password"])
        for index in range(5)
    ]

    for key in ("username", "password", "host", "port"):
        with pytest.raises(ValueError, match=f"{key} must be set"):
            assert ConnectionParameters.from_pydantic_multihost_hosts([{**full_host, key: None}, full_host])  # type: ignore[typeddict-item, list-item]


@pytest.mark.parametrize("ok_on_attempt", [1, 2, 3])
async def test_client_connect_to_one_server_ok(ok_on_attempt: int, monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = 0

    class MockConnection(BaseMockConnection):
        @classmethod
        async def connect(cls, host: str, port: int, timeout: int) -> Self | None:
            assert (host, port) == (client.servers[0].host, client.servers[0].port)
            nonlocal attempts
            attempts += 1

            return await super().connect(host, port, timeout) if attempts == ok_on_attempt else None

    sleep_mock = mock.AsyncMock()
    monkeypatch.setattr("asyncio.sleep", sleep_mock)
    client = EnrichedClient(connection_class=MockConnection)
    assert await client._connect_to_one_server(client.servers[0])
    assert attempts == ok_on_attempt == (len(sleep_mock.mock_calls) + 1)


@pytest.mark.usefixtures("mock_sleep")
async def test_client_connect_to_one_server_fails() -> None:
    class MockConnection(BaseMockConnection):
        @classmethod
        async def connect(cls, host: str, port: int, timeout: int) -> Self | None:
            return None

    client = EnrichedClient(connection_class=MockConnection)
    assert await client._connect_to_one_server(client.servers[0]) is None


@pytest.mark.usefixtures("mock_sleep")
async def test_client_connect_to_any_server_ok() -> None:
    class MockConnection(BaseMockConnection):
        @classmethod
        async def connect(cls, host: str, port: int, timeout: int) -> Self | None:
            return await super().connect(host, port, timeout) if port == successful_server.port else None

    successful_server = ConnectionParameters("localhost", 10, "login", "pass")
    client = EnrichedClient(
        servers=[
            ConnectionParameters("localhost", 0, "login", "pass"),
            ConnectionParameters("localhost", 1, "login", "pass"),
            successful_server,
            ConnectionParameters("localhost", 3, "login", "pass"),
        ],
        connection_class=MockConnection,
    )
    await client._connect_to_any_server()
    assert client._connection
    assert client._connection_parameters == successful_server


@pytest.mark.usefixtures("mock_sleep")
async def test_client_connect_to_any_server_fails() -> None:
    class MockConnection(BaseMockConnection):
        @classmethod
        async def connect(cls, host: str, port: int, timeout: int) -> Self | None:
            return None

    client = EnrichedClient(
        servers=[
            ConnectionParameters("", 0, "", ""),
            ConnectionParameters("", 1, "", ""),
            ConnectionParameters("", 2, "", ""),
            ConnectionParameters("", 3, "", ""),
        ],
        connection_class=MockConnection,
    )

    with pytest.raises(FailedAllConnectAttemptsError):
        await client._connect_to_any_server()


async def test_client_lifespan_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    connected_frame = ConnectedFrame(headers={"version": Client.PROTOCOL_VERSION, "heart-beat": "1,1"})
    receipt_frame = ReceiptFrame(headers={"receipt-id": "whatever"})
    connection_class, collected_frames = create_spying_connection([[connected_frame], [receipt_frame]])
    write_heartbeat_mock = mock.Mock()

    class MockConnection(connection_class):  # type: ignore[valid-type, misc]
        write_heartbeat = write_heartbeat_mock

    receipt_id = "myid"
    monkeypatch.setattr(stompman.client, "uuid4", lambda: receipt_id)

    login = "login"
    async with EnrichedClient(
        [ConnectionParameters("localhost", 10, login, "%3Dpasscode")], connection_class=MockConnection
    ) as client:
        await asyncio.sleep(0)

    assert collected_frames == [
        ConnectFrame(
            headers={
                "host": client._connection_parameters.host,
                "accept-version": client.PROTOCOL_VERSION,
                "heart-beat": client.heartbeat.to_header(),
                "login": login,
                "passcode": "=passcode",
            }
        ),
        connected_frame,
        DisconnectFrame(headers={"receipt": receipt_id}),
        receipt_frame,
    ]
    write_heartbeat_mock.assert_called_once_with()


async def test_client_lifespan_connection_not_confirmed(monkeypatch: pytest.MonkeyPatch) -> None:
    async def timeout(future: Coroutine[Any, Any, Any], timeout: float) -> object:
        assert timeout == client.connection_confirmation_timeout
        task = asyncio.create_task(future)
        await asyncio.sleep(0)
        return await original_wait_for(task, 0)

    original_wait_for = asyncio.wait_for
    monkeypatch.setattr("asyncio.wait_for", timeout)

    class MockConnection(BaseMockConnection):
        @staticmethod
        async def read_frames(max_chunk_size: int, timeout: int) -> AsyncGenerator[AnyServerFrame, None]:
            yield ErrorFrame(headers={"message": "hi"})
            await asyncio.sleep(0)

    client = EnrichedClient(connection_class=MockConnection)
    with pytest.raises(ConnectionConfirmationTimeoutError) as exc_info:
        await client.__aenter__()  # noqa: PLC2801

    assert exc_info.value == ConnectionConfirmationTimeoutError(
        timeout=client.connection_confirmation_timeout, frames=[ErrorFrame(headers={"message": "hi"})]
    )


async def test_client_lifespan_unsupported_protocol_version() -> None:
    given_version = "whatever"
    connection_class, _ = create_spying_connection(
        [[ConnectedFrame(headers={"version": given_version, "heart-beat": "1,1"})]]
    )

    client = EnrichedClient(connection_class=connection_class)
    with pytest.raises(UnsupportedProtocolVersionError) as exc_info:
        await client.__aenter__()  # noqa: PLC2801

    assert exc_info.value == UnsupportedProtocolVersionError(
        given_version=given_version, supported_version=client.PROTOCOL_VERSION
    )


async def test_client_subscribe(monkeypatch: pytest.MonkeyPatch) -> None:
    destination = "/topic/test"
    subscription_id = "myid"
    monkeypatch.setattr(stompman.client, "uuid4", lambda: subscription_id)

    connection_class, collected_frames = create_spying_connection(get_read_frames_with_lifespan([]))
    async with EnrichedClient(connection_class=connection_class) as client, client.subscribe(destination):
        pass

    assert_frames_between_lifespan_match(
        collected_frames,
        [
            SubscribeFrame(
                headers={
                    "destination": destination,
                    "id": subscription_id,
                    "ack": "client-individual",
                }
            ),
            UnsubscribeFrame(headers={"id": subscription_id}),
        ],
    )


async def test_client_start_sendind_heartbeats(monkeypatch: pytest.MonkeyPatch) -> None:
    real_sleep = asyncio.sleep
    sleep_calls = []

    async def mock_sleep(delay: float) -> None:
        await real_sleep(0)
        sleep_calls.append(delay)

    monkeypatch.setattr("asyncio.sleep", mock_sleep)

    write_heartbeat_mock = mock.Mock()
    connection_class, _ = create_spying_connection(get_read_frames_with_lifespan([]))

    class MockConnection(connection_class):  # type: ignore[valid-type, misc]
        write_heartbeat = write_heartbeat_mock

    async with EnrichedClient(connection_class=MockConnection):
        await real_sleep(0)
        await real_sleep(0)
        await real_sleep(0)

    assert sleep_calls == [1, 1]
    assert write_heartbeat_mock.mock_calls == [mock.call(), mock.call(), mock.call()]


async def test_client_heartbeat_not_raises_connection_lost() -> None:
    connection_class, _ = create_spying_connection(get_read_frames_with_lifespan([]))

    class MockConnection(connection_class):  # type: ignore[valid-type, misc]
        write_heartbeat = mock.Mock(side_effect=ConnectionLostError)

    async with EnrichedClient(connection_class=MockConnection):
        await asyncio.sleep(0)


async def test_client_listen_to_events_ok() -> None:
    message_frame = MessageFrame(headers={"destination": "", "message-id": "", "subscription": ""}, body=b"hello")
    error_frame = ErrorFrame(headers={"message": "short description"})
    heartbeat_frame = HeartbeatFrame()

    connection_class, _ = create_spying_connection(
        get_read_frames_with_lifespan(
            [
                [
                    message_frame,
                    error_frame,
                    heartbeat_frame,  # type: ignore[list-item]
                ]
            ]
        )
    )
    async with EnrichedClient(connection_class=connection_class) as client:
        events = [event async for event in client.listen()]

    assert events == [
        MessageEvent(_client=client, _frame=message_frame),
        ErrorEvent(_client=client, _frame=error_frame),
        HeartbeatEvent(_client=client, _frame=heartbeat_frame),
    ]
    assert events[0].body == message_frame.body  # type: ignore[union-attr]
    assert events[1].message_header == error_frame.headers["message"]  # type: ignore[union-attr]
    assert events[1].body == error_frame.body  # type: ignore[union-attr]


@pytest.mark.parametrize("frame", [ConnectedFrame(headers={"version": ""}), ReceiptFrame(headers={"receipt-id": ""})])
async def test_client_listen_to_events_unreachable(frame: ConnectedFrame | ReceiptFrame) -> None:
    connection_class, _ = create_spying_connection(get_read_frames_with_lifespan([[frame]]))

    async with EnrichedClient(connection_class=connection_class) as client:
        with pytest.raises(AssertionError, match="unreachable"):
            [event async for event in client.listen()]


async def test_ack_nack_ok() -> None:
    subscription = "subscription-id"
    message_id = "message-id"

    message_frame = MessageFrame(
        headers={"subscription": subscription, "message-id": message_id, "destination": "whatever"}, body=b"hello"
    )
    nack_frame = NackFrame(headers={"id": message_id, "subscription": subscription})
    ack_frame = AckFrame(headers={"id": message_id, "subscription": subscription})

    connection_class, collected_frames = create_spying_connection(get_read_frames_with_lifespan([[message_frame]]))
    async with EnrichedClient(connection_class=connection_class) as client:
        events = [event async for event in client.listen()]

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, MessageEvent)
        await event.nack()
        await event.ack()

    assert_frames_between_lifespan_match(collected_frames, [message_frame, nack_frame, ack_frame])


async def test_ack_nack_connection_lost_error() -> None:
    message_frame = MessageFrame(headers={"subscription": "", "message-id": "", "destination": ""}, body=b"")
    connection_class, _ = create_spying_connection(get_read_frames_with_lifespan([[message_frame]]))

    class MockConnection(connection_class):  # type: ignore[valid-type, misc]
        @staticmethod
        async def write_frame(frame: AnyClientFrame) -> None:
            if isinstance(frame, AckFrame | NackFrame):
                raise ConnectionLostError

    async with EnrichedClient(connection_class=MockConnection) as client:
        events = [event async for event in client.listen()]
        event = events[0]
        assert isinstance(event, MessageEvent)

        await event.nack()
        await event.ack()


def get_mocked_message_event() -> tuple[MessageEvent, mock.AsyncMock, mock.AsyncMock, mock.Mock]:
    ack_mock, nack_mock, on_suppressed_exception_mock = mock.AsyncMock(), mock.AsyncMock(), mock.Mock()

    class CustomMessageEvent(MessageEvent):
        ack = ack_mock
        nack = nack_mock

    return (
        CustomMessageEvent(
            _frame=MessageFrame(
                headers={"destination": "destination", "message-id": "message-id", "subscription": "subscription"},
                body=b"",
            ),
            _client=mock.Mock(),
        ),
        ack_mock,
        nack_mock,
        on_suppressed_exception_mock,
    )


async def test_message_event_with_auto_ack_nack() -> None:
    event, ack, nack, on_suppressed_exception = get_mocked_message_event()
    exception = RuntimeError()

    async def raises_runtime_error() -> None:  # noqa: RUF029
        raise exception

    await event.with_auto_ack(
        raises_runtime_error(),
        supressed_exception_classes=(Exception,),
        on_suppressed_exception=on_suppressed_exception,
    )

    ack.assert_not_called()
    nack.assert_called_once_with()
    on_suppressed_exception.assert_called_once_with(exception, event)


async def test_message_event_with_auto_ack_ack_raises() -> None:
    event, ack, nack, on_suppressed_exception = get_mocked_message_event()

    async def func() -> None:  # noqa: RUF029
        raise ImportError

    with suppress(ImportError):
        await event.with_auto_ack(
            func(), supressed_exception_classes=(ModuleNotFoundError,), on_suppressed_exception=on_suppressed_exception
        )

    ack.assert_called_once_with()
    nack.assert_not_called()
    on_suppressed_exception.assert_not_called()


async def test_message_event_with_auto_ack_ack_ok() -> None:
    event, ack, nack, on_suppressed_exception = get_mocked_message_event()
    await event.with_auto_ack(mock.AsyncMock()(), on_suppressed_exception=on_suppressed_exception)
    ack.assert_called_once_with()
    nack.assert_not_called()
    on_suppressed_exception.assert_not_called()


async def test_send_message_and_enter_transaction_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    body = b"hello"
    destination = "/queue/test"
    expires = "whatever"
    transaction = "myid"
    content_type = "my-content-type"
    monkeypatch.setattr(stompman.client, "uuid4", lambda: transaction)

    connection_class, collected_frames = create_spying_connection(get_read_frames_with_lifespan([]))
    async with (
        EnrichedClient(connection_class=connection_class) as client,
        client.enter_transaction() as transaction,
    ):
        await client.send(
            body=body,
            destination=destination,
            transaction=transaction,
            content_type=content_type,
            headers={"expires": expires},
        )

    assert_frames_between_lifespan_match(
        collected_frames,
        [
            BeginFrame(headers={"transaction": transaction}),
            SendFrame(
                headers={  # type: ignore[typeddict-unknown-key]
                    "content-length": str(len(body)),
                    "content-type": content_type,
                    "destination": destination,
                    "transaction": transaction,
                    "expires": expires,
                },
                body=b"hello",
            ),
            CommitFrame(headers={"transaction": transaction}),
        ],
    )


async def test_send_message_and_enter_transaction_abort(monkeypatch: pytest.MonkeyPatch) -> None:
    transaction = "myid"
    monkeypatch.setattr(stompman.client, "uuid4", lambda: transaction)

    connection_class, collected_frames = create_spying_connection(get_read_frames_with_lifespan([]))
    async with EnrichedClient(connection_class=connection_class) as client:
        with suppress(AssertionError):
            async with client.enter_transaction() as transaction:
                raise AssertionError

    assert_frames_between_lifespan_match(
        collected_frames,
        [BeginFrame(headers={"transaction": transaction}), AbortFrame(headers={"transaction": transaction})],
    )
