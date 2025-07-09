#!/usr/bin/env python
"""
Configure the lambda alveo card

Original code from Giles:

from scapy.all import *
payload = "0x000001DEADFACE00AABBCCDDEEFF0000000000000000"
payload_bytes = bytes.fromhex(payload.replace("0x", ""))
a = Ether()/IP()/UDP()/Raw(load=payload_bytes)
sendp(a, iface="ens6np0")

A successful packet is indicated by
.
Sent 1 packets.

In that example write to 
address 0x000001
the value 0xDEADFACE

Copyright (C) CSIRO 2025
"""
import os
import sys
import logging
from scapy.all import *

try:
    import netifaces as ni
    got_netifaces = True
except:
    got_netifaces = False


__author__ = "Keith Bannister <keith.bannister@csiro.au>"

log = logging.getLogger(__name__)

DEFAULT_INTERFACE = os.environ.get('LAMBDA_INTERFACE', '')
DEFAULT_IP = os.environ.get('LAMBDA_IP', '')
DEFAULT_MAC = os.environ.get('LAMBDA_MAC', '')

def tobytes(s:str):
    '''
    COnverts the given string to bytes
    If it starts with 0x it assumes hex
    Otherwise it assumes UTF-8
    '''
    if s.startswith('0x'):
        data = bytes.fromhex(s[2:])
    else:
        data = s.encode('utf-8')

    return data

def parse_int(s):
    '''
    Parse the given string into a 32 bit int

    >>> parse_int('0x12345678')
    305419896
    >>> parse_int('12345678')
    12345678
    '''
    s = s.strip().lower()
    if s.startswith("0x"):
        x = int(s, 16)
    else:
        x = int(s, 10)

    return x

def parse_values(values:list[str]):
    '''
    Parse the given values into 32 bit ints
    '''
    
    if len(values) == 1:
        data = tobytes(values[0])
    else:  # parse into 32 bit ints
        data = bytes()
        for v in values:
            x = parse_int(v)
            assert x <= 0xffffffff, f"Value {v} is too large"
            b = x.to_bytes(4, 'big')
            data += b;

    return data

def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description='Script description', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Be verbose')
    parser.add_argument('-i', '--interface', dest='interface', help='Interface to use', default=DEFAULT_INTERFACE)
    parser.add_argument('--ip', dest='ip', help='IP address', default=DEFAULT_IP)
    parser.add_argument('--mac', dest='mac', help='MAC address', default=DEFAULT_MAC)
    parser.add_argument('values', help='Either 1 big string sent verbatim, or a list to parse and send as 32 bit ints as hex or decimal e.g 0x1 0xabcd', nargs='*')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Conver tdata to bytes
    # if it starts with 0x, assume it's hex.
    # otherwise convert to UTF-8 bytes
    data = parse_values(args.values)

    if got_netifaces:
        src_ip = ni.ifaddresses(args.interface)[ni.AF_INET][0]['addr']
        src_mac = '0c:42:a1:55:c4:3a'
    else:
        src_ip = '192.168.21.1'
        src_mac = '0c:42:a1:55:c4:3a'
    
    src_port = 1234
    dst_port = 1234
    
    # Create a packet
    # Send the packet
    log.info(f'Sending {len(data)} byte payload')
    packet = Ether(src=src_mac)/IP(src=src_ip)/UDP(sport=src_port, dport=dst_port)/Raw(load=data)
    hexdump(packet)
    sendp(packet, iface=args.interface)

    


if __name__ == '__main__':
    main()