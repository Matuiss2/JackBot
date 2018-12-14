"""Everything related to the logic for blocking expansions"""
from sc2.constants import BURROW, BURROWDOWN_ZERGLING


class BlockExpansions:
    """Needs improvements"""

    def __init__(self, main):
        self.controller = main
        self.zerglings = None

    async def should_handle(self):
        """Requirements for handle"""
        local_controller = self.controller
        self.zerglings = local_controller.zerglings.idle
        return (
            self.zerglings
            and not local_controller.burrowed_lings
            and len(self.zerglings) >= 5
            and local_controller.already_pending_upgrade(BURROW) == 1
        )

    async def handle(self):
        """Take the 5 'safest' zerglings and send them to the furthest enemy expansion locations to burrow
        needs improvements refill the force in case of failing until it succeeds(for a while at least),
         sometimes it just get stuck, also no need to send it to the enemy main"""
        local_controller = self.controller
        local_controller.burrowed_lings = [
            unit.tag for unit in self.zerglings.sorted_by_distance_to(local_controller.ordered_expansions[1])[:5]
        ]
        for list_index, zergling in enumerate(self.zerglings.tags_in(local_controller.burrowed_lings)):
            location = local_controller.ordered_expansions[:-1][-list_index - 1]
            local_controller.add_action(zergling.move(location))
            local_controller.add_action(zergling(BURROWDOWN_ZERGLING, queue=True))
