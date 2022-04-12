#!/usr/bin/python
import asyncio
from kasa import Discover, SmartPlug
from influxdb import InfluxDBClient
from datetime import datetime
import time

# DB Variables
DB_VAR_IP = '127.0.0.1'
DB_VAR_PORT = 8086
DB_VAR_USER = 'root'
DB_VAR_PASS = 'root'
DB_VAR_DB_NAME = 'db0' #'Meyerson_Deployment'

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

devices = asyncio.run(Discover.discover())
for addr, dev in devices.items():
    asyncio.run(dev.update())
    print(f"{addr} >> {dev}")

    
    
async def main():
    while 1:
        p = SmartPlug("10.103.212.255")
        await p.update()
        print(p.alias)
        print(p.hw_info['mac'])
        #if p.is_on:
         #   print("Turning off")
         #   await p.turn_off()
        #else:
         #   print("Turning on")
         #   await p.turn_on()
         int on_off_status= 0;
         
        if(p.is_on):
            on_off_status = 1;
        else:
            on_off_status = 0;
        print(p.emeter_realtime)
            
        try:
            time.sleep(1)
            
            ganacheLogger(float(on_off_status), "ON-OFF STATUS", "0/1", "MAC_Add_Addy_Rpi_1", "ON_OFF", "KASA", "KASA")
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error
    print("Ending session and closing connection... Goodbye!")
    
async def main():
    


if __name__ == "__main__":
    asyncio.run(main())
