"""Everything related to training zergling goes here"""
from sc2.constants import ZERGLING, ZERGLINGMOVEMENTSPEED


class TrainZergling:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to train zerglings, good enough for now but ratio values can probably be improved"""
        if (
            not self.main.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) and self.main.time < 145
        ) and not self.main.close_enemy_production:
            return False
        if not self.main.can_train(ZERGLING, self.main.pools.ready, hive_lock=True, cavern_lock=True):
            return False
        zergling_quantity = self.main.zergling_amount
        if self.main.hydradens.ready and self.main.hydra_amount * 3 <= zergling_quantity:
            return False
        if self.main.floating_buildings_bm:
            if self.main.supply_used > 150 or len(self.main.mutalisks) * 10 <= zergling_quantity:
                return False
        return True

    async def handle(self):
        """Execute the action of training zerglings"""
        self.main.add_action(self.main.larvae.random.train(ZERGLING))
        return True
