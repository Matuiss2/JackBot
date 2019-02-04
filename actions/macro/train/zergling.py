"""Everything related to training zergling goes here"""
from sc2.constants import ZERGLING, ZERGLINGMOVEMENTSPEED


class TrainZergling:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to train zerglings, good enough for now but ratio values can probably be improved"""
        if (
            not self.controller.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) and self.controller.time < 145
        ) and not self.controller.close_enemy_production:
            return False
        if not self.controller.can_train(ZERGLING, self.controller.pools.ready, hive_lock=True, cavern_lock=True):
            return False
        zergling_quantity = self.controller.zergling_amount
        if self.controller.hydradens.ready and self.controller.hydra_amount * 3 <= zergling_quantity:
            return False
        if self.controller.floating_buildings_bm:
            if self.controller.supply_used > 150 or len(self.controller.mutalisks) * 10 <= zergling_quantity:
                return False
        return True

    async def handle(self):
        """Execute the action of training zerglings"""
        self.controller.add_action(self.controller.larvae.random.train(ZERGLING))
        return True
