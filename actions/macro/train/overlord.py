"""Everything related to training overlords goes here"""
from sc2.constants import OVERLORD


class TrainOverlord:
    """Should be improved"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """We still get supply blocked sometimes, can be improved a lot still"""
        if self.main.supply_cap < 200 and self.main.supply_left < (8 + self.main.supply_used // 7):
            if self.main.can_train(OVERLORD):
                if self.game_beginning_lock():
                    return self.main.close_enemy_production
                if (self.main.base_amount in (1, 2) and self.main.ovs_in_queue) or (self.main.ovs_in_queue >= 3):
                    return False
                return True
            return False
        return False

    async def handle(self):
        """Execute the action of training overlords"""
        self.main.add_action(self.main.larvae.random.train(OVERLORD))

    def game_beginning_lock(self):
        """ Few locks for overlords on the early game, could be replaced for a hardcoded build order list"""
        return (
            len(self.main.drones.ready) == 14
            or (self.main.overlord_amount == 2 and self.main.base_amount == 1)
            or (self.main.base_amount == 2 and not self.main.pools)
        )
