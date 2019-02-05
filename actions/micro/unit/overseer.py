"""Everything related to controlling overseers goes here"""


class Overseer:
    """Can be improved a lot, make one follow the army and improve existing logic as well"""

    def __init__(self, main):
        self.main = main
        self.bases = self.overseers = None

    async def should_handle(self):
        """Requirements to move the overlords"""
        self.bases = self.main.townhalls.ready
        self.overseers = self.main.overseers
        return self.overseers and self.bases

    async def handle(self):
        """It sends the overseers at the closest bases, can be improved a lot"""
        for overseer in (ovs for ovs in self.overseers if ovs.distance_to(self.bases.closest_to(ovs)) > 5):
            for base in (th for th in self.bases if th.distance_to(self.overseers.closest_to(th)) > 5):
                if not self.overseers.closer_than(5, base):
                    self.main.add_action(overseer.move(base))
