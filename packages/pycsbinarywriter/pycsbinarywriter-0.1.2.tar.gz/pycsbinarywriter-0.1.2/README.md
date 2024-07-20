# pyCSBinaryWriter

A simple library for .NET binary (de)serialization.

This package gives developers access to simple method calls from decoding
binary data written by .NET BinaryWriter.

## Limitations

* Decimal is not implemented yet. Pull requests are welcome.
* asyncio support is brand new and may be buggy.

## Installation

```shell
$ pip install -U pycsbinarywriter
```

## Usage

```python
from pycsbinarywriter import cstypes

# Decode .NET 7-bit-prefixed string
assert 'abc123' == cstypes.string.unpack(b'\x06\x61\x62\x63\x31\x32\x33')

# Decode .NET uint8 (ubyte)
assert 127 == cstypes.uint8.unpack(b'\x7f')

# Encode .NET int16
assert b'\x2e\xfb' == cstypes.int16.pack(-1234)
```

## License

MIT License
