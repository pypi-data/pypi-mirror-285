"""unittests for properties and methods."""

import unittest
from hwaddress import MAC, GUID, EUI_48, WWN, IB_GUID, IB_GID


class MACProps(unittest.TestCase):
    """Test common properties, methods, and comparisons."""

    def test_mac_props(self):
        """Test common properties and methods."""
        mac = MAC("12:34:56:78:90:ab")

        self.assertEqual(repr(mac), "MAC(12:34:56:78:90:ab)")
        self.assertEqual(str(mac), "12:34:56:78:90:ab")
        self.assertEqual(mac.int, 20015998341291)
        self.assertEqual(mac.hex, "0x1234567890ab")
        self.assertEqual(
            mac.binary, "0001 0010 0011 0100 0101 0110 " + "0111 1000 1001 0000 1010 1011"
        )
        self.assertEqual(mac.format("."), "12.34.56.78.90.ab")
        self.assertEqual(mac.format(""), "0x1234567890ab")
        self.assertEqual(mac.format(group=4), "1234:5678:90ab")
        self.assertEqual(mac.format(upper=True), "12:34:56:78:90:AB")

        self.assertIsInstance(MAC.strict("12:34:56:78:90:ab"), MAC)

    def test_mac_comp(self):
        """Test comparisons."""
        mac1 = MAC("1234567890ab")
        mac2 = MAC("2234567890ab")
        mac3 = MAC("1234567890ab")

        self.assertLess(mac1, mac2)
        self.assertEqual(mac1, mac3)
        self.assertEqual(hash(mac1), hash(mac3))


class GUIDstr(unittest.TestCase):
    """Test GUID grouping as expected."""

    def test_guid_str(self):
        """Test GUID grouping as expected."""
        guid = GUID("12345678-90ab-cdef-1234-567890abcdef")

        self.assertEqual(str(guid), "12345678-90ab-cdef-1234-567890abcdef")


class EUIProps(unittest.TestCase):
    """Test EUI properties."""

    def test_eui_props(self):
        """Test EUI properties."""
        eui = EUI_48("12-34-56-78-90-ab")
        self.assertEqual(str(eui.oui), "12:34:56")
        self.assertEqual(str(eui.cid), "12:34:56")
        self.assertEqual(str(eui.oui36), "12:34:56:78:9")


class WWNProps(unittest.TestCase):
    """Test WWN properties."""

    def test_wwn_props(self):
        """Test WWN properties."""
        wwn1 = WWN("12:34:56:78:90:ab:cd:ef")
        wwn5 = WWN("52:34:56:78:90:ab:cd:ef")

        self.assertEqual(wwn1.naa, "1")
        self.assertEqual(wwn5.naa, "5")

        self.assertEqual(str(wwn1.oui), "56:78:90")
        self.assertEqual(str(wwn5.oui), "23:45:67")


class IBGIDProps(unittest.TestCase):
    """Test IB_GID properties."""

    def test_ib_gid_props(self):
        """Test IB_GID properties."""
        ibgid = IB_GID("1234:5678:90ab:cdef:2234:5678:90ab:cdef")
        ibguid = IB_GUID("2234:5678:90ab:cdef")

        self.assertEqual(str(ibgid.prefix), "1234:5678:90ab:cdef")
        self.assertEqual(ibgid.guid, ibguid)
