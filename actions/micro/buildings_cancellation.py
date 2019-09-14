"""Everything related to cancelling buildings goes here"""
from sc2.constants import AbilityId, UnitTypeId


class BuildingsCancellation:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements for cancelling the building"""
        return self.main.time < 300 if self.main.close_enemy_production else self.main.structures.not_ready

    async def handle(self):
        """Cancel the threatened building adapted from Burny's bot"""
        for building in self.main.structures.not_ready.exclude_type(self.main.tumors):
            build_progress = building.build_progress
            relative_health = building.health_percentage
            if (relative_health < build_progress - 0.5 or relative_health < 0.05 and build_progress > 0.1) or (
                building.type_id == UnitTypeId.HATCHERY and self.main.close_enemy_production
            ):
                self.main.add_action((building(AbilityId.CANCEL)))
