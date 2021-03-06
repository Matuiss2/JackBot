"""Everything related to building positioning goes here"""
from sc2.constants import UnitTypeId
from sc2.data import ActionResult
from sc2.position import Point2


class BuildingsPositions:
    """Ok for now"""

    def __init__(self):
        self.building_positions, self.viable_points = [], []

    async def final_triage_for_viable_locations(self):
        """See if its possible to build an evochamber or an engineering bay at the position - checking both is needed
        because it runs at the main base that has creep already(evochamber can be placed) but it also runs on new
        bases as well and on this ones the creep doesn't exist at the position yet(engineering bay can be placed)"""
        e_bay_creation_ability = self._game_data.units[UnitTypeId.ENGINEERINGBAY.value].creation_ability
        e_bay_mask = await self._client.query_building_placement(e_bay_creation_ability, self.viable_points)
        evo_creation_ability = self._game_data.units[UnitTypeId.EVOLUTIONCHAMBER.value].creation_ability
        evo_mask = await self._client.query_building_placement(evo_creation_ability, self.viable_points)
        for point in [
            point
            for i, point in enumerate(self.viable_points)
            if any(result == ActionResult.Success for result in [e_bay_mask[i], evo_mask[i]])
        ]:
            if self.building_positions:
                if all(
                    max(abs(already_found.x - point.x), abs(already_found.y - point.y)) >= 3
                    for already_found in self.building_positions
                ):
                    self.building_positions.append(point)
            else:
                self.building_positions.append(point)

    async def get_production_position(self):
        """Find the safest position looping through all possible ones"""
        for building_position in self.building_positions:
            if await self.can_place(UnitTypeId.EVOLUTIONCHAMBER, building_position):
                return building_position
        return None

    def initial_triage_for_viable_locations(self, townhall_center):
        """ Find all positions behind the mineral line"""
        surroundings = range(-11, 12)
        townhall_mineral_fields = self.state.mineral_field.closer_than(10, townhall_center)
        if townhall_mineral_fields:
            self.viable_points = [
                point
                for point in (
                    Point2((x + townhall_center.x, y + townhall_center.y))
                    for x in surroundings
                    for y in surroundings
                    if 121 >= x * x + y * y >= 81
                )
                if abs(point.distance_to(townhall_mineral_fields.closest_to(point)) - 3) < 0.5
            ]

    async def prepare_building_positions(self, center):
        """Check all possible positions behind the mineral line when a hatchery is built"""
        self.initial_triage_for_viable_locations(center)
        await self.final_triage_for_viable_locations()
