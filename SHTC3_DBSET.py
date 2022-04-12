import DBSETUP
import adafruit_shtc3
from datetime import datetime
import math, struct, array, time, io, fcntl

i2c = board.I2C()  # uses board.SCL and board.SDA
sht = adafruit_shtc3.SHTC3(i2c)


bus = 1
addressT6713 = 0x15
I2C_SLAVE=0x0703



class i2c(object):
	def __init__(self, device, bus):

		self.fr = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
		self.fw = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

		# set device address

		fcntl.ioctl(self.fr, I2C_SLAVE, device)
		fcntl.ioctl(self.fw, I2C_SLAVE, device)

	def write(self, bytes):
		self.fw.write(bytes)
		time.sleep(1)

	def read(self, bytes):
		return self.fr.read(bytes)

	def close(self):
		self.fw.close()
		self.fr.close()

class T6713(object):
	def __init__(self):
		self.dev = i2c(addressT6713, bus)

	def status(self):
		buffer = array.array('B', [0x04, 0x13, 0x8a, 0x00, 0x01])
		self.dev.write(buffer)
		time.sleep(1)
		data = self.dev.read(4)
		buffer = array.array('B', data)
		return buffer[2]*256+buffer[3]

	def gasPPM(self):
		buffer = array.array('B', [0x04, 0x13, 0x8b, 0x00, 0x01])
		self.dev.write(buffer)
		time.sleep(0.1)
		data = self.dev.read(4)
		buffer = array.array('B', data)
		return buffer[2]*256+buffer[3]

	def checkABC(self):
		buffer = array.array('B', [0x04, 0x03, 0xee, 0x00, 0x01])
		self.dev.write(buffer)
		time.sleep(0.1)
		data = self.dev.read(4)
		buffer = array.array('B', data)
		return buffer[2]*256+buffer[3]

	def calibrate(self):
		buffer = array.array('B', [0x05, 0x03, 0xec, 0xff, 0x00])
		self.dev.write(buffer)
		time.sleep(0.1)
		data = self.dev.read(5)
		buffer = array.array('B', data)
		return buffer[3]*256+buffer[3]



while True:
  temp, hum = sht.measurements
  obj = T6713()
  print("PPM: ", obj.gasPPM())
  print("C: ", temp)
  print("%: ", hum)
  time.sleep(1)	
  DBSETUP.ganacheLogger(float(hum), "Humidity_Office_1", "%", "MAC_Office_1", "unit_descrip_OFFICE_1", "SHTC3_OFFICE_1", "Sensirion")
  DBSETUP.ganacheLogger(float(temp), "Temperature_Office_1", "C", "MAC_Office_1", "unit_descrip_OFFICE_1", "SHTC3_OFFICE_1", "Sensirion")
  DBSETUP.ganacheLogger(float(obj.gasPPM()), "CO2_Reading_PPM_RPi_1", "PPM_RPi_1", "MAC_Add_Addy_Rpi_1", "co2_t6713_RPi", "T6713_Rpi", "Telaire")
  time.sleep(1)
