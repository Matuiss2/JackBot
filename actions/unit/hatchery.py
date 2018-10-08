from sc2.constants import CANCEL


class Hatchery:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return self.ai.close_enemy_production and self.ai.time < 300

    async def handle(self, iteration):
        """Make the cancelling general"""
        for building in self.ai.units.structure.not_ready.filter(lambda x: x.type_id not in self.ai.tumors):
            if (
                building.health_percentage < building.build_progress - 0.4
                or building.health_percentage < 0.1
                and building.build_progress > 0.15
            ):
                self.ai.actions.append((building(CANCEL)))
