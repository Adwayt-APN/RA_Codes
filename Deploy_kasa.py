#!/usr/bin/python
import asyncio
from kasa import Discover, SmartPlug
from influxdb import InfluxDBClient
from datetime import datetime
import time
import requests, secrets, json

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

api_url = "https://wap.tplinkcloud.com"
username = "blah"
password = "YouAreAWizardHarry"

def create_random_uuid():
    uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    uuid = list(uuid)

    uuid_sec = secrets.token_hex(36)

    for uuid_index,uuid_char in enumerate(uuid):
        r = uuid_sec[uuid_index]
        d = int(r,16) & 0x3 | 0x8
    #    (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16)
        if (uuid_char == "x"):
            uuid[uuid_index] = r
        elif (uuid_char == "y"):
            uuid[uuid_index] = format(d,'01x')

    uuid = "".join(uuid)
    return uuid

def get_auth_token(uuid, username, password):
    auth_obj = {
        "method": "login", 
        "params": {
            "appType": "Kasa_Mac",
            "cloudUserName": username,
            "cloudPassword": password,
            "terminalUUID": uuid,
        }
    }

    response = requests.post(api_url+"/", json=auth_obj)
#    if (response.status_code == 200): print("Auth success!")
    kasa_token = response.json()["result"]["token"]
    return response.status_code, kasa_token

def get_dev_list(token):
    dev_obj = {"method": "getDeviceList"}
    response = requests.post(api_url+"?token="+token, json=dev_obj)
    return response.status_code, response.json()["error_code"], response.json()["result"]["deviceList"]

def set_dev_state(token, sel_device_id, sel_device_state):
    set_obj = {
        "method": "passthrough", "params": {
            "deviceId": sel_device_id,
            "requestData": "{\"system\":{\"set_relay_state\":{\"state\":" + str(sel_device_state) + "}}}"
        }
    }
    response = requests.post(api_url+"?token="+token, json=set_obj)
    return response.status_code, response.json()["error_code"]

def set_dev_state_emeter(token, sel_device_id):
    set_obj = {
        "method": "passthrough", "params": {
            "deviceId": sel_device_id,
            "requestData": "{\"system\":{\"get_sysinfo\":null},\"emeter\":{\"get_realtime\":null}}"
        }
    }
    response = requests.post(api_url+"?token="+token, json=set_obj)
    return response.status_code, response.json()["error_code"], response.json()

# Authenticate and get token
uuid = create_random_uuid()
print("uuid:",uuid)

[response_code, kasa_token] = get_auth_token(uuid, username, password)
if (response_code == 200): print("Auth success!")
print("kasa_token", kasa_token)
kasa_token = set the token here if you already have one
# Get device list
[response_code, err_code, dev_list] = get_dev_list(kasa_token)
if (response_code == 200): print("List success!")
if (err_code == 0): print("List has no errors")
print("Identified # of devices:",len(dev_list))

# Select device and turn it off
sel_device = dev_list[0]
print("sel_device", sel_device["deviceId"])
sel_device_id = sel_device["deviceId"]
sel_device_state = 1
[response_code, err_code] = set_dev_state(kasa_token, sel_device_id, sel_device_state)
if (response_code == 200): print("Set success!")
if (err_code == 0): print("Set has no errors")

[response_code, err_code, json_resp] = set_dev_state_emeter(kasa_token, sel_device_id)
if (response_code == 200): print("Set success!")
if (err_code == 0): print("Set has no errors")

    
while True:
    dev_ma = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['current_ma']
    dev_mv = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['voltage_mv']
    dev_mw = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['power_mw']
    dev_wh = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['total_wh']
    dev_e_err = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['err_code']

    print(str("dev_ma: %0.2f A" % (dev_ma/1000)))
    print(str("dev_mv: %0.2f V" % (dev_mv/1000)))
    print(str("dev_mw: %0.2f W" % (dev_mw/1000)))
    print(str("dev_wh: %0.2f W/H" % (dev_wh/1000)))

    ganacheLogger(float(dev_ma/1000), "Current Reading", "A", "MAC_DETKIN", "MAC_DETKIN", "MAC_DETKIN", "KASA")
    ganacheLogger(float(dev_mv/1000), "Voltage Reading", "V", "MAC_DETKIN", "MAC_DETKIN", "MAC_DETKIN", "KASA")
    ganacheLogger(float(dev_mw/1000), "Power Reading", "W", "MAC_DETKIN", "MAC_DETKIN", "MAC_DETKIN", "KASA")
    ganacheLogger(float(dev_wh/1000), "Energy Reading", "W/H", "MAC_DETKIN", "MAC_DETKIN", "MAC_DETKIN", "KASA")
    time.sleep(1)
