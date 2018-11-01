"""Everything related to building positioning goes here"""
from sc2.constants import EVOLUTIONCHAMBER, ENGINEERINGBAY
from sc2.position import Point2


class BuildingPositioning:
    """Ok for now"""

    async def prepare_building_positions(self, start):
        """Check all possible positions behind the mineral line when a hatchery is built"""
        if self.state.mineral_field:
            all_points = [
                Point2((x + start.position.x, y + start.position.y))
                for x in range(-12, 13)
                for y in range(-12, 13)
                if 144 >= x * x + y * y >= 64
            ]
            resources = self.state.mineral_field.closer_than(10, start)
            behind_resources = (point for point in all_points if 2 < point.distance_to(resources.closest_to(point)) < 4)
            for point in behind_resources:
                # also check engineering bay placement for hatcheries that just spawned but have no creep around
                if await self.can_place(ENGINEERINGBAY, point) or await self.can_place(EVOLUTIONCHAMBER, point):
                    if self.building_positions:
                        if all(
                            [
                                abs(already_found.x - point.x) >= 3 or abs(already_found.y - point.y) >= 3
                                for already_found in self.building_positions
                            ]
                        ):
                            self.building_positions.append(point)
                    else:
                        self.building_positions.append(point)

    async def get_production_position(self):
        """Find the safest position looping through all possible ones"""
        if self.building_positions:
            for building_position in self.building_positions:
                if await self.can_place(EVOLUTIONCHAMBER, building_position):
                    return building_position
        else:
            return None
