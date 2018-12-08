"""Everything related to building logic for the lairs goes here"""
from sc2.constants import CANCEL_MORPHLAIR, LAIR, UPGRADETOLAIR_LAIR


class BuildLair:
    """Maybe can be improved, probably its a bit greedy"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_bases = None

    async def should_handle(self):
        """Builds the lair"""
        local_controller = self.ai
        self.selected_bases = local_controller.hatcheries.ready.idle
        return (
            not (local_controller.lairs or local_controller.hives)
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.evochambers.ready) >= 2)
            )
            and local_controller.can_build_unique(LAIR, local_controller.caverns, self.selected_bases)
            and not await self.morphing_hatcheries()
        )

    async def handle(self):
        """Finishes the action of making the lair choosing the safest base"""
        local_controller = self.ai
        local_controller.add_action(
            self.selected_bases.furthest_to(local_controller.game_info.map_center)(UPGRADETOLAIR_LAIR)
        )
        return True

    async def morphing_hatcheries(self):
        """Check if there is a hatchery morphing looping all hatcheries"""
        local_controller = self.ai
        for hatch in local_controller.hatcheries:
            if await local_controller.is_morphing(hatch, CANCEL_MORPHLAIR):
                return True
        return False
