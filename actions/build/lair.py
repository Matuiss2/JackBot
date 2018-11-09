"""Everything related to building logic for the lairs goes here"""
from sc2.constants import CANCEL_MORPHLAIR, UPGRADETOLAIR_LAIR


class BuildLair:
    """Maybe can be improved, it can argued that its a bit greedy"""

    def __init__(self, ai):
        self.ai = ai
        self.hatcheries = None

    async def should_handle(self, iteration):
        """Builds the infestation pit, placement can maybe be improved(far from priority)"""
        local_controller = self.ai
        if local_controller.lairs or local_controller.hives:
            return False

        self.hatcheries = local_controller.hatcheries.ready

        return (
            self.hatcheries.idle
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.evochambers.ready) >= 2)
            )
            and local_controller.can_afford(UPGRADETOLAIR_LAIR)
            and not await self.morphing_hatcheries()
        )

    async def handle(self, iteration):
        """Finishes the action of making the lair choosing the safest base"""
        local_controller = self.ai
        local_controller.add_action(
            self.hatcheries.ready.furthest_to(local_controller.game_info.map_center)(UPGRADETOLAIR_LAIR)
        )
        return True

    async def morphing_hatcheries(self):
        """Check if there is a hatchery morphing looping all hatcheries"""
        for hatch in self.hatcheries:
            if await self.ai.is_morphing(hatch, CANCEL_MORPHLAIR):
                return True
        return False
