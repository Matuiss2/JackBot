"""Everything related to controlling overseers goes here"""


class Overseer:
    """Can be improved a lot, it barely do its job as of now"""

    def __init__(self, ai):
        self.ai = ai
        self.bases = None
        self.overseers = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        self.bases = local_controller.townhalls.ready
        self.overseers = local_controller.overseers
        return self.overseers and self.bases

    async def handle(self, iteration):
        """It sends the overseer at the closest ally, can be improved a lot"""
        local_controller = self.ai
        for overseer in (ovs for ovs in self.overseers if ovs.distance_to(self.bases.closest_to(ovs)) > 5):
            for base in (th for th in self.bases if th.distance_to(self.overseers.closest_to(th)) > 5):
                if not self.overseers.closer_than(5, base):
                    local_controller.add_action(overseer.move(base))
