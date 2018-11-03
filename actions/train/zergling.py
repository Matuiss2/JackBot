"""Everything related to training zergling goes here"""
from sc2.constants import ZERGLING, ZERGLINGMOVEMENTSPEED


class TrainZergling:
    """Ok for now, mutas ratio untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """good enough for now"""
        local_controller = self.ai
        zerglings = local_controller.zerglings
        game_time = local_controller.time
        if (
            not local_controller.pools.ready
            or (not local_controller.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) and local_controller.time < 160)
        ) and not local_controller.close_enemy_production:
            return False

        if not local_controller.can_train(ZERGLING):
            return False
        if game_time < 1380:
            if local_controller.caverns.ready:
                if not len(local_controller.ultralisks) * 8.5 > len(zerglings):
                    return False
            if local_controller.hydradens.ready:
                if not len(local_controller.hydras) * 3 > len(zerglings):
                    return False
        if local_controller.floating_buildings_bm:
            if local_controller.supply_used > 150:
                return False
            if not len(local_controller.mutalisks) * 10 > len(zerglings):
                return False
        return True

    async def handle(self, iteration):
        """Execute the action of training zerglings"""
        local_controller = self.ai
        local_controller.add_action(local_controller.larvae.random.train(ZERGLING))
        return True
