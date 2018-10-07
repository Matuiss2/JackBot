from sc2.constants import (HIVE, LAIR, INFESTATIONPIT, UPGRADETOHIVE_HIVE, CANCEL_MORPHHIVE)

class BuildHive:

    def __init__(self, ai):
        self.ai = ai
        self.lairs = None

    async def should_handle(self, iteration):
        """Builds the infestation pit, placement can maybe be improved(far from priority)"""
        if self.ai.hives:
            return False

        self.lairs = self.ai.lairs.ready

        return (
            self.ai.pit.ready
            and self.lairs.idle
            and self.ai.can_afford(HIVE)
            and not await self.morphing_lairs()
        )

    async def handle(self, iteration):
        self.ai.actions.append(self.lairs.ready.first(UPGRADETOHIVE_HIVE))
        return True

    async def morphing_lairs(self):
        for hatch in self.lairs:
            if await self.is_morphing(hatch):
                return True
        return False

    async def is_morphing(self, hatch):
        abilities = await self.ai.get_available_abilities(hatch)
        return CANCEL_MORPHHIVE in abilities
