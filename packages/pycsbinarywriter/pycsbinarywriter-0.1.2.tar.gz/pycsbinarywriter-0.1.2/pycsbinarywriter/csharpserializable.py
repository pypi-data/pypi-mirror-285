import ctypes
import datetime
from typing import Any, BinaryIO, Optional

import pytz

from pycsbinarywriter import cstypes
from pycsbinarywriter.cstypes.simple import SimpleCSType

NUL: bytes = bytes([0x00])

'''
Don't worry, I am still debating whether this class should still exist. :weeping-smile:
'''
class CSharpSerializable(object):
    def __init__(self) -> None:
        self.pos: int = 0
        self.fh: BinaryIO = None

    def unpackSpecified(self, cstype: SimpleCSType) -> Any:
        sz: int = cstype.calcsize()
        o: Any = cstype.unpackFrom(self.fh)
        self.pos += sz
        return o

    def unpackInt32(self) -> int:
        return self.unpackSpecified(cstypes.int32)

    def unpackUInt32(self) -> int:
        return self.unpackSpecified(cstypes.uint32)

    def unpackInt64(self) -> int:
        return self.unpackSpecified(cstypes.int64)

    def unpackUInt64(self) -> int:
        return self.unpackSpecified(cstypes.uint64)

    def unpack7BitInteger(self) -> int:
        o = 0
        shf = 0
        for i in range(5):
            b = ord(self.fh.read(1))
            #print(b, hex(b)[2:].zfill(2), bin(b)[2:].zfill(8), 'END' if (b & 128) == 0 else 'CONT')
            self.pos += 1
            o |= (b & 127) << shf
            shf += 7
            if not (b & 128):
                return o
        raise Exception('Bad 7bit (ran out of bytes)')

    def unpackCSharpString(self, encoding='utf-8') -> str:
        strlen = self.unpack7BitInteger()
        strb = self.fh.read(strlen)
        # print(repr(strb))
        return strb.decode('utf-8')

    def unpackNullTerminatedString(self, encoding='utf-8') -> str:
        buf: bytes = b''
        while True:
            c: bytes = self.fh.read(1)
            if c is None or c == NUL:
                return buf.decode(encoding)
            buf += c

    def unpackBoolean(self) -> bool:
        return self.unpackSpecified('<?', 1)

    def _ticks2datetime(self, cticks: ctypes.c_int64, tz: Optional[pytz.BaseTzInfo] = None) -> datetime.datetime:
        assert cticks >= ctypes.c_int64(0)
        assert cticks <= ctypes.c_int64(3155378975999999999)
        ticks: int = cticks.value
        t = datetime.datetime(1, 1, 1) + \
            datetime.timedelta(microseconds=ticks//10)
        if tz is not None:
            t = tz.localize(t)
        return t

    def unpackCSharpDateTime(self, tz: pytz.BaseTzInfo = pytz.UTC) -> datetime.datetime:
        dd = self.unpackInt64()
        cdd = ctypes.c_uint64(dd)
        #print(bin(dd)[2:].zfill(64), dd >> 62)
        chk = cdd >> ctypes.c_uint64(62)
        if chk == ctypes.c_uint64(0):
            return self._ticks2datetime(cdd, tz)
        if chk != ctypes.c_uint64(1):
            return self._ticks2datetime(cdd & ctypes.c_uint64(4611686018427387903), tz)
        return self._ticks2datetime(cdd ^ ctypes.c_uint64(4611686018427387904), tz)
