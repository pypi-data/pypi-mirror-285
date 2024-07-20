from abc import ABC, abstractmethod
from enum import Enum

from scapy.layers.inet import TCP, UDP
from scapy.packet import Packet

from netmon_proc.netinfo import MAC_ADDRS
from netmon_proc.utils import human_readable_format


class Metrics(str, Enum):
    transferred = "transferred"
    received = "received"
    transmitted = "transmitted"


class Metric(ABC):

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __add__(self, packet: Packet):
        pass

    @abstractmethod
    def __iadd__(self, packet: Packet):
        pass

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def human_readable_value(self):
        pass

    @abstractmethod
    def add(self, metric: "Metric"):
        pass

    @abstractmethod
    def remove(self, metric: "Metric"):
        pass

    @abstractmethod
    def children(self):
        pass


class NetworkMetric(Metric):
    def __init__(self, name):
        self._name: str = name
        self._value: int = 0
        self._unit: str = ""

    def __str__(self):
        return f"{self._name}: {self._value} {self._unit}"

    @abstractmethod
    def __iadd__(self, packet: Packet):
        pass

    @abstractmethod
    def __add__(self, packet: Packet):
        pass

    def name(self):
        return self._name

    def value(self):
        return self._value

    def human_readable_value(self):
        return self._value

    def add(self, metric: Metric):
        raise NotImplementedError("Leaf nodes can't add components")

    def remove(self, metric: Metric):
        raise NotImplementedError("Leaf nodes can't remove components")

    def children(self):
        raise NotImplementedError("Leaf nodes don't have children")


class RxBytes(NetworkMetric):
    def __init__(self):
        super().__init__("Received")
        self._unit = "bytes"

    def __str__(self):
        return f"{self._name}: {' '.join(human_readable_format(self._value))}"

    def __iadd__(self, packet: Packet):
        for layer in (TCP, UDP):
            if packet.haslayer(layer) and packet.src not in MAC_ADDRS:
                self._value += len(packet[layer].payload)
                break
        return self

    def __add__(self, packet: Packet):
        new_metric = RxBytes()
        for layer in (TCP, UDP):
            if packet.haslayer(layer) and packet.src not in MAC_ADDRS:
                new_metric._value = self._value + len(packet[layer].payload)
                break
        return new_metric

    def human_readable_value(self):
        return "".join(human_readable_format(self._value))


class CompositeMetric(Metric):
    _metrics: list[Metric] = []
    _name: str = ""

    def __init__(self, name):
        self._name = name

    def __iadd__(self, packet: Packet):
        for metric in self._metrics:
            metric += packet
        return self

    def __add__(self, packet: Packet):
        new_composite = CompositeMetric(self._name)
        for metric in self._metrics:
            new_composite.add(metric + packet)
        return new_composite

    def __str__(self):
        result = f"== {self._name} ==\n"
        for metric in self._metrics:
            result += str(metric) + "\n"
        return result.strip()

    def name(self):
        return self._name

    def add(self, metric: Metric):
        self._metrics.append(metric)

    def remove(self, metric: Metric):
        self._metrics.remove(metric)

    def children(self):
        return self._metrics

    def value(self):
        raise NotImplementedError("Leaf nodes can't add components")

    def human_readable_value(self):
        raise NotImplementedError("Leaf nodes can't add components")
