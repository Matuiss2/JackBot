"""Everything related to training overlords goes here"""
from sc2.constants import OVERLORD


class TrainOverlord:
    """Should be improved"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """We still get supply blocked sometimes, can be improved a lot still"""
        if self.main.supply_cap <= 200 and self.main.supply_left < (7 + self.main.supply_used // 7):
            overlords_in_queue = self.main.already_pending(OVERLORD)
            if self.main.can_train(OVERLORD):
                if (
                    len(self.main.drones.ready) == 14
                    or (self.main.overlord_amount == 2 and self.main.base_amount == 1)
                    or (self.main.base_amount == 2 and not self.main.pools)
                ):
                    return self.main.close_enemy_production
                if (self.main.base_amount in (1, 2) and overlords_in_queue) or (overlords_in_queue >= 3):
                    return False
                return True
            return False
        return False

    async def handle(self):
        """Execute the action of training overlords"""
        self.main.add_action(self.main.larvae.random.train(OVERLORD))
        return True
