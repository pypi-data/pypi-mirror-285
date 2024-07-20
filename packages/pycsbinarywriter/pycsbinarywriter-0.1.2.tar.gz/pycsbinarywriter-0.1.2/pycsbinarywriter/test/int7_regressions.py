
import builtins
import unittest

from pycsbinarywriter import cstypes

__all__ = ['TestInt7Regressions']


class TestInt7Regressions(unittest.TestCase):
    def test_pack_323559(self) -> None:
        input_value: builtins.int = 323559
        expected: bytes = b"\xE7\xDF\x13"
        actual: bytes = cstypes.int7.pack(input_value)
        self.assertEqual(actual, expected)

    def test_unpack_323559(self) -> None:
        input_bytes: bytes = b"\xE7\xDF\x13"
        expected: builtins.int = 323559
        actual: builtins.int = cstypes.int7.unpack(input_bytes)
        self.assertEqual(actual, expected)
