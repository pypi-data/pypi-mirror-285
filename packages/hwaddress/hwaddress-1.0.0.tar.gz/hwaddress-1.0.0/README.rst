=========
hwaddress
=========

Lightweight python library for EUI-48, EUI-64 based hardware (MAC) addresses. 

.. contents::
    :local:


Quick start & Example usage
---------------------------

Install hwaddress

.. code:: bash

    $ pip install hwaddress

Import a few hwaddress classes and create instances
by passing string representations of hardware address to them.

.. code:: python

    >>> from hwaddress import MAC, EUI_48
    >>>
    >>> MAC('12:34:56:78:90:ab') 
    MAC(12:34:56:78:90:ab)
    >>>
    >>> EUI_48('12-34-56-78-90-ab')
    EUI_48(12-34-56-78-90-ab)

Strings passed to hwaddress classes do not have to conform to a given format.
All occurrences of :code:`'-', ':', '.', ' ', '0x'` are removed,
and as long as the remaining characters are hexadecimal digits matching the 
bit-length of the class, and instance will be created.

The following list of strings are able to create instances of both :code:`MAC` and :code:`EUI_48` classes.

.. code:: python

    >>> maclist = ['12:34:56:78:90:ab', '23-78-ab-CD-43-ff', '0xABCDEF123456', '56 78 ab cd 12 54', '5432.abcd.3456', 'ab cdef.12-45:90']
    >>>
    >>> [MAC(mac) for mac in maclist]
    [MAC(12:34:56:78:90:ab), MAC(23:78:ab:cd:43:ff), MAC(ab:cd:ef:12:34:56), MAC(56:78:ab:cd:12:54), MAC(54:32:ab:cd:34:56), MAC(ab:cd:ef:12:45:90)]
    >>>
    >>> [EUI_48(mac) for mac in maclist]
    [EUI_48(12-34-56-78-90-ab), EUI_48(23-78-ab-cd-43-ff), EUI_48(ab-cd-ef-12-34-56), EUI_48(56-78-ab-cd-12-54), EUI_48(54-32-ab-cd-34-56), EUI_48(ab-cd-ef-12-45-90)]

hwaddress classes have a `strict`_ classmethod that (by default) will only
return an instance if it matches the format defined by the class.

.. code:: python

    >>> MAC.strict('12:34:56:78:90:ab')
    MAC(12:34:56:78:90:ab)
    >>>
    >>> MAC.strict('12-34-56-78-90-ab')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/egeldmac/git/hwaddress/hwaddress/core.py", line 228, in strict
        raise ValueError(f'{address} did not pass verification.')
    ValueError: 12-34-56-78-90-ab did not pass verification.
    >>>
    >>> EUI_48.strict('12-34-56-78-90-ab')
    EUI_48(12-34-56-78-90-ab)
    >>>
    >>> EUI_48.strict('12:34:56:78:90:ab')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/egeldmac/git/hwaddress/hwaddress/core.py", line 228, in strict
        raise ValueError(f'{address} did not pass verification.')
    ValueError: 12:34:56:78:90:ab did not pass verification.

hwaddress classes also have a `verify`_ classmethod
that check if a string conforms to the format specified by the class.

.. code:: python

    >>> MAC.verify('12:34:56:78:90:ab')
    True
    >>> MAC.verify('12-34-56-78-90-ab')
    False
    >>>
    >>> EUI_48.verify('12:34:56:78:90:ab')
    False
    >>> EUI_48.verify('12-34-56-78-90-ab')
    True

There is also a `get_verifier`_ factory function available that,
when given hwaddress classes as arguments, will return a verifier function.
This function will return True if the address passed conforms to the format of 
any of the hwaddress classes passed to get_verifier.

.. code:: python

    >>> from hwaddress import get_verifier
    >>>
    >>> verifier = get_verifier(MAC, EUI_48)
    >>>
    >>> verifier('12:34:56:78:90:ab')
    True
    >>> verifier('12-34-56-78-90-ab')
    True
    >>> verifier('1234.5678.90ab')
    False

The resulting verifier can be used to filter a list of possible hardware
addresses or be passed to the `strict`_ classmethod.

.. code:: python

    >>> maclist
    ['12:34:56:78:90:ab', '23-78-ab-CD-43-ff', '0xABCDEF123456', '56 78 ab cd 12 54', '5432.abcd.3456', 'ab cdef.12-45:90']
    >>>
    >>> [EUI_48(mac) for mac in filter(verifier, maclist)]
    [EUI_48(12-34-56-78-90-ab), EUI_48(23-78-ab-cd-43-ff)]
    >>>
    >>> EUI_48.strict('12:34:56:78:90:ab', verifier=verifier)
    EUI_48(12-34-56-78-90-ab)
    >>>
    >>> EUI_48.strict('12-34-56-78-90-ab', verifier=verifier)
    EUI_48(12-34-56-78-90-ab)
    >>>
    >>> EUI_48.strict('1234.5678.90ab', verifier=verifier)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/egeldmac/git/hwaddress/hwaddress/core.py", line 228, in strict
        raise ValueError(f'{address} did not pass verification.')
    ValueError: 1234.5678.90ab did not pass verification.

Included Hardware Address Classes
---------------------------------

+---------+-------------------------------------------------+-----------------+
| Name    | Format                                          | Properties      |
+=========+=================================================+=================+
| MAC     | ff:ff:ff:ff:ff:ff                               |                 |
+---------+-------------------------------------------------+-----------------+
| MAC_64  | ff:ff:ff:ff:ff:ff:ff:ff                         |                 |
+---------+-------------------------------------------------+-----------------+
| GUID    | ffffffff-ffff-ffff-ffff-ffffffffffff            |                 |
+---------+-------------------------------------------------+-----------------+
| EUI_48  | ff-ff-ff-ff-ff-ff                               | oui, oui36, cid |
+---------+-------------------------------------------------+-----------------+
| EUI_64  | ff-ff-ff-ff-ff-ff-ff-ff                         | oui, oui36, cid |
+---------+-------------------------------------------------+-----------------+
| WWN     | ff:ff:ff:ff:ff:ff:ff:ff                         | naa, oui        |
+---------+-------------------------------------------------+-----------------+
| WWNx    | ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff | naa, oui        |
+---------+-------------------------------------------------+-----------------+
| IB_LID  | 0xffff                                          |                 |
+---------+-------------------------------------------------+-----------------+
| IB_GUID | ffff:ffff:ffff:ffff                             |                 |
+---------+-------------------------------------------------+-----------------+
| IB_GID  | ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff         | prefix, guid    |
+---------+-------------------------------------------------+-----------------+


Common Classmethods/Methods/Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**All classes inheriting from MAC will have the following methods, classmethos, and properties.**

+-----------+-------------+----------------+--------------------------------------------------------------+
| Name      | Type        | Returns        | Description                                                  |
+===========+=============+================+==============================================================+
| `verify`_ | classmethod | bool           | Verify that address conforms to formatting defined by class. |
+-----------+-------------+----------------+--------------------------------------------------------------+
| `strict`_ | classmethod | class instance | Create instance only if it passes verification.              |
+-----------+-------------+----------------+--------------------------------------------------------------+
| `format`_ | method      | str            | Format address with given formatting options.                |
+-----------+-------------+----------------+--------------------------------------------------------------+
| `int`_    | property    | int            | Integer representation of address.                           |
+-----------+-------------+----------------+--------------------------------------------------------------+
| `hex`_    | property    | str            | Hexadecimal representation of address.                       |
+-----------+-------------+----------------+--------------------------------------------------------------+
| `binary`_ | property    | str            | Padded binary representation of each hex digit in address.   |
+-----------+-------------+----------------+--------------------------------------------------------------+

.. _verify:

**verify(address)**

::

    Verify that address conforms to formatting defined by class.


.. code:: python

    >>> hwaddress.MAC.verify('12:34:56:78:90:ab')
    True
    >>> hwaddress.MAC.verify('1234.5678.90ab')
    False

.. _strict:

**strict(address, verifier=None)**

::

    Create object only if it passes verification.

    If no verifier is passed, the classes verify classmethod will be used.


.. code:: python

    >>> MAC.strict('12:34:56:78:90:ab')
    MAC(12:34:56:78:90:ab)
    >>> MAC.strict('12-34-56-78-90-ab')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/egeldmac/git/hwaddress/hwaddress/core.py", line 228, in strict
        raise ValueError(f'{address} did not pass verification.')
    ValueError: 12-34-56-78-90-ab did not pass verification.

.. _format:

**format(self, delimiter=None, group=None, upper=None)**

::

    Format address with given formatting options.

    If an option is not specified,
    the option defined by the class will be used

    Args:
      delimiter (str): character separating hex digits.
      group (int): how many hex digits in each group.
      upper (bool): True for uppercase, False for lowercase.


.. code:: python

    >>> mac = hwaddress.MAC('12:34:56:78:90:ab')
    >>> mac
    MAC(12:34:56:78:90:ab)
    >>> str(mac)
    '12:34:56:78:90:ab'
    >>> mac.format('-')
    '12-34-56-78-90-ab'
    >>> mac.format('.', 4)
    '1234.5678.90ab'
    >>> mac.format(group=4, upper=True)
    '1234:5678:90AB'

.. _int:

**int**

.. code:: python

    >>> mac.int
    20015998341291

.. _hex:

**hex**

.. code:: python

    >>> mac.hex
    '0x1234567890ab'

.. _binary:

**binary**

.. code:: python

    >>> mac.binary
    '0001 0010 0011 0100 0101 0110 0111 1000 1001 0000 1010 1011'


EUI Properties
~~~~~~~~~~~~~~

+-------+---------+--------------------------------------------+
| Name  | Returns | Description                                |
+=======+=========+============================================+
| oui   | OIU     | 24-bit Organizationally Unique Identifier. |
+-------+---------+--------------------------------------------+
| cid   | CID     | 24-bit Company ID.                         |
+-------+---------+--------------------------------------------+
| oui36 | OUI36   | 36-bit Organizationally Unique Identifier. |
+-------+---------+--------------------------------------------+


WWN Properties
~~~~~~~~~~~~~~

+------+---------+--------------------------------------------+
| Name | Returns | Description                                |
+======+=========+============================================+
| naa  | str     | Network Address Authority.                 |
+------+---------+--------------------------------------------+
| oui  | OUI     | 24-bit Organizationally Unique Identifier. |
+------+---------+--------------------------------------------+


IB_GID Properties
~~~~~~~~~~~~~~~~~

+--------+---------------+--------------------------+
| Name   | Returns       | Description              |
+========+===============+==========================+
| prefix | IB_GID_prefix | 64-bit IB_GID_prefix.    |
+--------+---------------+--------------------------+
| guid   | IB_GUID       | Embedded 64-bit IB_GUID. |
+--------+---------------+--------------------------+


Factory Functions
-----------------

new_hwaddress_class
~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> from hwaddress import new_hwaddress_class

get_address_factory
~~~~~~~~~~~~~~~~~~~

Return a hwaddress object from objs tuple
depending on the address passed as an argument.

.. code:: python

    >>> from hwaddress import get_address_factory, EUI_48, EUI_64
    >>>
    >>> hw_address = get_address_factory()
    >>>
    >>> hw_address('12:34:56:78:90:ab')
    MAC(12:34:56:78:90:ab)
    >>> hw_address('12:34:56:78:90:ab:cd:ef')
    MAC_64(12:34:56:78:90:ab:cd:ef)
    >>>
    >>> eui_address = get_address_factory(EUI_48, EUI_64)


get_verifier
~~~~~~~~~~~~

.. code:: python

    >>> from hwaddress import MAC, EUI_48, get_verifier
    >>>
    >>> class MyMAC(MAC):
    ...     _len_ = 48
    ...     _del_ = '.'
    ...     _grp_ = 4
    ...
    >>>
    >>> my_verifier = get_verifier(MAC, EUI_48, MyMAC)
    >>>
    >>> my_verifier('12:34:56:78:90:ab')
    True
    >>> my_verifier('12-34-56-78-90-ab')
    True
    >>> my_verifier('1234.5678.90ab')
    True
    >>> my_verifier('12.34.56.78.90.ab')
    False
    >>> my_verifier('1234-5678-90ab')
    False

