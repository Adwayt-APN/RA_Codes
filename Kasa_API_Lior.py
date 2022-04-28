#!/usr/bin/python
import math, struct, array, time, io, fcntl
import logging, os, inspect, logging.handlers
import board
import adafruit_shtc3
import Adafruit_SSD1306
#import sps30
import DBSETUP  # import the db setup

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# for the leds and buttons
import RPi.GPIO as GPIO

import requests, secrets, json

api_url = "https://wap.tplinkcloud.com"

username = "blockpennplug1@gmail.com"
password = "KasaPlug_779901"

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
# kasa_token = set the token here if you already have one
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

dev_ma = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['current_ma']
dev_mv = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['voltage_mv']
dev_mw = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['power_mw']
dev_wh = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['total_wh']
dev_e_err = json.loads(json_resp['result']['responseData'])['emeter']['get_realtime']['err_code']
#print(str("dev_ma: %0.2f A" % (dev_ma/1000)))
#print(str("dev_mv: %0.2f V" % (dev_mv/1000)))
#print(str("dev_mw: %0.2f W" % (dev_mw/1000)))
#print(str("dev_wh: %0.2f W/H" % (dev_wh/1000)))



#  {'error_code': 0, 
#  'result': 
#     {'responseData': 
#         '{"system":
#             {"get_sysinfo":
#                 {"sw_ver":"1.0.18 Build 210910 Rel.141202","hw_ver":"1.0","model":"KP115(US)","deviceId":"8006623D62F030B75853E090A889843E1EDA9D79","oemId":"9FDE0C9E37EDF4495F681216FEFB0CFB","hwId":"3E2B9A976B98DCFC5C83D11C8CEF7510","rssi":-35,"latitude_i":399615,"longitude_i":-751772,"alias":"Lab1","status":"configured","obd_src":"tplink","mic_type":"IOT.SMARTPLUGSWITCH","feature":"TIM:ENE","mac":"10:27:F5:8A:36:C6","updating":0,"led_off":0,"relay_state":1,"on_time":0,"icon_hash":"","dev_name":"Smart Wi-Fi Plug Mini","active_mode":"none","next_action":{"type":-1},"ntc_state":0,"err_code":0}},"emeter":{"get_realtime":{"current_ma":0,"voltage_mv":120338,"power_mw":0,"total_wh":0,"err_code":0}}}'}}
