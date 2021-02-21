from dataclasses import dataclass

import yaml

@dataclass
class SensorData:
    name: str
    tag: str
    value: float

class Sensor(yaml.YAMLObject):
    yaml_tag = u'!Sensor'
    def register_publishers(self, publishers: list):
        self.publishers = publishers

    def data_callback(self, sender: int, data: bytearray):
        if len(data) == self.data_length:
            sensor_data = []
            for d in self.value_definitions:
                value = d['scale'] * int.from_bytes(data[d['from']:d['to']], byteorder=d['byteorder'])
                sensor_data.append(SensorData(name=d['name'], tag=d['tag'], value=value))
            self.__publish(sensor_data)

    def __publish(self, sensor_data: list):
        if hasattr(self, 'publishers'):
            for publisher in self.publishers:
                publisher.publish(sensor_data)