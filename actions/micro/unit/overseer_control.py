"""Everything related to controlling overseers goes here"""
from itertools import product
from sc2.constants import AbilityId


class OverseerControl:
    """Can be improved a lot, make one follow the army and improve existing logic as well"""

    def __init__(self, main):
        self.main = main
        self.overseers = self.ready_bases = None

    async def should_handle(self):
        """Requirements to move the overlords"""
        self.overseers = self.main.overseers
        self.ready_bases = self.main.ready_bases
        return self.overseers and self.ready_bases

    async def handle(self):
        """It sends the overseers at the closest bases and creates changelings can be improved a lot"""
        for overseer, base in product(
            self.overseers.filter(lambda ov: ov.distance_to(self.ready_bases.closest_to(ov)) > 5),
            self.ready_bases.filter(lambda th: th.distance_to(self.overseers.closest_to(th)) > 5),
        ):
            self.main.add_action(overseer.move(base))
        for overseer in self.overseers.filter(lambda ov: ov.energy >= 50):
            self.main.add_action(overseer(AbilityId.SPAWNCHANGELING_SPAWNCHANGELING))
