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
import socket
from scapy.all import *

try:
    import netifaces as ni
    got_netifaces = True
except:
    got_netifaces = False


__author__ = "Keith Bannister <keith.bannister@csiro.au>"

log = logging.getLogger(__name__)

DEFAULT_INTERFACE = os.environ.get('LAMBDA_INTERFACE', 'enp175s0np0')
DEFAULT_IP = os.environ.get('LAMBDA_IP', '192.168.1.10')
DEFAULT_MAC = os.environ.get('LAMBDA_MAC', '00:11:22:33:44:55')

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
    parser.add_argument('--raw', dest='raw', action='store_true', help='Send data over raw socket - requires mac address cap_net_raw which requires sudo setcap cap_net_raw=ep ./dist/lambda_config')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Conver tdata to bytes
    # if it starts with 0x, assume it's hex.
    # otherwise convert to UTF-8 bytes
    if len(args.values) == 0:
        print('No data provided')
        return 

    if args.interface == '':
        print('No interface provided')
        return

    data = parse_values(args.values)

    if got_netifaces:
        src_ip = ni.ifaddresses(args.interface)[ni.AF_INET][0]['addr']
        src_mac = '0c:42:a1:55:c4:5a'
    else:
        src_ip = '192.168.1.1'
        src_mac = '0c:42:a1:55:c4:5a' # enp175s0np0 on blackmesa
    
    src_port = 2222
    dst_port = 3333
    
    # Create a packet
    # Send the packet
    log.info(f'Sending {len(data)} byte payload')
    if args.raw:
        try:
            packet = Ether(src=src_mac, dst=args.mac)/IP(src=src_ip, dst=args.ip)/UDP(sport=src_port, dport=dst_port)/Raw(load=data)
            hexdump(packet)
            print(packet.summary(), 'data', data.hex(), 'len', len(data), 'to', args.interface)
            sendp(packet, iface=args.interface)
        except PermissionError as e:
            log.error(f'Error sending packet: {e}')
            log.error(f'''Could not open raw socket. Insufficient permissions.
             Try running: sudo setcap cap_net_raw=ep {sys.argv[0]} or running without --raw.
             Youll need to set arp entires with 
             sudo ip neigh add <IP_ADDRESS> lladdr <MAC_ADDRESS> dev <INTERFACE> 
             (or use 'replace' instead of 'add')''')
            return
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (args.ip, dst_port))
    


if __name__ == '__main__':
    main()