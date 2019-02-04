"""Everything related to cancelling buildings goes here"""
from sc2.constants import CANCEL, HATCHERY


class Buildings:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements for cancelling the building"""
        return (
            self.controller.time < 300
            if self.controller.close_enemy_production
            else self.controller.structures.not_ready
        )

    async def handle(self):
        """Cancel the threatened building adapted from Burny's bot"""
        for building in self.controller.structures.not_ready.exclude_type(self.controller.tumors):
            build_progress = building.build_progress
            relative_health = building.health_percentage
            if (relative_health < build_progress - 0.5 or relative_health < 0.05 and build_progress > 0.1) or (
                building.type_id == HATCHERY and self.controller.close_enemy_production
            ):
                self.controller.add_action((building(CANCEL)))
