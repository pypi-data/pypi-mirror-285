import asyncio
import socket
from collections.abc import AsyncGenerator, Generator, Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from typing import Protocol, Self, TypeVar, cast

from stompman.errors import ConnectionLostError
from stompman.frames import AnyClientFrame, AnyServerFrame
from stompman.serde import NEWLINE, FrameParser, dump_frame

FrameType = TypeVar("FrameType", bound=AnyClientFrame | AnyServerFrame)


@dataclass(kw_only=True)
class AbstractConnection(Protocol):
    active: bool = True

    @classmethod
    async def connect(cls, host: str, port: int, timeout: int) -> Self | None: ...
    async def close(self) -> None: ...
    def write_heartbeat(self) -> None: ...
    async def write_frame(self, frame: AnyClientFrame) -> None: ...
    def read_frames(self, max_chunk_size: int, timeout: int) -> AsyncGenerator[AnyServerFrame, None]: ...


@dataclass(kw_only=True, slots=True)
class Connection(AbstractConnection):
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    @classmethod
    async def connect(cls, host: str, port: int, timeout: int) -> Self | None:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        except (TimeoutError, ConnectionError, socket.gaierror):
            return None
        else:
            return cls(reader=reader, writer=writer)

    async def close(self) -> None:
        self.writer.close()
        with suppress(ConnectionError):
            await self.writer.wait_closed()
        self.active = False

    @contextmanager
    def _reraise_connection_lost(self, *causes: type[Exception]) -> Generator[None, None, None]:
        try:
            yield
        except causes as exception:
            self.active = False
            raise ConnectionLostError from exception

    def write_heartbeat(self) -> None:
        with self._reraise_connection_lost(RuntimeError):
            return self.writer.write(NEWLINE)

    async def write_frame(self, frame: AnyClientFrame) -> None:
        with self._reraise_connection_lost(RuntimeError):
            self.writer.write(dump_frame(frame))
        with self._reraise_connection_lost(ConnectionError):
            await self.writer.drain()

    async def _read_non_empty_bytes(self, max_chunk_size: int) -> bytes:
        while (chunk := await self.reader.read(max_chunk_size)) == b"":  # pragma: no cover (it defenitely happens)
            await asyncio.sleep(0)
        return chunk

    async def read_frames(self, max_chunk_size: int, timeout: int) -> AsyncGenerator[AnyServerFrame, None]:
        parser = FrameParser()

        while True:
            with self._reraise_connection_lost(ConnectionError, TimeoutError):
                raw_frames = await asyncio.wait_for(self._read_non_empty_bytes(max_chunk_size), timeout=timeout)

            for frame in cast(Iterator[AnyServerFrame], parser.parse_frames_from_chunk(raw_frames)):
                yield frame
