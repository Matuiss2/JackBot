"""Everything related to controlling overseers goes here"""
from sc2.constants import AbilityId


class OverseerControl:
    """Can be improved a lot, make one follow the army and improve existing logic as well"""

    def __init__(self, main):
        self.main = main
        self.overseers = None

    async def should_handle(self):
        """Requirements to move the overlords"""
        self.overseers = self.main.overseers
        return self.overseers and self.main.ready_bases

    async def handle(self):
        """It sends the overseers at the closest bases and creates changelings can be improved a lot"""
        for overseer in (ovs for ovs in self.overseers if ovs.distance_to(self.main.ready_bases.closest_to(ovs)) > 5):
            for base in (th for th in self.main.ready_bases if th.distance_to(self.overseers.closest_to(th)) > 5):
                self.main.add_action(overseer.move(base))

        for overseer in self.overseers.filter(lambda ov: ov.energy >= 50):
            self.main.add_action(overseer(AbilityId.SPAWNCHANGELING_SPAWNCHANGELING))
