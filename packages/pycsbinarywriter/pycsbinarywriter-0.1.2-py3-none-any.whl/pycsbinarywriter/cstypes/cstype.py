from asyncio import StreamReader, StreamWriter
import struct
from typing import Type, TypeVar, Generic, BinaryIO, Optional

__all__ = ['BaseCSType', 'SimpleCSType']

T = TypeVar('T')


class BaseCSType(Generic[T]):
    def __init__(self, name: str, pytype: Type) -> None:
        self.name: str = name
        self.pytype: Type = pytype

    def unpack(self, data: bytes) -> Optional[T]:
        return None

    def pack(self, value: T) -> bytes:
        return b''

    def packTo(self, value: T, f: BinaryIO) -> None:
        pass

    async def asyncPackTo(self, value: T, f: StreamWriter) -> None:
        pass

    def calcsize(self) -> int:
        return -1

    def unpackFrom(self, f: BinaryIO) -> Optional[T]:
        return None

    async def asyncUnpackFrom(self, f: StreamReader) -> Optional[T]:
        return None


class SimpleCSType(BaseCSType[T]):
    def __init__(self, name: str, fmt: str, size: int, pytype: Type) -> None:
        super().__init__(name, pytype)
        self.format: str = fmt
        self.size: int = size

    def unpack(self, data: bytes) -> Optional[T]:
        sz: int = self.calcsize()
        if len(data) < sz:
            return None
        return struct.unpack(self.format, data[:sz])[0]

    def pack(self, value: T) -> bytes:
        return struct.pack(self.format, value)

    def packTo(self, value: T, f: BinaryIO) -> None:
        f.write(self.pack(value))

    async def asyncPackTo(self, value: T, f: StreamWriter) -> None:
        f.write(self.pack(value))

    async def asyncUnpackFrom(self, f: StreamReader) -> Optional[T]:
        sz: int = self.calcsize()
        data: bytes = await f.read(sz)
        if len(data) < sz:
            return None
        return struct.unpack(self.format, data)[0]

    def calcsize(self) -> int:
        return self.size if self.size > 0 else struct.calcsize(self.format)

    def unpackFrom(self, f: BinaryIO) -> Optional[T]:
        sz: int = self.calcsize()
        data: bytes = f.read(sz)
        if len(data) < sz:
            return None
        return struct.unpack(self.format, data)[0]
