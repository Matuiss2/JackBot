"""Everything related to training overlords goes here"""
from sc2.constants import OVERLORD


class TrainOverlord:
    """Should be improved"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """We still get supply blocked sometimes, can be improved a lot still"""
        local_controller = self.controller
        if local_controller.supply_cap <= 200 and local_controller.supply_left < (
            7 + local_controller.supply_used // 7
        ):
            overlords_in_queue = local_controller.already_pending(OVERLORD)
            if local_controller.can_train(OVERLORD):
                base_amount = len(local_controller.townhalls)
                if (
                    len(local_controller.drones.ready) == 14
                    or (len(local_controller.overlords) == 2 and base_amount == 1)
                    or (base_amount == 2 and not local_controller.pools)
                ):
                    return local_controller.close_enemy_production
                if (base_amount in (1, 2) and overlords_in_queue) or (overlords_in_queue >= 3):
                    return False
                return True
            return False
        return False

    async def handle(self):
        """Execute the action of training overlords"""
        local_controller = self.controller
        local_controller.add_action(local_controller.larvae.random.train(OVERLORD))
        return True
