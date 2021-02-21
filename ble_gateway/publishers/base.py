import yaml
from abc import ABC, abstractmethod

class Publisher(ABC):
    """ Publisher Base Class

    Every Publisher has to implement at least an `activate` as well as a `publish` method.
    """
    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def publish(self, data: list):
        pass


class PublisherMeta(type(yaml.YAMLObject), type(Publisher)):
    """ Publisher Metaclass

    The Publisher implementations require this metaclass for their multiple inheritance.
    """
    pass
