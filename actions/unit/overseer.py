"""Everything related to controlling overseers goes here"""


class Overseer:
    """Can be improved a lot, it barely do its job as of now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return local_controller.overseers and (
            local_controller.zerglings | local_controller.ultralisks or local_controller.townhalls
        )

    async def handle(self, iteration):
        """It sends the overseer at the closest ally, can be improved a lot"""
        local_controller = self.ai
        bases = local_controller.townhalls.ready
        overseers = local_controller.overseers
        if bases:
            for overseer in (
                ovs for ovs in overseers if ovs.distance_to(bases.closest_to(ovs)) > 5
            ):
                for base in (th for th in bases if th.distance_to(overseers.closest_to(th)) > 5):
                    if not overseers.closer_than(5, base):
                        local_controller.add_action(overseer.move(base))
