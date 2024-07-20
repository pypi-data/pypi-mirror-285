from asyncio import StreamReader, StreamWriter
from typing import BinaryIO, Optional

from pycsbinarywriter.cstypes.cstype import BaseCSType

__all__ = ['int7']


class SevenBitIntType(BaseCSType[int]):
    '''
    7-bit integer, as used in Strings.
    '''

    def __init__(self) -> None:
        super().__init__('int7', int)
        self.bytesRead: int = 0

    def unpack(self, data: bytes, start: int = 0) -> Optional[int]:
        o = 0
        shf = 0
        self.bytesRead = 0
        for i in range(5):
            b = ord(data[start+i:start+i+1])
            self.bytesRead += 1
            o |= (b & 127) << shf
            shf += 7
            if not (b & 128):
                return o
        raise Exception('Bad 7bit (ran out of bytes)')

    def pack(self, value: int) -> bytes:
        o = b''
        while value >= 0x80:
            o += bytes([(value | 0x80) & 0xFF])
            value >>= 7
        return o + bytes([value])

    def calcsize(self) -> int:
        return -1

    def unpackFrom(self, f: BinaryIO) -> Optional[int]:
        o = 0
        shf = 0
        self.bytesRead = 0
        for i in range(5):
            b = ord(f.read(1))
            # print(b, hex(b)[2:].zfill(2), bin(b)[2:].zfill(8), 'END' if (b & 128) == 0 else 'CONT')
            self.bytesRead += 1
            o |= (b & 127) << shf
            shf += 7
            if not (b & 128):
                return o
        raise Exception('Bad 7bit (ran out of bytes)')

    async def asyncUnpackFrom(self, f: StreamReader) -> Optional[int]:
        o = 0
        shf = 0
        self.bytesRead = 0
        for i in range(5):
            b = ord(await f.readexactly(1))
            # print(b, hex(b)[2:].zfill(2), bin(b)[2:].zfill(8), 'END' if (b & 128) == 0 else 'CONT')
            self.bytesRead += 1
            o |= (b & 127) << shf
            shf += 7
            if not (b & 128):
                return o
        raise Exception('Bad 7bit (ran out of bytes)')

    def packTo(self, value: int, f: BinaryIO) -> None:
        while value >= 0x80:
            f.write(bytes([value | 0x80]))
            value >>= 7
        f.write(bytes([value]))

    async def asyncPackTo(self, value: int, f: StreamWriter) -> None:
        while value >= 0x80:
            f.write(bytes([value | 0x80]))
            value >>= 7
        f.write(bytes([value]))


int7: SevenBitIntType = SevenBitIntType()
