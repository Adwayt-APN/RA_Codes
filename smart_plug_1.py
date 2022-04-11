import asyncio
from kasa import SmartPlug

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



async def main():
	
	# DEVICE 1	
	p1 = SmartPlug("10.0.0.141")
	await p1.update()
	#await p1.turn_on()
	print(p1.sys_info)
	print("Power Consumption Device 1: ", p1.emeter_realtime )

	print("")

	# DEVICE 2
	p2 = SmartPlug("10.0.0.177")
	await p2.update()
	#await p2.turn_off()	
	print(p2.sys_info)
	print("Power Consumption Device 2: ", p2.emeter_realtime )

	DBSETUP.ganacheLogger(str(p1.is_on), "Device_1_Status", "Desc.", "Desc. DEsc.", "MAC_Address_Addy_Nadkarni", "Smart_plug 1", "Kasa")
	DBSETUP.ganacheLogger(str(p2.is_on), "Device_2_Status", "Desc.", "Desc. DEsc.", "MAC_Address_Addy_Nadkarni", "Smart_plug 2", "Kasa")

 	
if __name__ == "__main__":
	asyncio.run(main())
