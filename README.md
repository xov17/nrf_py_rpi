# nrf_py_rpi
Mods of nrf2401 libraries/scripts in python for RPI

#### Test scripts

##### ping_autoack.py
Sending pings with blank ack to node1 from node0

##### alternate_twonodes.py
Sending pings alternately to node1 and node2 from node 0

##### sendback_one.py
Central node alternately sends data to 2 different nodes and receives back msg

##### two_autodetect.py
Mod of sendback_one.py with detection of live nodes

**List of Functions Needed for Controller**
[ ] Config function
[ ] Auto-detects available nodes by pinging to them, return value: array with # of addresses
[ ] Send data. args: addrNo, data. return value: 1 if blank autoack received, 0 if not
[ ] Send & receive data w/ timeout. return value:  pipeNo, result a.k.a. radio.available_pipe()
