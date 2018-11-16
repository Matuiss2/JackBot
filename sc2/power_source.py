"""Useful for protoss"""
from .position import Point2


class PowerSource:
    """Returns the powered areas from pylons, prisms and nexus"""
    @classmethod
    def from_proto(cls, proto):
        """Gets data from the protocol"""
        return cls(Point2.from_proto(proto.pos), proto.radius, proto.tag)

    def __init__(self, position, radius, unit_tag):
        assert isinstance(position, Point2)
        assert radius
        self.position = position
        self.radius = radius
        self.unit_tag = unit_tag

    def covers(self, position):
        """Returns the powered area covered"""
        return self.position.distance_to(position) <= self.radius

    def __repr__(self):
        return f"PowerSource({self.position}, {self.radius})"


class PsionicMatrix:
    """Returns the units that are a power source"""
    @classmethod
    def from_proto(cls, proto):
        """Gets data from the protocol"""
        return cls([PowerSource.from_proto(p) for p in proto])

    def __init__(self, sources):
        self.sources = sources

    def covers(self, position):
        """Returns the powered area covered from all sources that exists"""
        return any(source.covers(position) for source in self.sources)
