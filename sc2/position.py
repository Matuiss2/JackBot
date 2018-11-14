from math import sqrt, pi, sin, cos, atan2, hypot, inf
import random
import itertools
from typing import List, Set, Union  # for mypy type checking

FLOAT_DIGITS = 8
EPSILON = 10 ** (-FLOAT_DIGITS)


def _sign(num):
    if num == 0:
        return 0
    return 1 if num > 0 else -1


class Pointlike(tuple):
    @property
    def rounded(self) -> "Pointlike":
        return self.__class__(round(q) for q in self)

    @property
    def position(self) -> "Pointlike":
        return self

    def distance_to(self, unit_or_pos: Union["Unit", "Point2", "Point3"]) -> Union[int, float]:
        pos = unit_or_pos.position
        assert isinstance(pos, Pointlike)
        if self == pos:
            return 0
        return sqrt(sum(self.__class__((b - a) ** 2 for a, b in itertools.zip_longest(self, pos, fillvalue=0))))

    def distance_to_point2(self, po2: "Point2") -> Union[int, float]:
        """ Same as the function above, but should be 3-4 times faster because of the dropped asserts
         and conversions and because it doesnt use a loop (itertools or zip). """
        return ((self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2) ** 0.5

    def distance_squared(self, po2: "Point2") -> Union[int, float]:
        """ Function used to not take the square root as the distances will stay proportionally the same.
        This is to speed up the sorting process. """
        return (self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2

    def sort_by_distance(self, iterable: Union["Units", List["Point2"]]) -> List["Point2"]:
        """ This returns the target points sorted as list.
        You should not pass a set or dict since those are not sortable.
        If you want to sort your units towards a point, use 'units.sorted_by_distance_to(point)' instead. """
        if iterable and all(isinstance(p, Point2) for p in iterable):
            return sorted(iterable, key=lambda p: self.distance_squared(p))
        return sorted(iterable, key=lambda p: self.distance_to(p))

    def closest(self, iterable: Union["Units", List["Point2"], Set["Point2"]]) -> Union["Unit", "Point2"]:
        """ This function assumes the 2d distance is meant """
        assert iterable
        closest_distance_squared = inf
        for po2 in iterable:
            p2pos = po2
            if not isinstance(p2pos, Point2):
                p2pos = po2.position
            distance = (self[0] - p2pos[0]) ** 2 + (self[1] - p2pos[1]) ** 2
            if distance < closest_distance_squared:
                closest_distance_squared = distance
                closest_element = po2
        return closest_element

    def distance_to_closest(self, iterable: Union["Units", List["Point2"], Set["Point2"]]) -> Union[int, float]:
        """ This function assumes the 2d distance is meant """
        assert iterable
        closest_distance_squared = inf
        for po2 in iterable:
            if not isinstance(po2, Point2):
                po2 = po2.position
            distance = (self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2
            if distance < closest_distance_squared:
                closest_distance_squared = distance
        return closest_distance_squared ** 0.5

    def furthest(self, iterable: Union["Units", List["Point2"], Set["Point2"]]) -> Union["Unit", "Pointlike"]:
        """ This function assumes the 2d distance is meant """
        assert iterable
        furthest_distance_squared = -inf
        for po2 in iterable:
            p2pos = po2
            if not isinstance(p2pos, Point2):
                p2pos = po2.position
            distance = (self[0] - p2pos[0]) ** 2 + (self[1] - p2pos[1]) ** 2
            if furthest_distance_squared < distance:
                furthest_distance_squared = distance
                furthest_element = po2
        return furthest_element

    def distance_to_furthest(self, iterable: Union["Units", List["Point2"], Set["Point2"]]) -> Union[int, float]:
        """ This function assumes the 2d distance is meant """
        assert iterable
        furthest_distance_squared = -inf
        for po2 in iterable:
            if not isinstance(po2, Point2):
                po2 = po2.position
            distance = (self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2
            if furthest_distance_squared < distance:
                furthest_distance_squared = distance
        return furthest_distance_squared ** 0.5

    def offset(self, pos) -> "Pointlike":
        return self.__class__(a + b for a, b in itertools.zip_longest(self, pos[: len(self)], fillvalue=0))

    def unit_axes_towards(self, pos):
        return self.__class__(_sign(b - a) for a, b in itertools.zip_longest(self, pos[: len(self)], fillvalue=0))

    def towards(
        self, pos_or_unit: Union["Unit", "Pointlike"], distance: Union[int, float] = 1, limit: bool = False
    ) -> "Pointlike":
        pos = pos_or_unit.position
        assert self != pos
        dist = self.distance_to(pos)
        if limit:
            distance = min(dist, distance)
        return self.__class__(
            a + (b - a) / dist * distance for a, b in itertools.zip_longest(self, pos[: len(self)], fillvalue=0)
        )

    def __eq__(self, other):
        if not isinstance(other, tuple):
            return False
        return all(abs(a - b) < EPSILON for a, b in itertools.zip_longest(self, other, fillvalue=0))

    def __hash__(self):
        return hash(tuple(int(c * FLOAT_DIGITS) for c in self))


class Point2(Pointlike):
    @classmethod
    def from_proto(cls, data):
        return cls((data.x, data.y))

    @property
    def x(self) -> Union[int, float]:
        return self[0]

    @property
    def y(self) -> Union[int, float]:
        return self[1]

    @property
    def to2(self) -> "Point2":
        return Point2(self[:2])

    @property
    def to3(self) -> "Point3":
        return Point3((*self, 0))

    def distance2_to(self, other: "Point2"):
        """Squared distance to a point."""
        assert isinstance(other, Point2)
        return (self[0] - other[0]) ** 2 + (self[1] - other[1]) ** 2

    def random_on_distance(self, distance):
        if isinstance(distance, (tuple, list)):  # interval
            distance = distance[0] + random.random() * (distance[1] - distance[0])

        assert distance > 0
        angle = random.random() * 2 * pi

        deltax, deltay = cos(angle), sin(angle)
        return Point2((self.x + deltax * distance, self.y + deltay * distance))

    def towards_with_random_angle(
        self,
        pos: Union["Point2", "Point3"],
        distance: Union[int, float] = 1,
        max_difference: Union[int, float] = (pi / 4),
    ) -> "Point2":
        tangx, tangy = self.to2.towards(pos.to2, 1)
        angle = atan2(tangy - self.y, tangx - self.x)
        angle = (angle - max_difference) + max_difference * 2 * random.random()
        return Point2((self.x + cos(angle) * distance, self.y + sin(angle) * distance))

    def circle_intersection(self, po2: "Point2", radius: Union[int, float]) -> Set["Point2"]:
        """ self is point1, p is point2, r is the radius for circles originating in both points
        Used in ramp finding """
        assert self != po2
        distance_between_points = self.distance_to(po2)
        assert radius > distance_between_points / 2
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

    def negative_offset(self, other: "Point2") -> "Point2":
        return self.__class__((self.x - other.x, self.y - other.y))

    def __add__(self, other: "Point2") -> "Point2":
        return self.offset(other)

    def __sub__(self, other: "Point2") -> "Point2":
        return self.negative_offset(other)

    def __neg__(self) -> "Point2":
        return self.__class__(-a for a in self)

    def __abs__(self) -> Union[int, float]:
        return hypot(self.x, self.y)

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

    def __mul__(self, other: Union[int, float, "Point2"]) -> "Point2":
        if isinstance(other, self.__class__):
            return self.__class__((self.x * other.x, self.y * other.y))
        return self.__class__((self.x * other, self.y * other))

    def __rmul__(self, other: Union[int, float, "Point2"]) -> "Point2":
        return self.__mul__(other)

    def __truediv__(self, other: Union[int, float, "Point2"]) -> "Point2":
        if isinstance(other, self.__class__):
            return self.__class__((self.x / other.x, self.y / other.y))
        return self.__class__((self.x / other, self.y / other))

    def is_same_as(self, other: "Point2", dist=0.1) -> bool:
        return self.distance_squared(other) <= dist ** 2

    def direction_vector(self, other: "Point2") -> "Point2":
        """ Converts a vector to a direction that can face vertically, horizontally or diagonal or be zero,
         e.g. (0, 0), (1, -1), (1, 0) """
        return self.__class__((_sign(other.x - self.x), _sign(other.y - self.y)))

    def manhattan_distance(self, other: "Point2") -> Union[int, float]:
        return abs(other.x - self.x) + abs(other.y - self.y)

    @staticmethod
    def center(iterator: Union[Set["Point2"], List["Point2"]]) -> "Point2":
        """ Returns the central point for points in list """
        total = Point2((0, 0))
        for po2 in iterator:
            total += po2
        return total / len(iterator)


class Point3(Point2):
    @classmethod
    def from_proto(cls, data):
        return cls((data.x, data.y, data.z))

    @property
    def z(self) -> Union[int, float]:
        return self[2]

    @property
    def to3(self) -> "Point3":
        return Point3(self)


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
        assert data.p0.x < data.p1.x and data.p0.y < data.p1.y
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
        return Size(self[2], self[3])

    @property
    def center(self) -> Point2:
        return Point2((self.x + self.width / 2, self.y + self.height / 2))

    def offset(self, point):
        return self.__class__((self[0] + point[0], self[1] + point[1], self[2], self[3]))
