from typing import Callable

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

class SensorDevice:
    def __init__(self, address: str, data_uuid: str, data_callback: Callable):
        self.address = address
        self.data_uuid = data_uuid
        self.data_callback = data_callback


def callback_htu(mqtt_client: mqtt.Client, ifdb: InfluxDBClient, sender: int, data: bytearray):
    if len(data) == 4:
        temperature = int.from_bytes(data[0:2], byteorder='little') / 100
        humidity = int.from_bytes(data[2:4], byteorder='little') / 100
        mqtt_client.publish('temperature', payload=f'{temperature:.2f}')
        mqtt_client.publish('humidity', payload=f'{humidity:.2f}')
        json_body = [
            {
                'measurement': 'temperature',
                'fields': {
                    'value': temperature
                }
            },
            {
                'measurement': 'humidity',
                'fields': {
                    'value': humidity
                }
            }
        ]
        ifdb.write_points(json_body)


def callback_airquality(mqtt_client: mqtt.Client, ifdb: InfluxDBClient, sender: int, data: bytearray):
    if len(data) == 4:
        eco2 = int.from_bytes(data[0:2], byteorder='big')
        tvoc = int.from_bytes(data[2:4], byteorder='big')
        mqtt_client.publish('eco2', payload=f'{eco2}')
        mqtt_client.publish('tvoc', payload=f'{tvoc}')
        json_body = [
            {
                'measurement': 'eco2',
                'fields': {
                    'value': eco2
                }
            },
            {
                'measurement': 'tvoc',
                'fields': {
                    'value': tvoc
                }
            }
        ]
        ifdb.write_points(json_body)


sensors = [
    # HTU Sensor
    SensorDevice(
        address="E3:BF:B3:23:85:F3",
        data_uuid="00002016-0000-1000-8000-00805f9b34fb",
        data_callback=callback_htu),
    # Air Quality Sensor
    SensorDevice(
        address="11:22:33:AA:BB:CC",
        data_uuid="00001111-0000-1000-8000-00805f9b34fb",
        data_callback=callback_airquality),
]
