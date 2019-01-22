"""Everything related to training zergling goes here"""
from sc2.constants import HIVE, ZERGLING, ZERGLINGMOVEMENTSPEED


class TrainZergling:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """good enough for now, maybe ratio values can be improved"""
        local_controller = self.controller
        zerglings = local_controller.zerglings
        if (
            not local_controller.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) and local_controller.time < 150
        ) and not local_controller.close_enemy_production:
            return False
        if (
            local_controller.pits.ready
            and not local_controller.hives
            and not local_controller.already_pending(HIVE, all_units=True)
        ):
            return False
        cavern = local_controller.caverns
        if not local_controller.can_train(ZERGLING, local_controller.pools.ready) or (
            local_controller.hives and not cavern
        ):
            return False
        zergling_quantity = len(zerglings)
        if local_controller.hydradens.ready and len(local_controller.hydras) * 3 <= zergling_quantity:
            return False
        if local_controller.floating_buildings_bm:
            if local_controller.supply_used > 150 or len(local_controller.mutalisks) * 10 <= zergling_quantity:
                return False
        return True

    async def handle(self):
        """Execute the action of training zerglings"""
        local_controller = self.controller
        local_controller.add_action(local_controller.larvae.random.train(ZERGLING))
        return True
