"""Everything related to cancelling buildings goes here"""
from sc2.constants import CANCEL, HATCHERY


class Buildings:
    """Ok for now but can be improved, it works every time
     but it should prevent cancelled buildings to be replaced right after"""

    def __init__(self, ai):
        self.controller = ai

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        return (
            local_controller.time < 300
            if local_controller.close_enemy_production
            else local_controller.structures.not_ready
        )

    async def handle(self):
        """Make the cancelling general"""
        local_controller = self.controller
        for building in local_controller.structures.not_ready.exclude_type(local_controller.tumors):
            build_progress = building.build_progress
            relative_health = building.health_percentage
            if (relative_health < build_progress - 0.5 or relative_health < 0.05 and build_progress > 0.1) or (
                building.type_id == HATCHERY and local_controller.close_enemy_production
            ):
                local_controller.add_action((building(CANCEL)))
