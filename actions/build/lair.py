"""Everything related to building logic for the lairs goes here"""
from sc2.constants import CANCEL_MORPHLAIR, UPGRADETOLAIR_LAIR


class BuildLair:
    """Maybe can be improved, it can argued that its a bit greedy"""
    def __init__(self, ai):
        self.ai = ai
        self.hatcheries = None

    async def should_handle(self, iteration):
        """Builds the infestation pit, placement can maybe be improved(far from priority)"""
        if self.ai.lairs or self.ai.hives:
            return False

        self.hatcheries = self.ai.hatcheries.ready

        return (
            self.hatcheries.idle
            and len(self.ai.townhalls) >= 3
            and self.ai.can_afford(UPGRADETOLAIR_LAIR)
            and not await self.morphing_hatcheries()
        )

    async def handle(self, iteration):
        """Finishes the action of making the lair choosing the safest base"""
        self.ai.adding(self.hatcheries.ready.furthest_to(self.ai._game_info.map_center)(UPGRADETOLAIR_LAIR))
        return True

    async def morphing_hatcheries(self):
        """Check if there is a hatchery morphing looping all hatcheries"""
        for hatch in self.hatcheries:
            if await self.is_morphing(hatch):
                return True
        return False

    async def is_morphing(self, hatch):
        """Check if there is a hatchery morphing by checking the available abilities"""
        abilities = await self.ai.get_available_abilities(hatch)
        return CANCEL_MORPHLAIR in abilities
