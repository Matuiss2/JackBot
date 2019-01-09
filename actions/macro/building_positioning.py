"""Everything related to building positioning goes here"""
from sc2.constants import EVOLUTIONCHAMBER, ENGINEERINGBAY
from sc2.data import ACTION_RESULT
from sc2.position import Point2


class BuildingPositioning:
    """Ok for now"""

    async def prepare_building_positions(self, center):
        """Check all possible positions behind the mineral line when a hatchery is built"""
        mineral_field = self.state.mineral_field
        if mineral_field:
            close_points = range(-11, 12)
            center_position = center.position
            add_positions = self.building_positions.append
            # No point in separating it on variables, I united everything, it gets points that are behind minerals
            viable_points = [
                point
                for point in (
                    Point2((x + center_position.x, y + center_position.y))
                    for x in close_points
                    for y in close_points
                    if 121 >= x * x + y * y >= 81
                )
                if abs(point.distance_to(mineral_field.closer_than(10, center).closest_to(point)) - 3) < 0.5
            ]
            e_bay_ability = self.game_data.units[ENGINEERINGBAY.value].creation_ability
            e_bay_mask = await self.client.query_building_placement(e_bay_ability, viable_points)
            evo_ability = self.game_data.units[EVOLUTIONCHAMBER.value].creation_ability
            evo_mask = await self.client.query_building_placement(evo_ability, viable_points)
            viable_points = [
                point
                for i, point in enumerate(viable_points)
                if e_bay_mask[i] == ACTION_RESULT.Success and evo_mask[i] == ACTION_RESULT.Success
            ]

            for point in viable_points:
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
