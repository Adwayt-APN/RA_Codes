import DBSETUP
import adafruit_shtc3
import time

i2c = board.I2C()  # uses board.SCL and board.SDA
sht = adafruit_shtc3.SHTC3(i2c)


while True:
  temperature, relative_humidity = sht.measurements
  print(temp)
  print(hum)
  time.sleep(1)	
  DBSETUP.ganacheLogger(float(relative_humidity), "Humidity_Office_1", "%", "MAC_Office_1", "unit_descrip_OFFICE_1", "SHTC3_OFFICE_1", "Sensirion")
  time.sleep(1)
  DBSETUP.ganacheLogger(float(temperature), "Temperature_Office_1", "C", "MAC_Office_1", "unit_descrip_OFFICE_1", "SHTC3_OFFICE_1", "Sensirion")
