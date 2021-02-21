#!/usr/bin/env python3

import sys
import logging
import asyncio
from argparse import ArgumentParser

import yaml
from bleak import BleakClient

from .publishers import *
from .producers import *

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

parser = ArgumentParser(description="Gateway service that connects BLE devices with data publishers.")
parser.add_argument("-c", "--config", type=str, dest="config_file", required=True,
                    help="path to the config file")

args = parser.parse_args()

async def device_handler(device):
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


def main():
    with open(args.config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)

    # Configure logging
    logger.setLevel(config['loglevel'])

    # Activate publishers
    logger.info('Activating publishers...')
    active_publishers = []
    for publisher in config['publishers']:
        if publisher['enabled']:
            publisher['instance'].activate()
            active_publishers.append(publisher['instance'])

    # Bind the active publishers to the producers
    logger.info('Registering publishers...')
    producers = []
    for producer in config['producers']:
        if producer['enabled']:
            producer['instance'].register_publishers(active_publishers)
            producers.append(producer['instance'])

    loop = asyncio.get_event_loop()

    logger.info('Starting tasks...')
    for producer in producers:
        loop.create_task(device_handler(producer))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('\nExiting...')
        pass


if __name__ == '__main__':
    main()
