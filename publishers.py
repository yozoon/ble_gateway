from abc import ABC, abstractmethod

from paho.mqtt.client import Client as MQTTClient
from influxdb import InfluxDBClient

class Publisher(ABC):
    @abstractmethod
    def publish(self, data: list):
        pass

class MQTTPublisher(Publisher):
    # Constructor is not actually required for pyyaml object creation
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def activate(self):
        self.mqtt_client = MQTTClient()
        self.mqtt_client.username_pw_set(self.username, self.password)
        self.mqtt_client.connect(self.host)

    def publish(self, data: list):
        for d in data:
            self.mqtt_client.publish(d.name, payload=f'{d.value:.2f}')

class InfluxDBPublisher(Publisher):
    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def activate(self):
        self.influxdb_client = InfluxDBClient(self.host, self.port, self.username, self.password, None)
        databases = self.influxdb_client.get_list_database()
        if len(list(filter(lambda x: x['name'] == self.database, databases))) == 0:
            self.influxdb_client.create_database(self.database)
            self.influxdb_client.create_retention_policy('oneweek', '1w', 1, self.database, default=True)
        self.influxdb_client.switch_database(self.database)

    def publish(self, data: list):
        for d in data:
            self.influxdb_client.write_points([
                {
                    'measurement': d.name,
                    'tags': {
                        'tag': d.tag,
                    },
                    'fields': {
                        'value': d.value
                    }
                }
            ])