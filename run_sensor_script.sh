#!/bin/bash
# Wait for influxdb to start
echo "Sensor script started"
until pids=$(pidof influxd)
do   
    sleep 5
done
echo "Influx is running, starting sensors python script"
cd /home/ubuntu/RA_Codes         
while true
do
    sudo python3 lior.py
    echo "Restarting code..."
done
