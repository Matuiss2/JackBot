"""Everything related to training overlords goes here"""
from sc2.constants import OVERLORD


class TrainOverlord:
    """Should be improved"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """We still get supply blocked sometimes, can be improved a lot still"""
        if self.controller.supply_cap <= 200 and self.controller.supply_left < (7 + self.controller.supply_used // 7):
            overlords_in_queue = self.controller.already_pending(OVERLORD)
            if self.controller.can_train(OVERLORD):
                if (
                    len(self.controller.drones.ready) == 14
                    or (len(self.controller.overlords) == 2 and self.controller.base_amount == 1)
                    or (self.controller.base_amount == 2 and not self.controller.pools)
                ):
                    return self.controller.close_enemy_production
                if (self.controller.base_amount in (1, 2) and overlords_in_queue) or (overlords_in_queue >= 3):
                    return False
                return True
            return False
        return False

    async def handle(self):
        """Execute the action of training overlords"""
        self.controller.add_action(self.controller.larvae.random.train(OVERLORD))
        return True
