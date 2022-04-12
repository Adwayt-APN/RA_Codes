from influxdb import InfluxDBClient
from datetime import datetime
import math, struct, array, time, io, fcntl

# DB Variables
DB_VAR_IP = '127.0.0.1'
DB_VAR_PORT = 8086
DB_VAR_USER = 'root'
DB_VAR_PASS = 'root'
DB_VAR_DB_NAME = 'db0' #'Meyerson_Deployment'

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

def createDatabase():
    client = InfluxDBClient(DB_VAR_IP, DB_VAR_PORT, DB_VAR_USER, DB_VAR_PASS, DB_VAR_DB_NAME)
    client.create_database(DB_VAR_DB_NAME)
    return client

client = createDatabase()

def ganacheLogger(data, Measurement, Unit, MAC_Address, unit_descrip, sensor_name, mfg_name):
    global client
    # This is per data Transmission
    json_body = []
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    json_body.append(
        {
            "measurement": Measurement,         # CO2, Temp, etc 
            "tags": {
                "ProjectID": "“BlockPenn”",            # CharacterString, project identifier, eg. “BlockPenn”
                "ProjectDeployment": "Deployment 1",        # CharacterString, phase of the project
                "UnitDescription": unit_descrip,        # CharacterString, e.g. "degree Celsius"
                "UnitSymbol": Unit,        # CharacterString, e.g. "°C"
                "MACAddress": MAC_Address,            # CharacterString
                "TimeZone": "Philadelphia",            # CharacterString
                "Address": "1908 Mt Vernon St",                 # CharacterString
                "BuildingID": "N/A",                   # CharacterString
                "BuildingName": "Max's Apartment",               # CharacterString
                "RoomNumber": "3F",       # CharacterString
                "SensorName": sensor_name,               # CharacterString, eg. DHT22
                "SensorManufacturer": mfg_name        # CharacterString, company name
            },
            "LocalTime": current_time,              # TM_Instant (ISO 8601 Time string) '%Y-%m-%dT%H:%M:%SZ' 
            "fields": {
                "value": data           # Any
            }
        }
    )
    client.write_points(json_body)

def main():
    while 1:
        try:
            time.sleep(1)
            obj = T6713()
            print("CO2 Reading in PPM: ", obj.gasPPM())
            ganacheLogger(float(obj.gasPPM()), "CO2_Reading_PPM_RPi_1", "PPM_RPi_1", "MAC_Add_Addy_Rpi_1", "co2_t6713_RPi", "T6713_Rpi", "Telaire")	
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
    

if __name__ == "__main__":
    main() 
