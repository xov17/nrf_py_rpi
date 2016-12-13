#!/usr/bin/env python

import hashlib
import logging

logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s (%(threadName)-2s) %(message)s')


def parsePacket(data_to_send):
    """
        Accepts string
        Returns list of 32 byte strings (if applicable)
        For sending packets
    """
    packet_list = []
    len_data = len(data_to_send)

    i = 0
    while (1):
        starting = i*32
        if (len_data <= 32):
            end = starting + len_data
            packet_list.append(data_to_send[starting:end])
            break
        else:
            end = starting + 32
            packet_list.append(data_to_send[starting:end])
            len_data = len_data - 32
            print len_data
        i = i + 1

    return packet_list




if __name__ == '__main__':

    data_to_send = "Someday we'll know, why I wasn't made for you"
    hash_orig = hashlib.md5()
    hash_orig.update(data_to_send)
    print hash_orig.hexdigest()
    print len(hash_orig.hexdigest())
    packet_list = parsePacket(data_to_send)
    print packet_list
    for i in range(len(packet_list)):
        print ('{}: {}'.format(i, packet_list[i]))
    joined_list = "".join(packet_list)
    print joined_list
    hash_joined = hashlib.md5()
    hash_joined.update(joined_list)
    print hash_joined.hexdigest()
    print len(hash_joined.hexdigest())


