"""Files that become unused, but might come back"""

from sc2.constants import BURROW, BURROWDOWN_ZERGLING  # block expansions
from sc2.constants import OVERLORDSPEED, RESEARCH_BURROW, RESEARCH_PNEUMATIZEDCARAPACE  # base_upgrades


# micro\block_expansions """Everything related to the logic for blocking expansions"""
class BlockExpansions:
    """Can be improved, it bugs occasionally, sometimes it just doesnt send some of the zerglings"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements for executing the blocking"""
        return (
            self.main.zerglings.idle
            and not self.main.burrowed_lings
            and len(self.main.zerglings) >= 4
            and self.main.already_pending_upgrade(BURROW) == 1
        )

    async def handle(self):
        """Take the 4 'safest' zerglings and send them to the furthest enemy expansion locations,
        excluding the main and the natural, to block it, need to fix the mentioned bug"""
        self.main.burrowed_lings = [
            unit.tag for unit in self.main.zerglings.sorted_by_distance_to(self.main.ordered_expansions[0])[:4]
        ]
        for list_index, zergling in enumerate(self.main.zerglings.tags_in(self.main.burrowed_lings)):
            location = self.main.ordered_expansions[:-1][-list_index - 1]
            self.main.add_action(zergling.move(location))
            self.main.add_action(zergling(BURROWDOWN_ZERGLING, queue=True))


# upgrades\base_upgrades """Upgrading ov speed and burrow"""
class UpgradesFromBases:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from bases"""
        if self.main.zergling_amount <= 19 and not self.main.close_enemy_production:
            return False
        if self.main.can_upgrade(BURROW, RESEARCH_BURROW, self.main.hatcheries.idle):
            self.selected_research = RESEARCH_BURROW
            return True
        if self.main.caverns and self.main.can_upgrade(
            OVERLORDSPEED, RESEARCH_PNEUMATIZEDCARAPACE, self.main.hatcheries.idle
        ):
            self.selected_research = RESEARCH_PNEUMATIZEDCARAPACE
            return True

    async def handle(self):
        """Execute the action of upgrading burrow or ov speed"""
        self.main.add_action(self.main.hatcheries.idle.random(self.selected_research))
        return True
