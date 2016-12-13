# nrf_py_rpi
Mods of nrf2401 libraries/scripts in python for RPI

#### Test scripts
Succeeding scripts usually build up on previous test script.
Will clean this up later into a library.

##### ping_autoack.py
Sending pings with blank ack to node1 from node0

##### alternate_twonodes.py
Sending pings alternately to node1 and node2 from node 0

##### sendback_one.py
Central node alternately sends data to 2 different nodes and receives back msg

##### two_autodetect.py
Mod of sendback_one.py with detection of live nodes

##### sendstring.py
Send string of any size

**List of Functions Needed for Controller**
[ ] Config function
[ ] Auto-detects available nodes by pinging to them, return value: array with # of addresses
[ ] Send data. args: addrNo, data. return value: 1 if blank autoack received, 0 if not
[ ] Send & receive data w/ timeout. return value:  pipeNo, result a.k.a. radio.available_pipe()





sendString(data_to_send, addr)
Send string, will detect length of string and send this first. 
Will also send md5 representation to ensure that the whole string sent was complete :))))
(16 bytes only for 32 byte string!)
Inputs:
Data_to_send: string
Addr: address to send to
Return Values:
Return 1 if sent
Special Strings/Commands:

recvString(addr, len_string, sha_data)
Will receive string based on anticipated length
Will compile string
Tiwala muna na di kailangan ng ordering haha
After compiling string, will compare to sha_data
Inputs:
Address to read from
Length of anticipated string
md5 of anticipated string (16 bytes only for 32 byte string!)
Return Values:
Return string if properly received, if not, return “Error Recv”
