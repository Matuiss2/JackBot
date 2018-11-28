"""Everything related to training overlords goes here"""
from sc2.constants import OVERLORD


class TrainOverlord:
    """Should be improved"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """We still get supply blocked sometimes, can be improved a lot still"""
        if self.ai.supply_cap <= 200 and self.ai.supply_left < (7 + self.ai.supply_used // 7):
            overlords_in_queue = self.ai.already_pending
            if self.ai.can_train(OVERLORD):
                base_amount = len(self.ai.townhalls)  # so it just calculate once per loop
                if (
                    len(self.ai.workers.ready) == 14
                    or (len(self.ai.overlords) == 2 and base_amount == 1)
                    or (base_amount == 2 and not self.ai.pools)
                ):
                    return self.ai.close_enemy_production
                if (base_amount in (1, 2) and overlords_in_queue(OVERLORD)) or (overlords_in_queue(OVERLORD) >= 2):
                    return False
                return True
            return False
        return False

    async def handle(self, iteration):
        """Execute the action of training overlords"""
        self.ai.add_action(self.ai.larvae.random.train(OVERLORD))
        return True
