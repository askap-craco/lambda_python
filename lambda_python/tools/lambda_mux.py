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

Keith's notes:
This has the useful information:
https://strawberry-linux.com/pub/AN232R-01_FT232RBitBangModes.pdf

CBUS Bit Bang mode is enabled using the FT_SetBitMode command. A
value of 0x20 will enable it and a value of 0x00 will reset the device mode.
Note that the CBUS pins must also be configured for CBUS Bit Bang in the
FT232R EEPROM.
FT_SetBitMode also provides the means to write data to the CBUS pins.
The upper nibble of the Mask parameter controls which pins are inputs or
outputs, while the lower nibble controls which of the outputs are high or low.


Copyright (C) CSIRO 2025
"""
import numpy as np
import os
import sys
import logging
import time
from pyftdi.gpio import GpioController, GpioException, Ftdi

log = logging.getLogger(__name__)

__author__ = "Keith Bannister <keith.bannister@csiro.au>"

port_map = ['Bottom Right','Bottom Left','Top Left','Top Right']

def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description='Script description', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Be verbose')
    parser.add_argument('-l', '--list', dest='list', action='store_true', help='List available FTDI devices')
    parser.add_argument(dest='position', type=int, choices=[0,1,2,3], nargs='?', help='Position to set the mux to')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

      
    if args.list:
        devices = Ftdi.list_devices()
        print(devices)
        return

    port = args.position
    assert 0 <= port <= 3, "Mux position must be 0, 1, 2, or 3 was {port}"

    value = 0xc0;
    value |= (port&0x3)<<2;   

    try:
        # Joseph uses CBUS bitbang to set the mux
        # 
        # setbitmode(0xf0, 0x20) # enables the mode.
        # then
        # setbitmode(value, 0x20)
        # ftStatus = FT_SetBitMode(ftHandleB,0xf0,0x20);  #0xc0 - c3,c2 outputs; c1,c0 inputs, 0x20 - CBUS BitBang
        #       value = 0xc0;
        #      value |= (Port&0x3)<<2;
        #      ftStatus = FT_SetBitMode(ftHandleB,value,0x20);
        ftdi = Ftdi()
        ftdi.open_from_url('ftdi://::JTAG_Sel/1') # open with serial number="JTAG_Sel"
        assert ftdi.has_cbus
        #eeprom = FtdiEeprom()
        #eeprom.connect(ftdi)
        #print('cbus mask', hex(eeprom.cbus_mask))
        ftdi.set_bitmode(0xf0, Ftdi.BitMode.CBUS) # ftStatus = FT_SetBitMode(ftHandleB,0xf0,0x20); 
        time.sleep(0.05)
        ftdi.set_bitmode(value, Ftdi.BitMode.CBUS) # ftStatus = FT_SetBitMode(ftHandleB,value,0x20);
        time.sleep(0.05)
        print(f"Mux set to position {port}={port_map[port]} with value 0x{value:02x}")
        
    except GpioException as e:
        print("Error communicating with FTDI device:", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
