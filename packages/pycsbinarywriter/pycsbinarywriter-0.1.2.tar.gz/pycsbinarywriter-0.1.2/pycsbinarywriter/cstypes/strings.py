import struct
from asyncio import StreamReader, StreamWriter
from typing import BinaryIO, Optional

from pycsbinarywriter.cstypes.cstype import BaseCSType
from pycsbinarywriter.cstypes.seven_bit_int import int7

__all__ = ['char', 'cstring', 'string']


class CharType(BaseCSType[str]):
    def __init__(self) -> None:
        super().__init__('char', str)

    def calcsize(self) -> int:
        return 1

    def unpack(self, data: bytes) -> Optional[str]:
        if len(data) < 1:
            return None
        return chr(struct.unpack('<b', data[:1])[0])

    def pack(self, value: str) -> bytes:
        return struct.pack('<b', ord(value[0]))

    def unpackFrom(self, f: BinaryIO) -> Optional[str]:
        data: bytes = f.read(1)
        if len(data) < 1:
            return None
        return struct.unpack('<b', data)[0]

    async def asyncPackTo(self, value: str, f: StreamWriter) -> None:
        f.write(self.pack(value))

    async def asyncUnpackFrom(self, f: StreamReader) -> Optional[str]:
        data: bytes = await f.readexactly(1)
        return struct.unpack('<b', data)[0]


class CStringType(BaseCSType[str]):
    def __init__(self) -> None:
        super().__init__('cstring', str)
        self.bytesRead: int = 0

    def unpack(self, data: bytes, start: int = 0, encoding='utf-8') -> Optional[str]:
        self.bytesRead = 0
        buffer = b''
        while True:
            idx = start+self.bytesRead
            b = data[idx:idx+1]
            if b is None:
                break
            self.bytesRead += 1
            if b == b'\x00':
                break
            buffer += b
        return buffer.decode(encoding)

    def pack(self, value: str, encoding='utf-8') -> bytes:
        return value.encode(encoding)+b'\x00'

    def calcsize(self) -> int:
        return -1

    def unpackFrom(self, f: BinaryIO, encoding: str = 'utf-8') -> Optional[str]:
        self.bytesRead = 0
        buffer = b''
        while True:
            b = f.read(1)
            if b is None:
                break
            self.bytesRead += 1
            if b == b'\x00':
                break
            buffer += b
        return buffer.decode(encoding)

    async def asyncPackTo(self, value: str, f: StreamWriter, encoding: str = 'utf-8') -> None:
        f.write(self.pack(value, encoding=encoding))

    async def asyncUnpackFrom(self, f: StreamReader, encoding: str = 'utf-8') -> Optional[str]:
        self.bytesRead = 0
        buffer = b''
        while True:
            b = await f.readexactly(1)
            self.bytesRead += 1
            if b == b'\x00':
                break
            buffer += b
        return buffer.decode(encoding)


class CSStringType(BaseCSType[str]):
    def __init__(self) -> None:
        super().__init__('string', str)
        self.bytesRead: int = 0

    def unpack(self, data: bytes, start: int = 0, encoding: str = 'utf-8') -> Optional[str]:
        self.bytesRead = 0
        nbytes: int = int7.unpack(data, start)
        self.bytesRead += int7.bytesRead
        start += int7.bytesRead
        ob: bytes = data[start:start+nbytes]
        assert len(ob) == nbytes
        o: str = data[start:start+nbytes].decode(encoding)
        self.bytesRead += nbytes
        return o

    def pack(self, value: str, encoding='utf-8') -> bytes:
        return int7.pack(len(value))+value.encode(encoding)

    def calcsize(self) -> int:
        return -1

    def unpackFrom(self, f: BinaryIO, encoding: str = 'utf-8') -> Optional[str]:
        self.bytesRead = 0
        nbytes = int7.unpackFrom(f)
        self.bytesRead += int7.bytesRead

        ob: bytes = f.read(nbytes)
        assert len(ob) == nbytes
        o: str = ob.decode(encoding)
        self.bytesRead += nbytes
        return o

    async def asyncPackTo(self, value: str, f: StreamWriter, encoding: str = 'utf-8') -> None:
        f.write(self.pack(value, encoding=encoding))

    async def asyncUnpackFrom(self, f: StreamReader, encoding: str = 'utf-8') -> Optional[str]:
        self.bytesRead = 0
        nbytes: int = await int7.asyncUnpackFrom(f)
        self.bytesRead += int7.bytesRead

        ob: bytes = await f.readexactly(nbytes)
        assert len(ob) == nbytes
        o: str = ob.decode(encoding)
        self.bytesRead += nbytes
        return o


char: CharType = CharType()
cstring: CStringType = CStringType()
string: CSStringType = CSStringType()
