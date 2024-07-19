"""unittests for hwaddresses factory functions."""

from random import choice, choices
from string import hexdigits
import unittest
from hwaddress import (
    get_address_factory,
    get_verifier,
    new_hwaddress_class,
    MAC,
    MAC_64,
    GUID,
    EUI_48,
    EUI_64,
    WWN,
    WWNx,
    IB_LID,
    IB_GUID,
    IB_GID,
)


def getrandhex(n):
    """Generate hex string representing bit length defined by n."""
    n = int(n / 4)
    return "".join(choices(hexdigits, k=n))


class GenericFactory(unittest.TestCase):
    """Test default factory function."""

    def test_hw_rand_hex(self):
        """Test given hex strings returns correct MAC/GUID object."""
        hw_address = get_address_factory()

        testlist = [(getrandhex(48), MAC), (getrandhex(64), MAC_64), (getrandhex(128), GUID)]

        for ti in testlist:
            self.assertIsInstance(hw_address(ti[0]), ti[1])

    def test_default_verifier(self):
        """Test that the default verifier behaves as expected."""
        verifier = get_verifier()

        tlist = ["12:34:56:78:90:ab", "12-34-56-78-90-ab"]

        flist = ["12:34:56:78:90:ab:cd:ef", "12-34-56-78-90-ab-cd-ef", "1234.5678.90ab"]

        for ts in tlist:
            self.assertTrue(verifier(ts))

        for fs in flist:
            self.assertFalse(verifier(fs))

    def test_hw_verifier(self):
        """Test verifier returns expected bool for MAC/MAC_64/GUID."""
        hw_verifier = get_verifier(MAC, MAC_64, GUID)

        tlist = [
            "12:34:56:78:90:ab",
            "12:34:56:78:90:ab:cd:ef",
            "12345678-90ab-cdef-1234-567890abcdef",
        ]

        flist = [
            "12-34-56-78-90-ab",
            "12-34-56-78-90-ab-cd-ef",
            "12345678:90ab:cdef:1234:567890abcdef",
        ]

        for ts in tlist:
            self.assertTrue(hw_verifier(ts))

        for fs in flist:
            self.assertFalse(hw_verifier(fs))


class EuiFactory(unittest.TestCase):
    """Test eui_address factory function."""

    def test_eui_rand_hex(self):
        """Test given hex strings returns correct EUI object."""
        eui_address = get_address_factory(EUI_48, EUI_64)

        testlist = [(getrandhex(48), EUI_48), (getrandhex(64), EUI_64)]

        for ti in testlist:
            self.assertIsInstance(eui_address(ti[0]), ti[1])

    def test_eui_verifier(self):
        """Test verifier returns expected bool for EUI_48/EUI_64."""
        eui_verifier = get_verifier(EUI_48, EUI_64)

        tlist = ["12-34-56-78-90-ab", "12-34-56-78-90-ab-cd-ef"]

        flist = ["12:34:56:78:90:ab", "12:34:56:78:90:ab:cd:ef"]

        for ts in tlist:
            self.assertTrue(eui_verifier(ts))

        for fs in flist:
            self.assertFalse(eui_verifier(fs))


class WwnFactory(unittest.TestCase):
    """Test wwn_address factory function."""

    def test_wwn_rand_hex(self):
        """Test given hex strings returns correct WWN object."""
        wwn_address = get_address_factory(WWN, WWNx)

        wwnhex = choice(("1", "2", "5")) + getrandhex(60)
        wwnxhex = "6" + getrandhex(124)

        testlist = [(wwnhex, WWN), (wwnxhex, WWNx)]

        for ti in testlist:
            self.assertIsInstance(wwn_address(ti[0]), ti[1])

    def test_wwn_verifier(self):
        """Test verifier returns expected bool for WWN/WWNx."""
        wwn_verifier = get_verifier(WWN, WWNx)

        tlist = [
            "12:34:56:78:90:ab:cd:ef",
            "22:34:56:78:90:ab:cd:ef",
            "52:34:56:78:90:ab:cd:ef",
            "62:34:56:78:90:ab:cd:ef:62:34:56:78:90:ab:cd:ef",
        ]

        flist = [
            "32:34:56:78:90:ab:cd:ef",
            "42:34:56:78:90:ab:cd:ef",
            "72:34:56:78:90:ab:cd:ef",
            "72:34:56:78:90:ab:cd:ef:62:34:56:78:90:ab:cd:ef",
        ]

        for ts in tlist:
            self.assertTrue(wwn_verifier(ts))

        for fs in flist:
            self.assertFalse(wwn_verifier(fs))


class IbFactory(unittest.TestCase):
    """Test ib_address factory function."""

    def test_ib_rand_hex(self):
        """Test given hex strings returns correct IB object."""
        ib_address = get_address_factory(IB_LID, IB_GUID, IB_GID)

        testlist = [(getrandhex(16), IB_LID), (getrandhex(64), IB_GUID), (getrandhex(128), IB_GID)]

        for ti in testlist:
            self.assertIsInstance(ib_address(ti[0]), ti[1])

    def test_ib_verifier(self):
        """Test verifier returns expected bool for EUI_48/EUI_64."""
        ib_verifier = get_verifier(IB_LID, IB_GUID, IB_GID)

        tlist = ["0x12ab", "1234:5678:90ab:cdef", "1234:5678:90ab:cdef:1234:5678:90ab:cdef"]

        flist = ["12ab", "0x12abcd", "1234-5678-90ab-cdef", "12345678:90ab:cdef:1234:567890abcdef"]

        for ts in tlist:
            self.assertTrue(ib_verifier(ts))

        for fs in flist:
            self.assertFalse(ib_verifier(fs))


class NewClassFactory(unittest.TestCase):
    """Test new_hwaddress_class factory function."""

    def test_new_class(self):
        """Test new_hwaddress_class factory function."""
        modellist = [
            {
                "args": ("T1MAC", 48, ".", 4, False),
                "tlist": ["1234.5678.90ab", "abcd.ef12.3456"],
                "flist": ["1234-5678-90ab", "1234.5678.90ab.cdef"],
            },
            {
                "args": ("T2MAC", 64, " ", (4, 2, 2, 4, 4), False),
                "tlist": ["1234 56 78 90ab cdef", "abcd ef 12 3456 7890"],
                "flist": ["1234-56-78-90ab-cdef", "1234.56.78.90ab"],
            },
        ]

        for model in modellist:
            HwCls = new_hwaddress_class(*model["args"])

            self.assertTrue(issubclass(HwCls, MAC))
            self.assertIsInstance(HwCls(getrandhex(model["args"][1])), HwCls)

            for ts in model["tlist"]:
                self.assertTrue(HwCls.verify(ts))

            for fs in model["flist"]:
                self.assertFalse(HwCls.verify(fs))
