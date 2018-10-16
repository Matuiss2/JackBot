from sc2.constants import BURROW, BURROWDOWN_ZERGLING


class BlockExpansions:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        zerglings = self.ai.zerglings.idle
        if (
            zerglings
            and not self.ai.burrowed_lings
            and len(zerglings) >= 6
            and self.ai.already_pending_upgrade(BURROW) == 1
        ):
            return True
        else:
            return False

    async def handle(self, iteration):
        zerglings = self.ai.zerglings.idle
        self.ai.burrowed_lings = [
            unit.tag for unit in zerglings.sorted_by_distance_to(self.ai.ordered_expansions[1])[:6]
        ]
        for n, zergling in enumerate(zerglings.tags_in(self.ai.burrowed_lings)):
            location = self.ai.ordered_expansions[-n - 1]

            # are we allowed to query into the dark?
            # if await self.ai.can_place(HATCHERY, location):

            self.ai.add_action(zergling.move(location))
            self.ai.add_action(zergling(BURROWDOWN_ZERGLING, queue=True))
            # print("burrowed", zergling.tag, location)

            # else:
            #     self.ai.burrowed_lings.remove(zergling.tag)
