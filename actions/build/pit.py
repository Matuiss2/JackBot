"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import INFESTATIONPIT, ZERGGROUNDARMORSLEVEL2


class BuildPit:
    """Ok for now"""
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the infestation pit, placement can maybe be improved(far from priority)"""
        if self.ai.pits or len(self.ai.townhalls) < 4:
            return False

        if self.ai.already_pending(INFESTATIONPIT):
            return False

        return (
            self.ai.evochambers
            and self.ai.lairs.ready
            and self.ai.already_pending_upgrade(ZERGGROUNDARMORSLEVEL2) > 0
            and self.ai.can_afford(INFESTATIONPIT)
            and self.ai.townhalls
        )

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        position = await self.ai.get_production_position()
        if position:
            await self.ai.build(INFESTATIONPIT, position)
            return True

        await self.ai.build(
                INFESTATIONPIT,
                near=self.ai.townhalls.furthest_to(self.ai.game_info.map_center).position.towards_with_random_angle(
                    self.ai.game_info.map_center, -14
                ),
            )
        return True
