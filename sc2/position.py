from __future__ import annotations
import itertools
import math
import random
from typing import List, Union, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .unit import Unit
    from .units import Units

EPSILON = 10 ** -8


def _sign(num):
    return math.copysign(1, num)


class Pointlike(tuple):
    @property
    def position(self) -> Pointlike:
        return self

    def distance_to(self, target) -> float:
        """Calculate a single distance from a point or unit to another point or unit

        :param target: """
        point_x, point_y = target.position
        return math.hypot(self[0] - point_x, self[1] - point_y)

    def distance_to_point2(self, po2) -> Union[int, float]:
        """ Same as the function above, but should be a bit faster because of the dropped asserts
        and conversion.

        :param po2: """
        return math.hypot(self[0] - po2[0], self[1] - po2[1])

    def _distance_squared(self, po2: Point2) -> Union[int, float]:
        """ Function used to not take the square root as the distances will stay proportionally the same.
        This is to speed up the sorting process.

        :param p2: """
        return (self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2

    def is_closer_than(self, distance: Union[int, float], po2: Union[Unit, Point2]) -> bool:
        """ Check if another point (or unit) is closer than the given distance.

        :param distance:
        :param po2: """
        po2 = po2.position
        return self.distance_to_point2(po2) < distance

    def is_further_than(self, distance: Union[int, float], po2: Union[Unit, Point2]) -> bool:
        """ Check if another point (or unit) is further than the given distance.

        :param distance:
        :param po2: """
        po2 = po2.position
        return self.distance_to_point2(po2) > distance

    def sort_by_distance(self, pos: Union[Units, Iterable[Point2]]) -> List[Point2]:
        """ This returns the target points sorted as list.
        You should not pass a set or dict since those are not sortable.
        If you want to sort your units towards a point, use 'units.sorted_by_distance_to(point)' instead.

        :param pos: """
        return sorted(pos, key=lambda p: self.distance_to_point2(p.position))

    def closest(self, pos: Union[Units, Iterable[Point2]]):
        """ This function assumes the 2d distance is meant

        :param pos: """
        assert pos, f"ps is empty"
        return min([self.distance_to(dis) for dis in pos])

    def distance_to_closest(self, pos: Union[Units, Iterable[Point2]]) -> Union[int, float]:
        """ This function assumes the 2d distance is meant
        :param pos: """
        if not pos:
            raise AssertionError(f"ps is empty")
        closest_distance = math.inf
        for po2 in pos:
            po2 = po2.position
            distance = self.distance_to(po2)
            if distance <= closest_distance:
                closest_distance = distance
        return closest_distance

    def furthest(self, pos: Union[Units, Iterable[Point2]]):
        """ This function assumes the 2d distance is meant

        :param pos: Units object, or iterable of Unit or Point2 """
        if not pos:
            raise AssertionError(f"ps is empty")
        return max([self.distance_to(dis) for dis in pos])

    def distance_to_furthest(self, pos: Union[Units, Iterable[Point2]]) -> Union[int, float]:
        """ This function assumes the 2d distance is meant

        :param pos: """
        if not pos:
            raise AssertionError(f"ps is empty")
        furthest_distance = -math.inf
        for po2 in pos:
            po2 = po2.position
            distance = self.distance_to(po2)
            if distance >= furthest_distance:
                furthest_distance = distance
        return furthest_distance

    def offset(self, pnt) -> Pointlike:
        """

        :param pnt:
        """
        return self.__class__(a + b for a, b in itertools.zip_longest(self, pnt[: len(self)], fillvalue=0))

    def unit_axes_towards(self, pnt):
        """

        :param p:
        """
        return self.__class__(_sign(b - a) for a, b in itertools.zip_longest(self, pnt[: len(self)], fillvalue=0))

    def towards(self, pnt: Union[Unit, Pointlike], distance: Union[int, float] = 1, limit: bool = False) -> Pointlike:
        """

        :param pnt:
        :param distance:
        :param limit:
        """
        pnt = pnt.position
        # assert self != p, f"self is {self}, p is {p}"
        if self == pnt:
            return self
        # end of test
        dis = self.distance_to(pnt)
        if limit:
            distance = min(dis, distance)
        return self.__class__(
            a + (b - a) / dis * distance for a, b in itertools.zip_longest(self, pnt[: len(self)], fillvalue=0)
        )

    def __eq__(self, other):
        try:
            return all(abs(a - b) <= EPSILON for a, b in itertools.zip_longest(self, other, fillvalue=0))
        except Exception:
            return False

    def __hash__(self):
        return hash(tuple(self))


class Point2(Pointlike):
    @classmethod
    def from_proto(cls, data):
        """
        :param data:
        """
        return cls((data.x, data.y))

    @property
    def rounded(self) -> Point2:
        return Point2((math.floor(self[0]), math.floor(self[1])))

    @property
    def x(self) -> Union[int, float]:
        return self[0]

    @property
    def y(self) -> Union[int, float]:
        return self[1]

    @property
    def to2(self) -> Point2:
        return Point2(self[:2])

    @property
    def to3(self) -> Point3:
        return Point3((*self, 0))

    def offset(self, off):
        return Point2((self[0] + off[0], self[1] + off[1]))

    def random_on_distance(self, distance):
        if isinstance(distance, (tuple, list)):  # interval
            distance = distance[0] + random.SystemRandom().random() * (distance[1] - distance[0])

        if distance <= 0:
            raise AssertionError(f"Distance is not greater than 0")
        angle = random.SystemRandom().random() * 2 * math.pi

        cos, sen = math.cos(angle), math.sin(angle)
        return Point2((self.x + cos * distance, self.y + sen * distance))

    def towards_with_random_angle(
        self,
        pnt: Union[Point2, Point3],
        distance: Union[int, float] = 1,
        max_difference: Union[int, float] = (math.pi / 4),
    ) -> Point2:
        tan_x, tan_y = self.to2.towards(pnt.to2, 1)
        angle = math.atan2(tan_y - self.y, tan_x - self.x)
        angle = (angle - max_difference) + max_difference * 2 * random.SystemRandom().random()
        return Point2((self.x + math.cos(angle) * distance, self.y + math.sin(angle) * distance))

    def circle_intersection(self, po2: Point2, radius: Union[int, float]):
        """ self is point1, p is point2, r is the radius for circles originating in both points
        Used in ramp finding

        :param po2:
        :param radius: """
        if self == po2:
            raise AssertionError(f"self is equal to p")
        distance_between_points = self.distance_to(po2)
        if radius < distance_between_points / 2:
            raise AssertionError()
        # remaining distance from center towards the intersection, using pythagoras
        remaining_distance_from_center = (radius ** 2 - (distance_between_points / 2) ** 2) ** 0.5
        # center of both points
        offset_to_center = Point2(((po2.x - self.x) / 2, (po2.y - self.y) / 2))
        center = self.offset(offset_to_center)

        # stretch offset vector in the ratio of remaining distance from center to intersection
        vector_stretch_factor = remaining_distance_from_center / (distance_between_points / 2)
        vect = offset_to_center
        offset_to_center_stretched = Point2((vect.x * vector_stretch_factor, vect.y * vector_stretch_factor))

        # rotate vector by 90° and -90°
        vector_rotated1 = Point2((offset_to_center_stretched.y, -offset_to_center_stretched.x))
        vector_rotated2 = Point2((-offset_to_center_stretched.y, offset_to_center_stretched.x))
        intersect1 = center.offset(vector_rotated1)
        intersect2 = center.offset(vector_rotated2)
        return {intersect1, intersect2}

    @property
    def neighbors4(self) -> set:
        return {
            Point2((self.x - 1, self.y)),
            Point2((self.x + 1, self.y)),
            Point2((self.x, self.y - 1)),
            Point2((self.x, self.y + 1)),
        }

    @property
    def neighbors8(self) -> set:
        return self.neighbors4 | {
            Point2((self.x - 1, self.y - 1)),
            Point2((self.x - 1, self.y + 1)),
            Point2((self.x + 1, self.y - 1)),
            Point2((self.x + 1, self.y + 1)),
        }

    def negative_offset(self, other: Point2) -> Point2:
        return self.__class__((self.x - other.x, self.y - other.y))

    def __add__(self, other: Point2):
        return self.offset(other)

    def __sub__(self, other: Point2) -> Point2:
        return self.negative_offset(other)

    def __neg__(self) -> Point2:
        return self.__class__(-a for a in self)

    def __abs__(self) -> Union[int, float]:
        return math.hypot(self.x, self.y)

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

    def __mul__(self, other: Union[int, float, Point2]) -> Point2:
        try:
            return self.__class__((self.x * other.x, self.y * other.y))
        except AttributeError:
            return self.__class__((self.x * other, self.y * other))

    def __rmul__(self, other: Union[int, float, Point2]) -> Point2:
        return self.__mul__(other)

    def __truediv__(self, other: Union[int, float, Point2]) -> Point2:
        if isinstance(other, self.__class__):
            return self.__class__((self.x / other.x, self.y / other.y))
        return self.__class__((self.x / other, self.y / other))

    def is_same_as(self, other: Point2, dist=0.001) -> bool:
        return self.distance_to_point2(other) <= dist

    def direction_vector(self, other: Point2) -> Point2:
        """ Converts a vector to a direction that can face vertically, horizontally or diagonal or be zero,
         e.g. (0, 0), (1, -1), (1, 0) """
        return self.__class__((_sign(other.x - self.x), _sign(other.y - self.y)))

    def manhattan_distance(self, other: Point2) -> Union[int, float]:
        """
        :param other:
        """
        return abs(other.x - self.x) + abs(other.y - self.y)

    @staticmethod
    def center(units_or_points: Iterable[Point2]) -> Point2:
        """ Returns the central point for points in list

        :param units_or_points:"""
        start_point = Point2((0, 0))
        for pnt in units_or_points:
            start_point += pnt
        return start_point / len(units_or_points)


class Point3(Point2):
    @classmethod
    def from_proto(cls, data):
        """
        :param data:
        """
        return cls((data.x, data.y, data.z))

    @property
    def rounded(self) -> Point3:
        return Point3((math.floor(self[0]), math.floor(self[1]), math.floor(self[2])))

    @property
    def z(self) -> Union[int, float]:
        return self[2]

    @property
    def to3(self) -> Point3:
        return Point3(self)

    def __add__(self, other: Union[Point2, Point3]) -> Point3:
        if not isinstance(other, Point3) and isinstance(other, Point2):
            return Point3((self.x + other.x, self.y + other.y, self.z))
        return Point3((self.x + other.x, self.y + other.y, self.z + other.z))


class Size(Point2):
    @property
    def width(self) -> Union[int, float]:
        return self[0]

    @property
    def height(self) -> Union[int, float]:
        return self[1]


class Rect(tuple):
    @classmethod
    def from_proto(cls, data):
        """
        :param data:
        """
        if not (data.p0.x < data.p1.x and data.p0.y < data.p1.y):
            raise AssertionError()
        return cls((data.p0.x, data.p0.y, data.p1.x - data.p0.x, data.p1.y - data.p0.y))

    @property
    def x(self) -> Union[int, float]:
        return self[0]

    @property
    def y(self) -> Union[int, float]:
        return self[1]

    @property
    def width(self) -> Union[int, float]:
        return self[2]

    @property
    def height(self) -> Union[int, float]:
        return self[3]

    @property
    def size(self) -> Size:
        return Size((self[2], self[3]))

    @property
    def center(self) -> Point2:
        return Point2((self.x + self.width / 2, self.y + self.height / 2))

    def offset(self, pnt):
        return self.__class__((self[0] + pnt[0], self[1] + pnt[1], self[2], self[3]))
