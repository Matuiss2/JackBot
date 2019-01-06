"""Groups everything related to a position on the map or of an unit"""
import itertools
import random
from math import atan2, cos, hypot, inf, pi, sin
from typing import List, Set, Union

FLOAT_DIGITS = 8
EPSILON = 10 ** (-FLOAT_DIGITS)


def _sign(num):
    """Defines the sign for the multiplication"""
    if not num:
        return 0
    return 1 if num > 0 else -1


class Pointlike(tuple):
    """Define points on the map"""

    @property
    def rounded(self) -> "Pointlike":
        """Round every point given"""
        return self.__class__(round(q) for q in self)

    @property
    def position(self) -> "Pointlike":
        """Return the position on the map of the argument given"""
        return self

    def return_distance(self, position):
        """Helper for distance_to"""
        if self == position:
            return 0
        return (
            sum(self.__class__((b - a) * (b - a) for a, b in itertools.zip_longest(self, position, fillvalue=0))) ** 0.5
        )

    def distance_to(self, unit_or_pos) -> Union[int, float]:
        """Distance from a unit or point to another point"""
        if isinstance(unit_or_pos, Pointlike):
            return self.return_distance(unit_or_pos)
        return self.return_distance(unit_or_pos.position)

    def distance_to_point2(self, po2: "Point2") -> Union[int, float]:
        """ Same as the function above, but should be 3-4 times faster because of the dropped asserts and conversions
         and because it doesnt use a loop (itertools or zip). """
        return ((self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2) ** 0.5

    def distance_squared(self, po2: "Point2") -> Union[int, float]:
        """ Function used to not take the square root as the distances will stay proportionally the same.
        This is to speed up the sorting process. """
        return (self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2

    def sort_by_distance(self, iterator) -> List["Point2"]:
        """ This returns the target points sorted as list.
        You should not pass a set or dict since those are not sortable.
        If you want to sort your units towards a point, use 'units.sorted_by_distance_to(point)' instead. """
        if len(iterator) == 1:
            return iterator[0]
        return sorted(iterator, key=lambda p: self.distance_squared(p.position))

    def closest(self, iterator):
        """ This function assumes the 2d distance is meant """
        assert iterator
        if len(iterator) == 1:
            return iterator[0]
        closest_distance_squared = inf
        for po2 in iterator:
            p2pos = po2
            if not isinstance(p2pos, Point2):
                p2pos = po2.position
            distance = (self[0] - p2pos[0]) ** 2 + (self[1] - p2pos[1]) ** 2
            if distance < closest_distance_squared:
                closest_distance_squared = distance
                closest_element = po2
        return closest_element

    def distance_to_closest(self, iterator) -> Union[int, float]:
        """ This function assumes the 2d distance is meant """
        assert iterator
        closest_distance_squared = inf
        for po2 in iterator:
            if not isinstance(po2, Point2):
                po2 = po2.position
            distance = (self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2
            if distance < closest_distance_squared:
                closest_distance_squared = distance
        return closest_distance_squared ** 0.5

    def furthest(self, iterator):
        """ This function assumes the 2d distance is meant """
        assert iterator
        if len(iterator) == 1:
            return iterator[0]
        furthest_distance_squared = -inf
        for po2 in iterator:
            p2pos = po2
            if not isinstance(p2pos, Point2):
                p2pos = po2.position
            distance = (self[0] - p2pos[0]) ** 2 + (self[1] - p2pos[1]) ** 2
            if furthest_distance_squared < distance:
                furthest_distance_squared = distance
                furthest_element = po2
        return furthest_element

    def distance_to_furthest(self, iterator) -> Union[int, float]:
        """ This function assumes the 2d distance is meant """
        assert iterator
        furthest_distance_squared = -inf
        for po2 in iterator:
            if not isinstance(po2, Point2):
                po2 = po2.position
            distance = (self[0] - po2[0]) ** 2 + (self[1] - po2[1]) ** 2
            if furthest_distance_squared < distance:
                furthest_distance_squared = distance
        return furthest_distance_squared ** 0.5

    def offset(self, point) -> "Pointlike":
        """ Returns the offset of the point"""
        return self.__class__(a + b for a, b in itertools.zip_longest(self, point[: len(self)], fillvalue=0))

    def unit_axes_towards(self, point):
        """Not sure what it does"""
        return self.__class__(_sign(b - a) for a, b in itertools.zip_longest(self, point[: len(self)], fillvalue=0))

    def towards(
        self, point, distance: Union[int, float] = 1, limit: bool = False
    ) -> "Pointlike":
        """Returns a point defined by the second parameter between the argument and the first parameter point"""
        point = point.position
        if self == point:
            return self
        dist = self.distance_to(point)
        if limit:
            distance = min(dist, distance)
        return self.__class__(
            a + (b - a) / dist * distance for a, b in itertools.zip_longest(self, point[: len(self)], fillvalue=0)
        )

    def __eq__(self, other):
        if not isinstance(other, tuple):
            return False
        return all(abs(a - b) < EPSILON for a, b in itertools.zip_longest(self, other, fillvalue=0))

    def __hash__(self):
        return hash(tuple(int(c * FLOAT_DIGITS) for c in self))


class Point2(Pointlike):
    """Everything related to point2 values"""

    @classmethod
    def from_proto(cls, data):
        """Get data from the protocol"""
        return cls((data.x, data.y))

    @property
    def x(self) -> Union[int, float]:
        """Returns the x point"""
        return self[0]

    @property
    def y(self) -> Union[int, float]:
        """Returns the y point"""
        return self[1]

    @property
    def to2(self) -> "Point2":
        """Converts a value to Point2"""
        return Point2(self[:2])

    @property
    def to3(self) -> "Point3":
        """Converts a value to Point3"""
        return Point3((*self, 0))

    def distance2_to(self, other: "Point2"):
        """Squared distance to a point."""
        assert isinstance(other, Point2)
        return (self[0] - other[0]) ** 2 + (self[1] - other[1]) ** 2

    def random_on_distance(self, distance):
        """Return a random Point2 value within the value given"""
        if isinstance(distance, (tuple, list)):
            distance = distance[0] + random.random() * (distance[1] - distance[0])

        assert distance
        angle = random.random() * 2 * pi

        deltax, deltay = cos(angle), sin(angle)
        return Point2((self.x + deltax * distance, self.y + deltay * distance))

    def towards_with_random_angle(
        self,
        point: Union["Point2", "Point3"],
        distance: Union[int, float] = 1,
        max_difference: Union[int, float] = (pi / 4),
    ) -> "Point2":
        """Is equal to towards but instead of a point in a straight line between 2 positions its more flexible"""
        tangx, tangy = self.to2.towards(point.to2, 1)
        angle = atan2(tangy - self.y, tangx - self.x)
        angle = (angle - max_difference) + max_difference * 2 * random.random()
        return Point2((self.x + cos(angle) * distance, self.y + sin(angle) * distance))

    def circle_intersection(self, po2: "Point2", radius: Union[int, float]) -> Set["Point2"]:
        """ self is point1, p is point2, r is the radius for circles originating in both points
        Used in ramp finding """
        assert self != po2
        distance_between_points = self.distance_to(po2)
        assert radius > distance_between_points / 2
        remaining_distance_from_center = (radius ** 2 - (distance_between_points / 2) ** 2) ** 0.5
        offset_to_center = Point2(((po2.x - self.x) / 2, (po2.y - self.y) / 2))
        center = self.offset(offset_to_center)
        vector_stretch_factor = remaining_distance_from_center / (distance_between_points / 2)
        vect = offset_to_center
        offset_to_center_stretched = Point2((vect.x * vector_stretch_factor, vect.y * vector_stretch_factor))
        vector_rotated1 = Point2((offset_to_center_stretched.y, -offset_to_center_stretched.x))
        vector_rotated2 = Point2((-offset_to_center_stretched.y, offset_to_center_stretched.x))
        intersect1 = center.offset(vector_rotated1)
        intersect2 = center.offset(vector_rotated2)
        return {intersect1, intersect2}

    @property
    def neighbors4(self) -> set:
        """All close points to the argument given, on the 4 main directions"""
        return {
            Point2((self.x - 1, self.y)),
            Point2((self.x + 1, self.y)),
            Point2((self.x, self.y - 1)),
            Point2((self.x, self.y + 1)),
        }

    @property
    def neighbors8(self) -> set:
        """All close points to the argument given, on the 8 main directions"""
        return self.neighbors4 | {
            Point2((self.x - 1, self.y - 1)),
            Point2((self.x - 1, self.y + 1)),
            Point2((self.x + 1, self.y - 1)),
            Point2((self.x + 1, self.y + 1)),
        }

    def negative_offset(self, other: "Point2") -> "Point2":
        """Returns the negative offset of the points given"""
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
        """Check if the distance between the point and argument is the same or lower than the value given"""
        return self.distance_squared(other) <= dist * dist

    def direction_vector(self, other: "Point2") -> "Point2":
        """ Converts a vector to a direction that can face vertically,
         horizontally or diagonal or be zero, e.g. (0, 0), (1, -1), (1, 0) """
        return self.__class__((_sign(other.x - self.x), _sign(other.y - self.y)))

    def manhattan_distance(self, other: "Point2") -> Union[int, float]:
        """Ideal distance between two vectors"""
        return abs(other.x - self.x) + abs(other.y - self.y)

    @staticmethod
    def center(point_list: Union[Set["Point2"], List["Point2"]]) -> "Point2":
        """ Returns the central point for points in list """
        total = Point2((0, 0))
        for point in point_list:
            total += point
        return total / len(point_list)


class Point3(Point2):
    """Get the point3 value or converts a value to point3"""

    @classmethod
    def from_proto(cls, data):
        """Get protocol data"""
        return cls((data.x, data.y, data.z))

    @property
    def z(self) -> Union[int, float]:
        """Get the height of the argument"""
        return self[2]

    @property
    def to3(self) -> "Point3":
        """Converts a value to point3"""
        return Point3(self)


class Size(Point2):
    """Return the width and height of the argument"""

    @property
    def width(self) -> Union[int, float]:
        """Return the width of the argument"""
        return self[0]

    @property
    def height(self) -> Union[int, float]:
        """Return the height of the argument"""
        return self[1]


class Rect(tuple):
    """Create a rectangle object"""

    @classmethod
    def from_proto(cls, data):
        """Get data from the protocol"""
        assert data.p0.x < data.p1.x and data.p0.y < data.p1.y
        return cls((data.p0.x, data.p0.y, data.p1.x - data.p0.x, data.p1.y - data.p0.y))

    @property
    def x(self) -> Union[int, float]:
        """Returns the x point of the rectangle"""
        return self[0]

    @property
    def y(self) -> Union[int, float]:
        """Returns the y point of the rectangle"""
        return self[1]

    @property
    def width(self) -> Union[int, float]:
        """Returns the width of the rectangle"""
        return self[2]

    @property
    def height(self) -> Union[int, float]:
        """Returns the height of the rectangle"""
        return self[3]

    @property
    def size(self) -> Size:
        """Returns the area of the rectangle"""
        return Size(self[2:4])

    @property
    def center(self) -> Point2:
        """Returns the center of the rectangle"""
        return Point2((self.x + self.width / 2, self.y + self.height / 2))

    def offset(self, point):
        """Returns the offset of the rectangle"""
        return self.__class__((self[0] + point[0], self[1] + point[1], self[2], self[3]))
