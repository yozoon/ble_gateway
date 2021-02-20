import os
import asyncio
import logging
from functools import partial

from dotenv import load_dotenv
from bleak import BleakClient, discover
import paho.mqtt.client as mqtt

from sensors import SensorDevice, sensors

# Load the environment variables defined in the .env file
load_dotenv()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# MQTT client
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(os.getenv('MQTT_USER'), os.getenv('MQTT_PASSWORD'))
logging.info('Connecting to MQTT client...')
mqtt_client.connect('localhost')

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
    sensor.data_callback = partial(sensor.data_callback, mqtt_client)
    loop.create_task(device_handler(sensor))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass