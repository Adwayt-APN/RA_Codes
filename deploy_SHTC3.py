from influxdb import InfluxDBClient
from datetime import datetime
import time
import adafruit_shtc3
import board

# DB Variables
DB_VAR_IP = '127.0.0.1'
DB_VAR_PORT = 8086
DB_VAR_USER = 'root'
DB_VAR_PASS = 'root'
DB_VAR_DB_NAME = 'db0' #'Meyerson_Deployment'


i2c= board.I2C()
sht= adafruit_shtc3.SHTC3(i2c)


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
            temperature = sht.temperature
            humidity = sht.relative_humidity
            print("Temperature: ", temperature, "c Humidity: ", humidity,"%")
            ganacheLogger(float(temperature), "Temperature_RPi_1", "C", "MAC_Add_Addy_Rpi_1", "Temp_shtc3_Rpi_1", "SHTC3_Rpi_1", "SparkFun")	
            ganacheLogger(float(humidity), "Humidity_RPi_1", "%", "MAC_Add_Addy_Rpi_1", "Hum_shtc3_Rpi_1", "SHTC3_RPi_1", "SparkFun")
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
    

if __name__ == "__main__":
    main() 
