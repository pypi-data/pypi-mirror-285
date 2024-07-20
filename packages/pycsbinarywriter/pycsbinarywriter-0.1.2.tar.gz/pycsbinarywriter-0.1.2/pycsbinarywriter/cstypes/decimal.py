from asyncio import StreamReader, StreamWriter
from decimal import Decimal
from typing import BinaryIO, Final, List, Optional

import pycsbinarywriter.cstypes.simple as simpletypes
from pycsbinarywriter.cstypes.cstype import BaseCSType

__all__ = ['decimal']

'''
This class does the incredibly painful process of converting between .NET floating-point decimals and Python Decimals.

.NET:
https://github.com/dotnet/runtime/blob/e420a0578c4964f8efbd9a14f9901c30ec686d6e/src/libraries/System.Private.CoreLib/src/System/IO/BinaryWriter.cs
https://github.com/dotnet/runtime/blob/e420a0578c4964f8efbd9a14f9901c30ec686d6e/src/libraries/System.Private.CoreLib/src/System/Decimal.cs#L590      
struct decimal {
    enumerator {
        int hi;
        int med;
        int low;
    };
    int flags = {
        SIGNED     = 0x8000000,
        SCALE_MASK = 0x00FF0000; (0-28?)
    };
}

Python:
https://github.com/python/cpython/blob/26d87fd5c7a2f94ad0a9c5385722a13a9c75fa78/Lib/_pydecimal.py#L523
class Decimal:
    def __init__(self) -> None:
        self._int: str # Yes, str. *cries*
        self._sign: Literal[0|1]
        self._exp: int

    def as_tuple(self) -> Tuple[int,Tuple[int,...],int]:
        return (self._sign,tuple(map(int,self._int)),self._exp)

Yes, this file makes my depression itch.  How could you tell? - N3X
'''


POWERS10: List[int] = [10**p for p in range(28)]
SIGN_MASK: Final[int] = 0x80_00_00_00
SCALE_MASK: Final[int] = 0x00_FF_00_00
SCALE_SHIFT: Final[int] = 16


class DecimalType(BaseCSType[Decimal]):
    def __init__(self) -> None:
        super().__init__('decimal', Decimal)

    def calcsize(self) -> int:
        return 16

    def unpack(self, data: bytes) -> Decimal:
        # lo: int = simpletypes.int32.unpack(data[0:4])
        # mid: int = simpletypes.int32.unpack(data[4:8])
        # hi: int = simpletypes.int32.unpack(data[8:12])
        n = 0
        for b in data[0:12]:
            n = (n << 8) | b

        flags: int = simpletypes.int32.unpack(data[12:16])
        scale = (flags & SCALE_MASK) >> SCALE_SHIFT

        d = Decimal(n) / Decimal(scale)
        if flags < 0:
            d = -d
        return d

    def pack(self, value: Decimal) -> bytes:
        # TODO:
        # This is incredibly fucking stupid, but I wrote it so w/e
        t = value.as_tuple()
        scale = t.exponent

        # Python does this internally, don't @ me.
        n = int(''.join(map(str, t.digits)))

        b = b''
        for _ in range(12):
            b += bytes([(n & 0xFF)])
            n = n >> 8

        flags: int = (scale << SCALE_SHIFT) & SCALE_MASK
        if value.is_signed():
            flags |= SIGN_MASK
        b += simpletypes.int32.pack(flags)
        return b

    def unpackFrom(self, f: BinaryIO) -> Decimal:
        data: bytes = f.read(16)
        if len(data) < 16:
            return None
        return self.unpack(data)

    async def asyncUnpackFrom(self, f: StreamReader) -> Optional[Decimal]:
        n = 0
        # for b in data[0:12]:
        buf = await f.readexactly(12)
        for b in buf:
            n = (n << 8) | b

        flags: int = await simpletypes.int32.asyncUnpackFrom(f)
        scale = (flags & SCALE_MASK) >> SCALE_SHIFT

        d = Decimal(n) / Decimal(scale)
        if flags < 0:
            d = -d
        return d

    async def asyncPackTo(self, value: Decimal, f: StreamWriter) -> None:
        # This is incredibly fucking stupid, but I wrote it so w/e
        t = value.as_tuple()
        scale = t.exponent

        # Python does this internally, don't @ me.
        n = int(''.join(map(str, t.digits)))

        for _ in range(12):
            f.write(bytes([(n & 0xFF)]))
            n = n >> 8

        flags: int = (scale << SCALE_SHIFT) & SCALE_MASK
        if value.is_signed():
            flags |= SIGN_MASK
        await simpletypes.int32.asyncPackTo(flags, f)


decimal: DecimalType = DecimalType()
