"""Everything related to cancelling buildings goes here"""
from sc2.constants import CANCEL, HATCHERY


class Buildings:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements for cancelling the building"""
        local_controller = self.controller
        return (
            local_controller.time < 300
            if local_controller.close_enemy_production
            else local_controller.structures.not_ready
        )

    async def handle(self):
        """Cancel the threatened building"""
        local_controller = self.controller
        for building in local_controller.structures.not_ready.exclude_type(local_controller.tumors):
            build_progress = building.build_progress
            relative_health = building.health_percentage
            if (relative_health < build_progress - 0.5 or relative_health < 0.05 and build_progress > 0.1) or (
                building.type_id == HATCHERY and local_controller.close_enemy_production
            ):
                local_controller.add_action((building(CANCEL)))
