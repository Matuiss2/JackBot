"""Everything related to the logic for blocking expansions"""
from sc2.constants import BURROW, BURROWDOWN_ZERGLING


class BlockExpansions:
    """Can be improved, it bugs occasionally, sometime it just doesnt send some of the zerglings"""

    def __init__(self, main):
        self.controller = main
        self.zerglings = None

    async def should_handle(self):
        """Requirements for executing the blocking"""
        local_controller = self.controller
        self.zerglings = local_controller.zerglings.idle
        return (
            self.zerglings
            and not local_controller.burrowed_lings
            and len(self.zerglings) >= 4
            and local_controller.already_pending_upgrade(BURROW) == 1
        )

    async def handle(self):
        """Take the 4 'safest' zerglings and send them to the furthest enemy expansion locations,
        excluding the main and the natural, to block it, need to fix the mentioned bug"""
        local_controller = self.controller
        local_controller.burrowed_lings = [
            unit.tag for unit in self.zerglings.sorted_by_distance_to(local_controller.ordered_expansions[0])[:4]
        ]
        for list_index, zergling in enumerate(self.zerglings.tags_in(local_controller.burrowed_lings)):
            location = local_controller.ordered_expansions[:-2][-list_index - 1]
            local_controller.add_action(zergling.move(location))
            local_controller.add_action(zergling(BURROWDOWN_ZERGLING, queue=True))
