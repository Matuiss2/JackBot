"""Everything related to training zergling goes here"""
from sc2.constants import ZERGLING, ZERGLINGMOVEMENTSPEED


class TrainZergling:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to train zerglings, good enough for now but ratio values can probably be improved"""
        if self.upgrades_lock():
            return False
        if not self.main.can_train(ZERGLING, self.main.pools.ready):
            return False
        if self.main.hydradens.ready and self.main.hydra_amount * 3 <= self.main.zergling_amount:
            return False
        if self.main.caverns.ready and len(self.main.ultralisks) * 8.5 <= self.main.zergling_amount:
            return False
        if self.main.floating_buildings_bm:
            return not (self.main.supply_used > 150 or len(self.main.mutalisks) * 10 <= self.main.zergling_amount)
        return True

    async def handle(self):
        """Execute the action of training zerglings"""
        self.main.add_action(self.main.larvae.random.train(ZERGLING))

    def upgrades_lock(self):
        """ Don't make zerglings if the zergling speed isn't done yet after 2:25"""
        return (
            not self.main.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
            and self.main.time < 145
            and not self.main.close_enemy_production
        )
