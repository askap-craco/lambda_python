#!/usr/bin/env python
"""
Listens for LAMBDA status packets and does useful things with them.

The packet format is:
--  Header :
--   bytes  total_bytes   Comment                 Source
--    6        6          destination MAC         table
--    6       12          source MAC              config register
--    2       14          ethertype               config register
--    20      34          IPv4 header             table

-- 8 42 UDP header 6 bytes from table, checksum = 0
--   Other things in the packet :
--    2       44          magic number
--    4       48          FPGA ID
--    4       52          packet sequence number
--    4       56          ADC lane captured in this packet. Each packet has 512 samples
--                        from one ADC. The ADC chosen cycles through 0 to (g_ADCs-1),
--                        over the course of g_ADCs packets.
--    4x32    184         State for 32 x 4byte registers
--    2x512   1208        512 x 16-bit samples


Copyright (C) CSIRO 2025
"""
import pylab
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import logging
from dataclasses import dataclass
import struct
import socket


__author__ = "Keith Bannister <keith.bannister@csiro.au>"

LAMBDA_MONITOR_PORT = 12345

log = logging.getLogger(__name__)


@dataclass
class LambdaMonitorPacket:
    magic_number: int
    fpga_id: int
    packet_sequence_number: int
    adc_lane: int
    state: np.ndarray
    samples: np.ndarray

def parse_packet(data:bytes):
    hdr_format = '<HIII'
    hdr_size = struct.calcsize(hdr_format)
    magic_number, fpga_id, packet_sequence_number, adc_lane = struct.unpack(hdr_format, data[0:hdr_size])

    state = np.frombuffer(data[hdr_size:hdr_size+4*32], dtype=np.uint32)
    assert len(state) == 32, f"Expected 32 state words, got {len(state)}"
    samples = np.frombuffer(data[hdr_size+4*32:], dtype=np.int16)
    assert len(samples) == 512, f"Expected 512 samples, got {len(samples)}"
    return LambdaMonitorPacket(magic_number, fpga_id, packet_sequence_number, adc_lane, state, samples)


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description='Script description', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Be verbose')
    parser.add_argument('-p', '--port', type=int, help='UDP port number to listen on', default=LAMBDA_MONITOR_PORT)
    parser.add_argment('-f','--fpga-id', type=int, help='FPGA ID to listen to. Others are ignored', default=0)
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # listen for packets on the given port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', args.port))
    latest_packets = {}
    adc_lines = {}
    fig = plt.figure()
    log.info('Listening on port %d', args.port)
    while True:
        data, addr = sock.recvfrom(8192)
        pkt = parse_packet(data)
        if pkt.fpga_id != args.fpga_id:
            log.debug('Ignoring packet from FPGA %d', pkt.fpga_id)
            continue
        
        last_packet = latest_packets.get(pkt.adc_lane, None)

        if last_packet is None:
            print(f'{addr[0]}{addr:1}/f{pkt.fpga_id} PSN {pkt.packet_sequence_number} registers:', map(hex, pkt.state))
            adc_lines[pkt.adc_lane] = fig.plot(pkt.samples, label=f'FPGA {pkt.fpga_id}')
        else: # seen this FPGA before
            # only print differences in state
            for i in range(32):
                if pkt.state[i] != last_packet.state[i]:
                    print(f'{addr[0]}{addr:1}/f{pkt.fpga_id} PSN {pkt.packet_sequence_number} register {i} changed from {last_packet.state[i]:08x} to {pkt.state[i]:08x}')

            adc_lines[pkt.adc_lane].set_data(pkt.samples)

        fig.canvas.draw()
        fig.canvas.flush_events()        
        latest_packets[pkt.adc_lane] = pkt



if __name__ == '__main__':
    _main()