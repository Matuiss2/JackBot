from sc2.constants import (HIVE, ULTRALISKCAVERN, EVOLUTIONCHAMBER)

class BuildCavern:

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
        await self.ai.build(
            ULTRALISKCAVERN,
            near=self.ai.townhalls.furthest_to(self.ai.game_info.map_center).position.towards_with_random_angle(
                self.ai.game_info.map_center, -10
            ),
        )
        return True
