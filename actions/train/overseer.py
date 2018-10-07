from sc2.constants import (OVERLORDCOCOON, OVERSEER, MORPH_OVERSEER, CANCEL_MORPHOVERSEER)

class TrainOverseer:

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return (
            (self.ai.lairs or self.ai.hives)
            and self.ai.overlords
            and not await self.morphing_overlords()
            and self.ai.can_afford(OVERSEER)
            and not self.ai.overseers
        )

    async def handle(self, iteration):
        """Morph the overseer"""
        self.ai.actions.append(self.ai.overlords.random(MORPH_OVERSEER))

    async def morphing_overlords(self):
        for hatch in self.ai.units(OVERLORDCOCOON):
            if await self.is_morphing(hatch):
                return True
        return False

    async def is_morphing(self, hatch):
        abilities = await self.ai.get_available_abilities(hatch)
        return CANCEL_MORPHOVERSEER in abilities
