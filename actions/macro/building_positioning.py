"""Everything related to building positioning goes here"""
from sc2.constants import ENGINEERINGBAY, EVOLUTIONCHAMBER
from sc2.position import Point2


class BuildingPositioning:
    """Ok for now"""

    async def prepare_building_positions(self, center):
        """Check all possible positions behind the mineral line when a hatchery is built"""
        mineral_field = self.state.mineral_field
        if mineral_field:
            close_points = range(-12, 13)
            center_position = center.position
            add_positions = self.building_positions.append
            # No point in separating it on variables, I united everything, it gets points that are behind minerals
            for point in (
                point
                for point in (
                    Point2((x + center_position.x, y + center_position.y))
                    for x in close_points
                    for y in close_points
                    if 144 >= x * x + y * y >= 64
                )
                if point.distance_to(mineral_field.closer_than(10, center).closest_to(point)) == 3
            ):
                # also check engineering bay placement for hatcheries that just spawned but have no creep around
                if await self.can_place(ENGINEERINGBAY, point) or await self.can_place(EVOLUTIONCHAMBER, point):
                    if self.building_positions:
                        if all(
                            abs(already_found.x - point.x) >= 3 or abs(already_found.y - point.y) >= 3
                            for already_found in self.building_positions
                        ):
                            add_positions(point)
                    else:
                        add_positions(point)

    async def get_production_position(self):
        """Find the safest position looping through all possible ones"""
        if self.building_positions:
            for building_position in self.building_positions:
                if await self.can_place(EVOLUTIONCHAMBER, building_position):
                    return building_position
        return None
