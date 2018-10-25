"""Everything related to training overseers goes here"""
from sc2.constants import CANCEL_MORPHOVERSEER, MORPH_OVERSEER, OVERLORDCOCOON, OVERSEER


class TrainOverseer:
    """Can be expanded"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            (local_controller.lairs or local_controller.hives)
            and local_controller.overlords
            and not await self.morphing_overlords()
            and local_controller.can_afford(OVERSEER)
            and not local_controller.overseers
        )

    async def handle(self, iteration):
        """Morph the overseer"""
        local_controller = self.ai
        local_controller.actions.append(local_controller.overlords.random(MORPH_OVERSEER))

    async def morphing_overlords(self):
        """Check if there is a overlord morphing looping through all cocoons"""
        for hatch in self.ai.units(OVERLORDCOCOON):
            if await self.is_morphing(hatch):
                return True
        return False

    async def is_morphing(self, hatch):
        """Check if there is a overlord morphing looping by checking available abilities"""
        abilities = await self.ai.get_available_abilities(hatch)
        return CANCEL_MORPHOVERSEER in abilities
