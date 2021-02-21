from .base import *

class Sensor(yaml.YAMLObject, Producer, metaclass=ProducerMeta):
    """ Sensor

    A simple 
    """
    yaml_tag = u'!Sensor'
    known_types = {
        'int': int,
        'float': float,
        'str': str,
    }

    def __init__(self, address:str, data_uuid:str, data_length:int, value_definitions:dict):
        self.address = address
        self.data_uuid = data_uuid
        self.data_length = data_length
        self.value_definitions = value_definitions

    def data_callback(self, sender: int, data: bytearray):
        if len(data) == self.data_length:
            sensor_data = []
            for d in self.value_definitions:
                try:
                    value = Sensor.known_types[d['dtype']](d['scale'] * int.from_bytes(data[d['from']:d['to']], byteorder=d['byteorder']))
                    sensor_data.append(SensorData(name=d['name'], tag=d['tag'], value=value))
                except Exception:
                    # Skip this value if an exception occured
                    pass
            self.publish(sensor_data)

    def publish(self, sensor_data: list):
        if hasattr(self, 'publishers'):
            for publisher in self.publishers:
                publisher.publish(sensor_data)
