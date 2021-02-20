#!/usr/bin/env python3

import asyncio
import logging
import configparser
from functools import partial

from bleak import BleakClient, discover
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

from sensors import SensorDevice, sensors

# Load the configuration file
config = configparser.ConfigParser()
config.read('gateway.ini')

# Configure logging
logger = logging.getLogger()
logger.setLevel(config.getint('common', 'loglevel', fallback=30))

# MQTT client
logging.info('Connecting to MQTT client...')
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(config['MQTT']['username'], config['MQTT']['password'])
mqtt_client.connect(config['MQTT']['host'])

# InfluxDB
influx = config['InfluxDB']
influxdb_client = InfluxDBClient(influx['host'], influx['port'], influx['username'], influx['password'], None)
databases = influxdb_client.get_list_database()
if len(list(filter(lambda x: x['name'] == influx['database'], databases))) == 0:
    influxdb_client.create_database(influx['database'])
    influxdb_client.create_retention_policy('oneweek', '1w', 1, influx['database'], default=True)
influxdb_client.switch_database(influx['database'])


async def device_handler(device: SensorDevice):
    """ Device Handler

    Coroutine which handles the connection to a BLE device, as well as subscribing
    to GATT data notifications. It also automatically restarts itself once the
    connection to the device is lost or when an error occurs during the initialization
    process.
    """
    logger.info(f"Starting device handler for {device.address}")
    disconnected_event = asyncio.Event()

    def disconnected_callback(client):
        logger.warning(f"Client with address {device.address} disconnected.")
        disconnected_event.set()

    # Create the client
    client = BleakClient(device.address, disconnected_callback=disconnected_callback)
    try:
        # Await the client connection
        await client.connect()
        # Start notifications
        await client.start_notify(device.data_uuid, device.data_callback)
        # Wait until the device disconnects
        await disconnected_event.wait()
    except Exception as e:
        logger.warning(e)
    finally:
        await client.disconnect()
    # Wait for one second
    await asyncio.sleep(10)
    # Restart this coroutine
    await device_handler(device)

loop = asyncio.get_event_loop()

for sensor in sensors:
    # Bind the mqtt client to the data callback
    sensor.data_callback = partial(sensor.data_callback, mqtt_client, influxdb_client)
    loop.create_task(device_handler(sensor))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass