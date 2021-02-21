from .base import *

from influxdb import InfluxDBClient

class InfluxDBPublisher(yaml.YAMLObject, Publisher, metaclass=PublisherMeta):
    """ InfluxDB Publisher

    Publishing service that sends data to an InfluxDB instance.
    """
    yaml_tag = u'!InfluxDBPublisher'
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
