from influxdb import InfluxDBClient
from datetime import datetime
from bluepy.btle_mod import *
import pandas as pd
import os

import requests.exceptions
import influxdb.exceptions 

###################################################
################ Global Variables #################
###################################################

counter_max = 5 # Max number of attempts for trying to upload to influx

## Below are arrays to hold data labels for the JSON body for each sensor

measurement_types = [
    "Temperature",
    "Relative Humidity",
    "CO2 Concentration",
    "Visible Light Intensity",
    "Infrared Light Intensity",
    "UV Index",
    "PM 1.0 Concentration",
    "PM 2.5 Concentration",
    "PM 10 Concentration"
]

units = [
    "C",
    "%", 
    "ppm",
    "counts",
    "counts",
    "n/a", 
    "ug/m^3",
    "ug/m^3",
    "ug/m^3"
]

unit_descrips = [
    "Degrees Celsius",
    "Percent Relative Humidity",
    "Parts Per Million", 
    "Unit Specified by Device Manufacturer",
    "Unit Specified by Device Manufacturer",
    "Unitless",
    "Micrograms per Cubic Meter of Air",
    "Micrograms per Cubic Meter of Air",
    "Micrograms per Cubic Meter of Air"
]

sensor_names = [
    "DHT22",
    "DHT22",
    "T6713",
    "SI1145",
    "SI1145",
    "SI1145",
    "PMSA003I",
    "PMSA003I",
    "PMSA003I"
]

manufacturers =[
    "Aosong Electronics Co.",
    "Aosong Electronics Co.",
    "Telaire",
    "Silicon Labs",
    "Silicon Labs",
    "Silicon Labs",
    "Plantower",
    "Plantower",
    "Plantower"
]

MAC_address_extensions = [
    "Temp",
    "RH",
    "CO2", 
    "VLI",
    "IRLI", 
    "UVI",
    "PM1", 
    "PM25",
    "PM10"
]

###################################################
############### Loading Credentials ###############
###################################################

# Loading room specific credentials from a .csv file. These can be edited for each
#   room om the "credentials.csv file"

# Creating the filepath to Access the CSV file 
directory = os.getcwd()
pathname = os.path.abspath(os.path.join(directory, "credentials.csv"))

# Loading the .csv file
credentials = pd.read_csv(pathname)

#parsing the .csv file
aws_ip = str(credentials['value'][0])
local_ip = str(credentials['value'][1])
port = int(credentials['value'][2])
user = str(credentials['value'][3])
auth = str(credentials['value'][4])
RoomNum = str(credentials['value'][5])
AWS_db = str(credentials['value'][6])
local_db = str(credentials['value'][7])
ProjectID = str(credentials['value'][8])
Deployment = str(credentials['value'][9])
TimeZone = str(credentials['value'][10])
Address = str(credentials['value'][11])
BldID = str(credentials['value'][12])
BldName = str(credentials['value'][13])
Metric_Base_MAC_Address = str(credentials['value'][14])
Energy_Base_MAC_Address = str(credentials['value'][15])
room_sqft = int(credentials['value'][16])
service_uuid = str(credentials['value'][17])
api_address = str(credentials['value'][18])
power_option = int(credentials['value'][19])

################################################
############## Send Data to Influx #############
################################################

# Returns a client connected to an Influx instance and creates a DB if one of that name doesn't exist
def createDatabase(ip, port, user, auth, db):
    client = InfluxDBClient(ip, 8086, user, auth, db)
    client.create_database('Meyerson_Deployment')
    return client
    
client_AWS = createDatabase(aws_ip, port, user, auth, AWS_db)           # For Influx on AWS server
client_local = createDatabase(local_ip, port, user, auth, local_db)     # For Influx on Raspberry Pi

# Handles sending the data to influx
def report_reading(reading, reading_name, timestep, UnitDescription, UnitSymbol, SensorName, SensorManufacturer, base_MAC_address, MAC_address_extension):
    global client_AWS, client_local 

    time_report = round_datetime(timestep)

    MAC_Address = base_MAC_address + "_" + MAC_address_extension # Adds a necessary extension for sensor data diambiguation

    json_body = construct_json_body(time_report, reading, reading_name, MAC_Address, UnitDescription, UnitSymbol, SensorName, SensorManufacturer)

    print (reading_name + ': ' + str(reading))              # Printing Data for Debug

    write_data(client_local, json_body)
    write_data(client_AWS, json_body)

# Constructs the JSON body text to send to Influx
def construct_json_body(timestep, data, Measurement, MAC_Address, UnitDescription, UnitSymbol, SensorName, SensorManufacturer):
    global ProjectID, RoomNum, Deployment, TimeZone, Address, BldID, BldName

    print_val = float(data)                     # Converting data to float type, which the BlockChain expects
    json_body = []
    # json_body.append(
    #     {
    #         "measurement": Measurement,         # CO2, Temp, etc 
    #         "tags": {
    #             "ProjectID": ProjectID,            # CharacterString, project identifier, eg. “BlockPenn”
    #             "ProjectDeployment": Deployment,        # CharacterString, phase of the project
    #             "UnitDescription": UnitDescription,        # CharacterString, e.g. "degree Celsius"
    #             "UnitSymbol": UnitSymbol,        # CharacterString, e.g. "°C"
    #             "MACAddress": MAC_Address,            # CharacterString
    #             "TimeZone": TimeZone,            # CharacterString
    #             "Address": Address,                 # CharacterString
    #             "BuildingID": BldID,                   # CharacterString
    #             "BuildingName": BldName,               # CharacterString
    #             "RoomNumber": RoomNum,       # CharacterString
    #             "SensorName": SensorName,               # CharacterString, eg. DHT22
    #             "SensorManufacturer": SensorManufacturer        # CharacterString, company name
    #         },
    #         "LocalTime": timestep,              # TM_Instant (ISO 8601 Time string) '%Y-%m-%dT%H:%M:%SZ' 
    #         "fields": {
    #             "value": print_val           # Any
    #         }
    #     }
    # )

    return json_body

# writes data to Influx 
def write_data(client_type, json_body):
    global counter_max
    flag_1 = 0                  # Flag for checking if writing to Influx was successful: 0 if fail, 1 if success
    counter = 0                 # counter for number of attempts. Max number specified in Global Variables
    while flag_1 == 0: 
        flag_1 = 1
        try:
            client_type.write_points(json_body)
        except influxdb.exceptions.InfluxDBServerError: 
            print("Influx Error, attempt number: " + str(counter + 1))
            flag_1 = 0
            counter = counter + 1
        except requests.exceptions.ConnectionError: 
            print("cannot reach AWS Server - WiFi Lapse")
            flag_1 = 0
            counter = counter + 1


        if counter > counter_max:            
            flag_1 = 1
            print("Could Not Connect To Influx")

# Rounds the datetime to the nearest minute
def round_datetime(base_datetime):
    microseconds = base_datetime.microsecond
    seconds = base_datetime.second
    seconds = seconds + microseconds / 1000000

    modifier = round(seconds/60)

    result = datetime.datetime(
        year = base_datetime.year,
        month = base_datetime.month, 
        day = base_datetime.day,
        hour = base_datetime.hour, 
        minute = (base_datetime.minute + modifier)
        )

    return result 

################################################
############## Handling Bluetooth ##############
################################################

# Bluetooth Parameters
SCAN_AD_TYPE = 0
SCAN_AD_VALUE = 2
COMPLETE_16B_SERVICES = 3
SCAN_TIMEOUT = 10.0
RECOGNIZED_SERVICE_UUIDS = [service_uuid]

# Lists for Devices and services that will connect
connectedDevices = {}
cHandleNames = {}

# Scanner Object to Handle Bluetooth Functions
class ScanDelegate(DefaultDelegate):
    # Initialization
    def __init__(self):
        DefaultDelegate.__init__(self)

    # Script to descover new bluetooth devices
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if((isNewDev | isNewData) & dev.connectable):
            print("Discovered device", dev.addr)
            scanData = dev.getScanData()
            for i in scanData:
                if (i[SCAN_AD_TYPE] == COMPLETE_16B_SERVICES):
                    for j in RECOGNIZED_SERVICE_UUIDS:
                        if j in i[SCAN_AD_VALUE]:
                            print("Looks like one of our devices; saving address...")
                            connectedDevices[dev.addr] = Peripheral()

    # function to handle notifications from bluetooth devices 
    def handleNotification(self, cHandle, data, addr):
        global measurement_types, unit_descrips, units, sensor_names, manufacturers, MAC_address_extensions
        temp_item = str(cHandleNames[addr, cHandle]).split()

        # Parsing which of the data streams is used
        if(temp_item[1] == "Temperature"):
            temp_index = 0
        elif(temp_item[1] == "Humidity"):
            temp_index = 1
        elif(temp_item[1] == "mass"):
            temp_index = 2
        elif(temp_item[1] == "2b03"):
            temp_index = 3
        elif(temp_item[1] == "2c20"):
            temp_index = 4
        elif(temp_item[1] == "UV"):
            temp_index = 5
        elif(temp_item[1] == "Cycling"):
            temp_index = 6
        elif(temp_item[1] == "Location"):
            temp_index = 7
        elif(temp_item[1] == "Environmental"):
            temp_index = 8

        # Recieved Data Value
        reading = int.from_bytes(data, "little", signed = True)

        # Assigning Data Labels
        reading_name = measurement_types[temp_index]
        UnitDescription = unit_descrips[temp_index]
        UnitSymbol = units[temp_index]
        SensorName = sensor_names[temp_index]
        SensorManufacturer = manufacturers[temp_index]

        # MAC Address Details
        MAC_address_extension = MAC_address_extensions[temp_index]
        base_MAC_address = str(addr)

        # Assigning current time for reporting
        timestep = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        report_reading(reading, reading_name, timestep, UnitDescription, UnitSymbol, SensorName, SensorManufacturer, base_MAC_address, MAC_address_extension)

# creating Bluetooth Objects
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(SCAN_TIMEOUT)

# Function to connect known devices
def scanAndConnect():
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(SCAN_TIMEOUT)   

    for i in connectedDevices.keys():
        try:
            print("Attempting to connect to device with addr %s..." % i)
            connectedDevices[i].connect(i, addrType = "random")
            connectedDevices[i].setDelegate(ScanDelegate()) # Not sure if necessary
            for j in connectedDevices[i].getServices():
                for k in j.getCharacteristics():
                    connectedDevices[i].writeCharacteristic(k.valHandle + 1,  b"\x01\x00")
                    cHandleNames[i, k.valHandle] = "%s %s" % (i, k.uuid.getCommonName())
            print("Successfully connected")
        except BTLEDisconnectError:
            print("Connection failed.")  

# Function to disconnect all devices (for refreshing connections)
def disconnectAllDevices():
    for i in connectedDevices.keys():
        connectedDevices[i].disconnect()

################################################
################ Main Function #################
################################################

def main():
    scanAndConnect()    
    while 1:
        for i in connectedDevices.values():
            try:
                if i.waitForNotifications(8.0):
                    continue
            except AttributeError: 
                disconnectAllDevices()
                scanAndConnect()
            except BTLEDisconnectError:
                disconnectAllDevices()
                scanAndConnect()
            except ConnectionError:
                disconnectAllDevices()
                scanAndConnect()
#           if i.waitForNotifications(8.0):
#               continue

    
    print("Ending session and closing connection... Goodbye!\n")
    

if __name__ == "__main__":
    main() 