from .base import *

from paho.mqtt.client import Client as MQTTClient

class MQTTPublisher(yaml.YAMLObject, Publisher, metaclass=PublisherMeta):
    """ MQTT Publisher

    Publishing service that sends data to an MQTT broker.
    """
    yaml_tag = u'!MQTTPublisher'
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
            self.mqtt_client.publish(d.name, payload=f'{d.value}')