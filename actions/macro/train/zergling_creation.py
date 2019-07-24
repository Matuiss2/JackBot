"""Everything related to training zergling goes here"""
from sc2.constants import UnitTypeId, UpgradeId


class ZerglingCreation:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to train zerglings, good enough for now but ratio values can probably be improved"""
        if self.block_production_for_upgrade or not self.main.can_train(UnitTypeId.ZERGLING, self.main.pools.ready):
            return False
        if self.train_to_avoid_mineral_overflow:
            return True
        if self.block_production_for_better_units:
            return False
        if self.main.floating_buildings_bm:
            return not (self.main.supply_used > 150 or len(self.main.mutalisks) * 10 <= self.main.zergling_amount)
        return True

    async def handle(self):
        """Execute the action of training zerglings"""
        self.main.add_action(self.main.larvae.random.train(UnitTypeId.ZERGLING))

    @property
    def block_production_for_upgrade(self):
        """ Don't make zerglings if the zergling speed isn't done yet after 2:25"""
        return (
            not self.main.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED)
            and self.main.time > 145
            and not self.main.close_enemy_production
        )

    @property
    def block_production_for_better_units(self):
        """ Block zerglings if there are better units to be made"""
        return (self.main.hydradens.ready and self.main.hydra_amount * 3 <= self.main.zergling_amount) or (
            self.main.caverns.ready and self.main.ultra_amount * 8.5 <= self.main.zergling_amount
        )

    @property
    def train_to_avoid_mineral_overflow(self):
        """ When overflowing with minerals and have a low amount of bases build zerglings"""
        return self.main.minerals >= 600 and self.main.ready_base_amount <= 5
