#!/usr/bin/env python
"""
Sets the position of the JTAG mux on Jospephs test lambda board.
Derived from his original borland C code.

Joseph's note:
The FT232R device has its serial number programmed as “JTAG_Sel” hence
 
char devName[30]="JTAG_Sel";
 
      ftStatus = FT_OpenEx(devName,FT_OPEN_BY_SERIAL_NUMBER, &ftHandleB);
 
      ftStatus = FT_SetBitMode(ftHandleB,0xf0,0x20);  //0xc0 - c3,c2 outputs; c1,c0 inputs, 0x20 - CBUS BitBang
 
 
actual setting the bits
 
      value = 0xc0;
      value |= (Port&0x3)<<2;
      ftStatus = FT_SetBitMode(ftHandleB,value,0x20);
 
 
the two bit “Port” mapping is
 
    if(Port==3)
      sprintf(str,"Connected to JTAG_Mux Top Right");
    if(Port==1)
      sprintf(str,"Connected to JTAG_Mux Bot Left");
    if(Port==2)
      sprintf(str,"Connected to JTAG_Mux Top Left");
    if(Port==0)
      sprintf(str,"Connected to JTAG_Mux Bot Right");
 
cheers,
joseph

Copyright (C) CSIRO 2025
"""
import numpy as np
import os
import sys
import loggingfrom pyftdi.gpio import GpioController, GpioException


__author__ = "Keith Bannister <keith.bannister@csiro.au>"

def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description='Script description', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Be verbose')
    parser.add_argument(dest='position', type=int, options=[0,1,2,3], help='Position to set the mux to')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    mux_val = args.position
    assert 0 <= mux_val <= 3, "Mux position must be 0, 1, 2, or 3"

    # FTDI GPIO bit positions: bits 2 and 3 used for mux (as in original C code)
    gpio_pins = 0x0C  # binary 00001100, use D2 and D3

    # Bitbang value: bits 2 and 3 get mux_val << 2
    value = (mux_val & 0x3) << 2

    #         ftStatus = FT_SetBitMode(ftHandleB,0xf0,0x20);  //0xc0 - c3,c2 outputs; c1,c0 inputs, 0x20 - CBUS BitBang

    try:
        gpio = GpioController()
        gpio.configure('ftdi://::/1', direction=gpio_pins)
        gpio.write_port(value)
        time.sleep(0.05)
        print(f"Mux set to position {mux_val}")
        gpio.close()
    except GpioException as e:
        print("Error communicating with FTDI device:", e)
        sys.exit(1)

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    _main()