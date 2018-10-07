from sc2.constants import (CANCEL)

class Hatchery:

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return self.ai.close_enemy_production and self.ai.time < 300

    async def handle(self, iteration):
        """find the hatcheries that are building, and have low health and cancel then,
        can be better, its easy to burst 400 hp, will look into that later,
         checking how fast the hp is going down might be a good idea"""
        for building in self.ai.hatcheries.filter(lambda x: 0.2 < x.build_progress < 1 and x.health < 400):
            self.ai.actions.append(building(CANCEL))
