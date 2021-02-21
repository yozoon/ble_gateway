from abc import ABC, abstractmethod
from dataclasses import dataclass

import yaml

@dataclass
class SensorData:
    name: str
    tag: str
    value: float


class Producer(ABC):
    """ Producer Base Class

    Every Producer implementation must contain the `register_publishers` method and the 
    `data_callback` method must be implemented.
    """
    def register_publishers(self, publishers:list):
        self.publishers = publishers

    @abstractmethod
    def data_callback(self, sender: int, data: bytearray):
        pass


class ProducerMeta(type(yaml.YAMLObject), type(Producer)):
    """ Producer Metaclass

    The Producer implementations require this metaclass for their multiple inheritance.
    """
    pass
