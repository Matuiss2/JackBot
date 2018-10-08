from sc2.constants import CANCEL_MORPHLAIR, UPGRADETOLAIR_LAIR


class BuildLair:
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
        self.ai.actions.append(self.hatcheries.ready.furthest_to(self.ai._game_info.map_center)(UPGRADETOLAIR_LAIR))
        return True

    async def morphing_hatcheries(self):
        for hatch in self.hatcheries:
            if await self.is_morphing(hatch):
                return True
        return False

    async def is_morphing(self, hatch):
        abilities = await self.ai.get_available_abilities(hatch)
        return CANCEL_MORPHLAIR in abilities
