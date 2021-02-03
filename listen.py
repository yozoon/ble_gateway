#!/usr/bin/env python3

import os
import time
import asyncio

from dotenv import load_dotenv
from bleak import BleakClient
import paho.mqtt.client as mqtt

# Load the environment variables defined in the .env file
load_dotenv()

# Bluetooth client
client = BleakClient(os.getenv('MODULE_HTU_ADDRESS'))

# MQTT client
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(os.getenv('MQTT_USER'), os.getenv('MQTT_PASSWORD'))

def data_callback_htu(sender: int, data: bytearray):
    if len(data) == 4:
        temperature = (1.0 * int.from_bytes(data[0:2], byteorder='little')) / 100
        humidity = (1.0 * int.from_bytes(data[2:4], byteorder='little')) / 100
        mqtt_client.publish('temperature', payload=f'{temperature:.2f}')
        mqtt_client.publish('humidity', payload=f'{humidity:.2f}')

loop = asyncio.get_event_loop()

print('Connecting to device...')
loop.run_until_complete(client.connect())

print('Connecting to MQTT client...')
mqtt_client.connect('localhost')

print('Starting updates...')
loop.run_until_complete(client.start_notify(os.getenv('MODULE_HTU_DATA_UUID'), data_callback_htu))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

print('Stopping updates...')
loop.run_until_complete(client.stop_notify(os.getenv('MODULE_HTU_DATA_UUID')))

print('Disconnecting from device...')
loop.run_until_complete(client.disconnect())

print('Disconnecting MQTT Client...')
mqtt_client.disconnect()

print('Done!')

