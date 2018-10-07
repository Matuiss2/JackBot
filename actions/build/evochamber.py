from sc2.constants import (EVOLUTIONCHAMBER)

class BuildEvochamber:

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the evolution chambers, placement can maybe be improved(far from priority),
        also there is some occasional bug that prevents both to be built at the same time,
        probably related to placement"""
        pool = self.ai.pools
        evochamber = self.ai.evochambers
        if (
            pool.ready
            and self.ai.can_afford(EVOLUTIONCHAMBER)
            and len(self.ai.townhalls) >= 3
            and len(evochamber) + self.ai.already_pending(EVOLUTIONCHAMBER) < 2
        ):
            return True
        return False

    async def handle(self, iteration):
        furthest_base = self.ai.townhalls.furthest_to(self.ai.game_info.map_center)
        second_base = (self.ai.townhalls - {furthest_base}).closest_to(furthest_base)
        await self.ai.build(
            EVOLUTIONCHAMBER, near=second_base.position.towards_with_random_angle(self.ai.game_info.map_center, -14)
        )
        return True
