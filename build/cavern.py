"""Everything related to building logic for the ultra cavern goes here"""
from sc2.constants import ULTRALISKCAVERN


class BuildCavern:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the ultralisk cavern, placement can maybe be improved(far from priority)"""
        if self.ai.caverns:
            return False

        return (
            self.ai.evochambers
            and self.ai.hives
            and self.ai.can_afford(ULTRALISKCAVERN)
            and not self.ai.already_pending(ULTRALISKCAVERN)
        )

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not build between the main and natural"""
        position = await self.ai.get_production_position()
        if position:
            await self.ai.build(ULTRALISKCAVERN, position)
            return True

        await self.ai.build(
            ULTRALISKCAVERN,
            near=self.ai.townhalls.furthest_to(self.ai.game_info.map_center).position.towards(
                self.ai.main_base_ramp.depot_in_middle, 6
            ),
        )
        return True
