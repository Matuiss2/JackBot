"""Everything related to the logic for blocking expansions"""
from sc2.constants import BURROW, BURROWDOWN_ZERGLING


class BlockExpansions:
    """Can be improved, it bugs occasionally, sometimes it just doesnt send some of the zerglings"""

    def __init__(self, main):
        self.main = main
        self.zerglings = None

    async def should_handle(self):
        """Requirements for executing the blocking"""
        self.zerglings = self.main.zerglings.idle
        return (
            self.zerglings
            and not self.main.burrowed_lings
            and len(self.zerglings) >= 4
            and self.main.already_pending_upgrade(BURROW) == 1
        )

    async def handle(self):
        """Take the 4 'safest' zerglings and send them to the furthest enemy expansion locations,
        excluding the main and the natural, to block it, need to fix the mentioned bug"""
        self.main.burrowed_lings = [
            unit.tag for unit in self.zerglings.sorted_by_distance_to(self.main.ordered_expansions[0])[:4]
        ]
        for list_index, zergling in enumerate(self.zerglings.tags_in(self.main.burrowed_lings)):
            location = self.main.ordered_expansions[:-1][-list_index - 1]
            self.main.add_action(zergling.move(location))
            self.main.add_action(zergling(BURROWDOWN_ZERGLING, queue=True))
