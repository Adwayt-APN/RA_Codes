import time
import board
import adafruit_shtc3

from smbus2 import SMBus, i2c_msg
import struct
from time import sleep

import sys
import argparse
import lgpio as sbc
#import DHT  # import current module as a class
import DBSETUP  # import the db setup
import datetime
import signal
import atexit

import time
import lgpio as sbc

i2c= board.I2C()
sht= adafruit_shtc3.SHTC3(i2c)


while True:
	print('Temperture Sense: ', sht.temperature)
	print('Humidity Sense: ', sht.relative_humidity)
	time.sleep(1)

	try:
            
		#typical_partical_size = (sps.dict_values['typical'])
  
		DBSETUP.ganacheLogger(float(sht.temperature), "TemPERATURE sense", "Desc.","Desc. DEsc.","MAC_Address_Addy_Nadkarni", "adafruit_shtc3", "adafruit_shtc3")  
		DBSETUP.ganacheLogger(float(sht.relative_humidity), "HumIDITY sense", "Desc","DEsc","MAC_Address_Addy_Nadkarni", "adafruit_shtc3", "adafruit_shtc3")

	except KeyboardInterrupt:
		break
