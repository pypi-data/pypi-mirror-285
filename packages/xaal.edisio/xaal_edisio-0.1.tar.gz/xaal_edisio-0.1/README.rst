

xaal.edisio
===========
This is a xAAL package to support Edisio wireless switches.


WARNING
-------
We only support Edisio wireless switches: https://www.edisio.com/wireless-switches-efcb/.
Edisio doesn't provide docs, protocol example or anything else. We had to figure out stuff by ourselves.


Sample outputs
--------------

.. code-block:: bash

    AA = Address ?
    BB = Button nb
    CC = Looks like a checksum
    EE = END of Data
                                                                AA AA AA AA BB    CC          EE EE EE
    2018-09-27 15:37:49 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 01 01 1f 01 00 03 64 0d 0a
    2018-09-27 15:37:49 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 01 01 1f 01 00 03 64 0d 0a
    2018-09-27 15:37:49 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 01 01 1f 01 00 03 64 0d 0a
    2018-09-27 15:37:49 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 01 01 1f 01 00 03 64 0d 0a
    2018-09-27 15:37:54 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 03 01 1f 01 00 03 64 0d 0a
    2018-09-27 15:37:54 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 03 01 1f 01 00 03 64 0d 0a
    2018-09-27 15:37:54 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 03 01 1f 01 00 03 64 0d 0a
    2018-09-27 15:37:54 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 00 74 bc b6 03 01 1f 01 00 03 64 0d 0a

    2018-09-27 15:38:00 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 01 01 1d 01 00 03 64 0d 0a
    2018-09-27 15:38:00 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 01 01 1d 01 00 03 64 0d 0a
    2018-09-27 15:38:00 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 01 01 1d 01 00 03 64 0d 0a
    2018-09-27 15:38:00 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 01 01 1d 01 00 03 64 0d 0a
    2018-09-27 15:38:09 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 03 01 1b 01 00 03 64 0d 0a
    2018-09-27 15:38:09 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 03 01 1b 01 00 03 64 0d 0a
    2018-09-27 15:38:09 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 03 01 1b 01 00 03 64 0d 0a
    2018-09-27 15:38:09 i7 xaal.edisio[18674] DEBUG [16] 6c 76 63 06 73 74 2b 03 01 1b 01 00 03 64 0d 0a

Usage
------
- Edit *edisio.ini* according to your needs, mainly change the serial port, by default
  everything else should be Ok.
