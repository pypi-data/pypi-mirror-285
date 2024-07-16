xaal.knx
===========
This package contains a xAAL gateway for KNX BUS. 


Software 
========
The datapoint mapping (dpts.py) come from the Smarthome.py software : 
https://mknx.github.io/smarthome/plugins/knx.html (GPLv3.0) 


Install
=======
You can use both pip, with pip install xaal.knx or setup.py

You can test the package with :
python setup.py develop (or install) --user

To run the gateway:
- edit your config file (~/.xaal/xaal.knx.ini) 
- launch python -m xaal.knx

run :

If you use an USB (serial) port, you can use knxd to forward commands
between serial & multicast. 

to build knxd : 
git clone https://github.com/knxd/knxd.git
./configure --enable-usb  --prefix=/opt/knxd --disable-systemd

sudo knxd -t 1023 -e 0.0.1 -E 0.0.2:8 -i -R -S -b usb:


This configuration doesn't work out of the box. For an unknow 
reason, knxd doesn't forward knx frame to serial port. Please read
this bug report (fix) 

https://github.com/knxd/knxd/issues/340



Supported datapoints
==================== 
You must use one of this in the configuration file.

+--------+---------+------+----------------------------------+
| DPT    | Data    | Type | Values                           |
+========+=========+======+==================================+
| 1      | 1 bit   | bool | True &#124; False                |
+--------+---------+------+----------------------------------+
| 2      | 2 bit   | list | [0, 0] - [1, 1]                  |
+--------+---------+------+----------------------------------+
| 3      | 4 bit   | list | [0, 0] - [1, 7]                  |
+--------+---------+------+----------------------------------+
| 4.002  | 8 bit   | str  | 1 character (8859_1) e.g. 'c'    |
+--------+---------+------+----------------------------------+
| 5      | 8 bit   | num  | 0 - 255                          |
+--------+---------+------+----------------------------------+
| 5.001  | 8 bit   | num  | 0 - 100                          |
+--------+---------+------+----------------------------------+
| 6      | 8 bit   | num  | -128 - 127                       |
+--------+---------+------+----------------------------------+
| 7      | 2 byte  | num  | 0 - 65535                        |
+--------+---------+------+----------------------------------+
| 8      | 2 byte  | num  | -32768 - 32767                   |
+--------+---------+------+----------------------------------+
| 9      | 2 byte  | num  | -671088,64 - 670760,96           |
+--------+---------+------+----------------------------------+
| 10     | 3 byte  | foo  | datetime.time                    |
+--------+---------+------+----------------------------------+
| 11     | 3 byte  | foo  | datetime.date                    |
+--------+---------+------+----------------------------------+
| 12     | 4 byte  | num  | 0 - 4294967295                   |
+--------+---------+------+----------------------------------+
| 13     | 4 byte  | num  | -2147483648 - 2147483647         |
+--------+---------+------+----------------------------------+
| 14     | 4 byte  | num  | 4-Octet Float Value IEEE 754     |
+--------+---------+------+----------------------------------+
| 16     | 14 byte | str  | 14 characters (ASCII)            |
+--------+---------+------+----------------------------------+
| 16.001 | 14 byte | str  | 14 characters (8859_1)           |
+--------+---------+------+----------------------------------+
| 17     | 8 bit   | num  | Scene: 0 - 63                    |
+--------+---------+------+----------------------------------+
| 20     | 8 bit   | num  | HVAC: 0 - 255                    |
+--------+---------+------+----------------------------------+
| 24     | var     | str  | ulimited string (8859_1)         |
+--------+---------+------+----------------------------------+
| 232    | 3 byte  | list | RGB: [0, 0, 0] - [255, 255, 255] |
+--------+---------+------+----------------------------------+

