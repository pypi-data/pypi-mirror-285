"""Lightweight EUI-48, EUI-64 based hardware (MAC) address library."""


class MAC:
    """Generic 48 bit MAC address object.

    Base object for other hardware address objects..
    """

    _del_opts_ = ("-", ":", ".", " ", "")

    _len_ = 48  # length of address in bits. multiple of 4
    _grp_ = 2  # default group size of hex digits, (1, 2, 3, 4)
    _del_ = ":"  # default delimiter, ("-", ":", ".", " ", "")
    _upper_ = False

    def __init__(self, address):
        """Initialize address object.

        Args:
            address: A string representing the Hardware Address

                Address string does not have to conform to any format.
                '-', ':', '.', ' ', '', and '0x' will be removed from the
                string. All remaining characters must be hexadecimal digits
                of length cls._len_ / 4

        Raises:
            AttributeError: If private attribute do not conform to restraints.
            TypeError: If address is not str or int type.
            ValueError if address is int and can not fit in self._len_ bits.
        """
        # check that self._len_ is evenly divisible by 4
        if (not isinstance(self._len_, int)) or (self._len_ % 4 != 0):
            raise AttributeError("length must be an int divisible by 4")

        if not isinstance(self._del_, str):
            raise AttributeError("delimiter must be a string")

        # check that self._grp_ is an int or tuple
        if not isinstance(self._grp_, (int, tuple)):
            raise AttributeError("group must be an int or tuple.")

        # check that self._upper_ is True or False
        # if self._upper_ not in (True, False):
        if not isinstance(self._upper_, bool):
            raise AttributeError("upper must be True or False")

        if isinstance(address, str):
            self._proc_string_(address)
        else:
            raise TypeError("'address' must be a string.")

        self._restrict_()

    def _proc_string_(self, string):
        """Extract hex digits from string and add self._digits_."""
        hws = string.lower()

        stripchar = list(self._del_opts_) + ["0x"]
        for char in stripchar:
            hws = hws.replace(char, "")

        if len(hws) != int(self._len_ / 4):
            raise ValueError

        try:
            int(hws, 16)
        except ValueError:
            raise ValueError(f"'{string}' contains non hexadecimal digits.")

        self._digits_ = tuple(hws)

    def _restrict_(self):
        """Raise error if restrictions are not met."""
        pass

    def __iter__(self):
        """Pass calls to __iter__ to self.digits."""
        return self._digits_.__iter__()

    def __getitem__(self, item):
        """Pass calls to __getitem__ to self.digits."""
        return self._digits_[item]

    def __len__(self):
        """Pass calls to __len__ to self.digits."""
        return len(self._digits_)

    def __lt__(self, other):
        """Sort based on self.int."""
        return self.int < other.int

    def __eq__(self, other):
        """Equity based on self.int."""
        return self.__class__ == other.__class__ and self.int == other.int

    def __hash__(self):
        """Make hashable."""
        return hash(f"{self.__class__}{self._digits_}")

    def __repr__(self):
        """Repr based on class name and __str__."""
        return f"{self.__class__.__name__}({str(self)})"

    def __str__(self):
        """Create string based on delimiter, group, and upper."""
        grp = self._grp_

        if isinstance(grp, int):
            parts = ["".join(self[i : i + grp]) for i in range(0, len(self), grp)]
        elif isinstance(grp, tuple):
            parts = []
            s = 0
            for i in grp:
                parts.append("".join(self[s : s + i]))
                s += i

        string = self._del_.join(parts)

        if self._upper_:
            string = string.upper()

        if self._del_ == "":
            return f"0x{string}"

        return string

    @property
    def int(self):
        """Integer representation of address."""
        return int(self.hex, 16)

    @property
    def hex(self):
        """Hexadecimal representation of address."""
        return f'0x{"".join(self)}'

    @property
    def binary(self):
        """Binary representation of each hex digit in address.

        Binary groups are padded with '0's to be 4 bits long,
        and are separated with a space to improve readability.
        """
        return " ".join([bin(int(d, 16))[2:].zfill(4) for d in self])

    def format(self, delimiter=None, group=None, upper=None):
        """Format address with given formatting options.

        If an option is not specified,
        the option defined by the class will be used

        Args:
            delimiter (str): character separating hex digits.
            group (int): how many hex digits in each group.
            upper (bool): True for uppercase, False for lowercase.
        """
        if delimiter is None:
            delimiter = self._del_

        if upper not in (True, False):
            upper = self._upper_

        prop = dict(_del_=delimiter, _grp_=group or self._grp_, _upper_=upper)

        if delimiter == "":
            prop["_del_"] = delimiter

        obj = type("_", (self.__class__,), prop)(self.hex)

        return str(obj)

    @classmethod
    def verify(cls, address):
        """Verify that address conforms to formatting defined by class."""
        if not isinstance(address, str):
            raise TypeError("address must be a srting.")

        if cls._del_ != "":
            grps = address.split(cls._del_)
            if isinstance(cls._grp_, tuple):
                if cls._grp_ != tuple(len(g) for g in grps):
                    return False
            if isinstance(cls._grp_, int):
                for g in grps:
                    if len(g) != cls._grp_:
                        return False

        else:
            if not address.startswith("0x"):
                return False
            address = address[2:]
            if (len(address) * 4) != cls._len_:
                return False

        try:
            cls(address)
        except Exception:
            return False

        return True

    @classmethod
    def strict(cls, address, verifier=None):
        """Create instance only if it passes verification.

        If no verifier is passed, the classes verify classmethod will be used.
        """
        if verifier is None:
            verifier = cls.verify

        if not callable(verifier):
            raise TypeError(f"'{type(verifier).__name__}' object is not callable")

        result = verifier(address)

        if not isinstance(result, bool):
            raise TypeError(f"verifier returned '{type(result).__name__}'. Expected 'bool'.")

        if result:
            return cls(address)
        else:
            raise ValueError(f"{address} did not pass verification.")


class MAC_64(MAC):
    """Generic 64 bit MAC address object."""

    _len_ = 64


class GUID(MAC):
    """Generic 128 bit GUID/UUID address object with 8-4-4-4-12 grouping."""

    _len_ = 128
    _grp_ = (8, 4, 4, 4, 12)
    _del_ = "-"


class _EUI_Mixin_:
    """Define properties for EUI objects."""

    @property
    def oui(self):
        obj = type("OUI", (MAC,), dict(_len_=24))
        return obj("".join(self[:6]))

    @property
    def cid(self):
        obj = type("CID", (MAC,), dict(_len_=24))
        return obj("".join(self[:6]))

    @property
    def oui36(self):
        obj = type("OUI36", (MAC,), dict(_len_=36))
        return obj("".join(self[:9]))


class EUI_48(MAC, _EUI_Mixin_):
    """Represent single EUI-48 object."""

    _del_ = "-"


class EUI_64(MAC, _EUI_Mixin_):
    """Represent single EUI-64 object."""

    _len_ = 64
    _del_ = "-"


class _WWN_Mixin_:
    """Define properties for WWN objects."""

    @property
    def naa(self):
        return self[0]

    @property
    def oui(self):
        obj = type("OUI", (MAC,), dict(_len_=24))

        if self.naa in ("1", "2"):
            return obj("".join(self[4:10]))
        elif self.naa in ("5", "6"):
            return obj("".join(self[1:7]))


class WWN(MAC, _WWN_Mixin_):
    """Represent single WWN object."""

    _len_ = 64

    def _restrict_(self):
        if self[0] not in ("1", "2", "5"):
            raise ValueError("First hex digit for WWN must be 1, 2, or 5")


class WWNx(MAC, _WWN_Mixin_):
    """Represent single 128 bit extended WWN object."""

    _len_ = 128

    def _restrict_(self):
        if self[0] != "6":
            raise ValueError("First hex digit for WWNx must be 6")


class IB_LID(MAC):
    """Represent single 16 bit Infiniband LID object."""

    _len_ = 16
    _del_ = ""
    _grp_ = 4


class IB_GUID(EUI_64):
    """Represent single 64 bit Infiniband GUID object."""

    _len_ = 64
    _del_ = ":"
    _grp_ = 4


class IB_GID(MAC):
    """Represent single 128 bit Infiniband GID object."""

    _len_ = 128
    _del_ = ":"
    _grp_ = 4

    @property
    def prefix(self):
        """Return embedded 64 bit Infiniband GID prefix."""
        prop = dict(_len_=64, _del_=":", _grp_=4)

        obj = type("IB_GID_prefix", (MAC,), prop)
        return obj("".join(self[:16]))

    @property
    def guid(self):
        """Return embedded 64 bit Infiniband GUID."""
        return IB_GUID("".join(self[16:]))


def new_hwaddress_class(name, length=48, delimiter=":", grouping=2, upper=False):
    """Return a class that is a subclass of MAC."""
    if not isinstance(length, int):
        raise TypeError("length must be an int")

    prop = dict(_len_=length, _del_=delimiter, _grp_=grouping, _upper_=upper)

    obj = type(name, (MAC,), prop)

    # Try to create instance of object before returning
    obj("0" * int(length / 4))

    return obj


def get_verifier(*args):
    """Return address verifier with given hwaddress objects."""
    if args:
        for arg in args:
            if (not isinstance(arg, type)) or (not issubclass(arg, MAC)):
                raise TypeError("args must be 'MAC' or subclass of 'MAC'.")
    else:
        args = (MAC, EUI_48)

    def verifier(address):
        """Return True if address will verify.."""
        for obj in args:
            if obj.verify(address):
                return True
        return False

    return verifier


def get_address_factory(*args):
    """Return address factory with given hwaddress objects."""
    if args:
        for arg in args:
            if (not isinstance(arg, type)) or (not issubclass(arg, MAC)):
                raise TypeError("args must be 'MAC' or subclass of 'MAC'.")
    else:
        args = (MAC, MAC_64, GUID)

    def address_factory(address):
        """Return hwaddress object for address."""
        for obj in args:
            try:
                return obj(address)
            except (TypeError, ValueError):
                pass

        raise ValueError(f"{address} does not seem to be any of {args}.")

    return address_factory
