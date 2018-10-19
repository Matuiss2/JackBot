"""Everything related to the logic for blocking expansions"""
from sc2.constants import BURROW, BURROWDOWN_ZERGLING


class BlockExpansions:
    """Needs few improvements like refill the force in case of failing until it succeeds(for a while at least)"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements for handle"""
        zerglings = self.ai.zerglings.idle
        if (
            zerglings
            and not self.ai.burrowed_lings
            and len(zerglings) >= 6
            and self.ai.already_pending_upgrade(BURROW) == 1
        ):
            return True
        return False

    async def handle(self, iteration):
        """Take the 6 'safest' zerglings and send them to the closest enemy expansion locations to burrow"""
        zerglings = self.ai.zerglings.idle
        self.ai.burrowed_lings = [
            unit.tag for unit in zerglings.sorted_by_distance_to(self.ai.ordered_expansions[1])[:6]
        ]
        for list_index, zergling in enumerate(zerglings.tags_in(self.ai.burrowed_lings)):
            location = self.ai.ordered_expansions[-list_index - 1]

            # are we allowed to query into the dark?
            # if await self.ai.can_place(HATCHERY, location):

            self.ai.add_action(zergling.move(location))
            self.ai.add_action(zergling(BURROWDOWN_ZERGLING, queue=True))
            # print("burrowed", zergling.tag, location)

            # else:
            #     self.ai.burrowed_lings.remove(zergling.tag)
