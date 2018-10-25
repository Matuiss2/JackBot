"""Everything related to cancelling buildings goes here"""
from sc2.constants import CANCEL, HATCHERY


class Buildings:
    """Ok for now, can be improved, it fails sometimes but is VERY rare"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return self.ai.time < 300 if self.ai.close_enemy_production else self.ai.structures.not_ready

    async def handle(self, iteration):
        """Make the cancelling general"""
        for building in self.ai.structures.not_ready.filter(lambda x: x.type_id not in self.ai.tumors):
            if (
                building.health_percentage < building.build_progress - 0.5
                or building.health_percentage < 0.05
                and building.build_progress > 0.1
            ) or (building.type_id == HATCHERY and self.ai.close_enemy_production):
                self.ai.add_action((building(CANCEL)))
