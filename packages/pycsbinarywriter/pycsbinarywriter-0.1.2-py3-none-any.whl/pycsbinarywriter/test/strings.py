import unittest
from pycsbinarywriter import cstypes
__all__ = ['TestSimpleSerializers']


class TestStringSerializers(unittest.TestCase):
    def test_string_pack(self) -> None:
        input_value: str = 'abc123'
        expected: bytes = b'\x06\x61\x62\x63\x31\x32\x33'
        actual: bytes = cstypes.string.pack(input_value)
        self.assertEqual(actual, expected)

    def test_string_unpack(self) -> None:
        input_bytes: bytes = b'\x06\x61\x62\x63\x31\x32\x33'
        expected: str = 'abc123'
        actual: bytes = cstypes.string.unpack(input_bytes)
        self.assertEqual(actual, expected)

    def test_cstring_pack(self) -> None:
        input_value: str = 'abc123'
        expected: bytes = b'\x61\x62\x63\x31\x32\x33\x00'
        actual: bytes = cstypes.cstring.pack(input_value)
        self.assertEqual(actual, expected)

    def test_cstring_unpack(self) -> None:
        input_bytes: bytes = b'\x61\x62\x63\x31\x32\x33\x00'
        expected: str = 'abc123'
        actual: bytes = cstypes.cstring.unpack(input_bytes)
        self.assertEqual(actual, expected)

    def test_char_pack(self) -> None:
        input_value: str = 'a'
        expected: bytes = b'\x61'
        actual: bytes = cstypes.char.pack(input_value)
        self.assertEqual(actual, expected)

    def test_char_unpack(self) -> None:
        input_bytes: bytes = b'\x61'
        expected: str = 'a'
        actual: str = cstypes.char.unpack(input_bytes)
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
