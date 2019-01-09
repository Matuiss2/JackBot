"""Groups some info about the map so it can be used in an easy way"""
from collections import deque
from typing import List, Set
from .pixel_map import PixelMap
from .player import Player
from .position import Point2, Rect, Size


class Ramp:
    """Groups everything related to ramps and all the things to do near it"""

    def __init__(self, points: Set[Point2], game_info: "GameInfo"):
        self._points: Set[Point2] = points
        self.__game_info = game_info
        self.x_offset = 0.5
        self.y_offset = -0.5

    @property
    def _height_map(self):
        """Returns the height map"""
        return self.__game_info.terrain_height

    @property
    def _placement_grid(self):
        """Returns the position of the ramp"""
        return self.__game_info.placement_grid

    @property
    def size(self) -> int:
        """Returns the area of the ramp"""
        return len(self._points)

    def height_at(self, po2: Point2) -> int:
        """Returns the height of the ramp"""
        return self._height_map[po2]

    @property
    def points(self) -> Set[Point2]:
        """Not sure what this do"""
        return self._points.copy()

    @property
    def upper(self) -> Set[Point2]:
        """ Returns the upper points of a ramp. """
        max_height = max([self.height_at(p) for p in self._points])
        return {p for p in self._points if self.height_at(p) == max_height}

    @property
    def upper2_for_ramp_wall(self) -> Set[Point2]:
        """ Returns the 2 upper ramp points of the main base ramp required for the supply depot
         and barracks placement properties used in this file. """
        if len(self.upper) > 5:
            return set()
        upper2 = sorted(list(self.upper), key=lambda x: x.distance_to(self.bottom_center), reverse=True)
        while len(upper2) > 2:
            upper2.pop()
        return set(upper2)

    @property
    def top_center(self) -> Point2:
        """Returns the center point right at the top of the ramp"""
        return Point2(
            (sum([p.x for p in self.upper]) / len(self.upper), sum([p.y for p in self.upper]) / len(self.upper))
        )

    @property
    def lower(self) -> Set[Point2]:
        """ Returns the lower points of a ramp. """
        min_height = min([self.height_at(p) for p in self._points])
        return {p for p in self._points if self.height_at(p) == min_height}

    @property
    def bottom_center(self) -> Point2:
        """Returns the center point right at the bottom of the ramp"""
        return Point2(
            (sum([p.x for p in self.lower]) / len(self.lower), sum([p.y for p in self.lower]) / len(self.lower))
        )

    @property
    def barracks_in_middle(self) -> Point2:
        """ Barracks position in the middle of the 2 depots """
        if len(self.upper2_for_ramp_wall) == 2:
            points = self.upper2_for_ramp_wall
            point1 = points.pop().offset((self.x_offset, self.y_offset))
            point2 = points.pop().offset((self.x_offset, self.y_offset))
            intersects = point1.circle_intersection(point2, 2.24)
            any_lower_point = next(iter(self.lower))
            return max(intersects, key=lambda p: p.distance_to(any_lower_point))
        raise Exception("Not implemented. Trying to access a ramp that has a wrong amount of upper points.")

    @property
    def depot_in_middle(self) -> Point2:
        """ Depot in the middle of the 3 depots """
        if len(self.upper2_for_ramp_wall) == 2:
            points = self.upper2_for_ramp_wall
            point1 = points.pop().offset((self.x_offset, self.y_offset))
            point2 = points.pop().offset((self.x_offset, self.y_offset))
            intersects = point1.circle_intersection(point2, 1.58)
            any_lower_point = next(iter(self.lower))
            return max(intersects, key=lambda p: p.distance_to(any_lower_point))
        raise Exception("Not implemented. Trying to access a ramp that has a wrong amount of upper points.")

    @property
    def corner_depots(self) -> Set[Point2]:
        """ Finds the 2 depot positions on the outside """
        if len(self.upper2_for_ramp_wall) == 2:
            points = self.upper2_for_ramp_wall
            point1 = points.pop().offset((self.x_offset, self.y_offset))
            point2 = points.pop().offset((self.x_offset, self.y_offset))
            center = point1.towards(point2, point1.distance_to(point2) / 2)
            depot_position = self.depot_in_middle
            intersects = center.circle_intersection(depot_position, 2.24)
            return intersects
        raise Exception("Not implemented. Trying to access a ramp that has a wrong amount of upper points.")

    @property
    def barracks_can_fit_addon(self) -> bool:
        """ Test if a barracks can fit an addon at natural ramp """
        # https://i.imgur.com/4b2cXHZ.png
        if len(self.upper2_for_ramp_wall) == 2:
            return self.barracks_in_middle.x + 1 > max(self.corner_depots, key=lambda depot: depot.x).x
        raise Exception("Not implemented. Trying to access a ramp that has a wrong amount of upper points.")

    @property
    def barracks_correct_placement(self) -> Point2:
        """ Corrected placement so that an addon can fit """
        if len(self.upper2_for_ramp_wall) == 2:
            if self.barracks_can_fit_addon:
                return self.barracks_in_middle
            return self.barracks_in_middle.offset((-2, 0))
        raise Exception("Not implemented. Trying to access a ramp that has a wrong amount of upper points.")


class GameInfo:
    """It groups some info about the map and units, like ramps, map center and paint groups"""

    def __init__(self, proto):
        self.proto = proto
        self.players: List[Player] = [Player.from_proto(p) for p in proto.player_info]
        self.map_size: Size = Size.from_proto(proto.start_raw.map_size)
        self.pathing_grid: PixelMap = PixelMap(proto.start_raw.pathing_grid)
        self.terrain_height: PixelMap = PixelMap(proto.start_raw.terrain_height)
        self.placement_grid: PixelMap = PixelMap(proto.start_raw.placement_grid)
        self.playable_area = Rect.from_proto(proto.start_raw.playable_area)
        self.map_ramps: List[Ramp] = None
        self.player_races = {p.player_id: p.race_actual or p.race_requested for p in proto.player_info}
        self.start_locations: List[Point2] = [Point2.from_proto(sl) for sl in proto.start_raw.start_locations]
        self.player_start_location: Point2 = None

    @property
    def map_center(self) -> Point2:
        """Returns the map_center position as point2"""
        return self.playable_area.center

    def find_ramps(self) -> List[Ramp]:
        """Calculate (self.pathing_grid - self.placement_grid) (for sets) and then find ramps by comparing heights."""
        ramp_dict = {
            Point2((x, y)): self.pathing_grid[(x, y)] == 0 and self.placement_grid[(x, y)] == 0
            for x in range(self.pathing_grid.width)
            for y in range(self.pathing_grid.height)
        }
        ramp_points = {p for p in ramp_dict if ramp_dict[p]}  # filter only points part of ramp
        ramp_groups = self._find_groups(ramp_points)
        return [Ramp(group, self) for group in ramp_groups]

    def _find_groups(
        self, points: Set[Point2], minimum_points_per_group: int = 8, max_distance_between_points: int = 2
    ) -> List[Set[Point2]]:
        """ From a set/list of points, this function will try to group points together
         Paint clusters of points in rectangular map using flood fill algorithm. """
        current_color: int = -1
        picture: List[List[int]] = [
            [-2 for _ in range(self.pathing_grid.width)] for _ in range(self.pathing_grid.height)
        ]

        def paint(po2: Point2) -> None:
            picture[po2.y][po2.x] = current_color

        nearby: Set[Point2] = set()
        for deltax in range(-max_distance_between_points, max_distance_between_points + 1):
            for deltay in range(-max_distance_between_points, max_distance_between_points + 1):
                if abs(deltax) + abs(deltay) <= max_distance_between_points:
                    nearby.add(Point2((deltax, deltay)))
        for point in points:
            paint(point)
        remaining: Set[Point2] = set(points)
        queue: [Point2] = deque()
        while remaining:
            current_group: Set[Point2] = set()
            if not queue:
                current_color += 1
                start = remaining.pop()
                paint(start)
                queue.append(start)
                current_group.add(start)
            while queue:
                base: Point2 = queue.popleft()
                for offset in nearby:
                    pointx, pointy = base.x + offset.x, base.y + offset.y
                    if (
                        pointx < 0
                        or pointy < 0
                        or pointx >= self.pathing_grid.width
                        or pointy >= self.pathing_grid.height
                    ):
                        continue
                    if picture[pointy][pointx] != -1:
                        continue
                    point: Point2 = Point2((pointx, pointy))
                    remaining.remove(point)
                    paint(point)
                    queue.append(point)
                    current_group.add(point)
            if len(current_group) >= minimum_points_per_group:
                yield current_group
