"""Everything related to building logic for the extractors goes here"""
from sc2.constants import EXTRACTOR


class BuildExtractor:
    """Can probably be improved,
    but I think the problem is more on the vespene collection than the extractor building"""

    def __init__(self, main):
        self.controller = main
        self.drone = self.geyser = None

    async def should_handle(self):
        """Couldn't find another way to build the geysers its heavily based on Burny's approach,
         still trying to find the optimal number"""
        finished_bases = self.controller.townhalls.ready
        if (self.controller.vespene * 1.25 > self.controller.minerals) or (
            not self.controller.building_requirement(EXTRACTOR, finished_bases)
        ):
            return False
        gas_amount = len(self.controller.extractors)
        for geyser in self.controller.state.vespene_geyser.closer_than(10, finished_bases.random):
            self.drone = self.controller.select_build_worker(geyser.position)
            if not self.drone or self.controller.already_pending(EXTRACTOR) or gas_amount > 10:
                return False
            self.geyser = geyser
            if (not gas_amount and self.controller.pools) or gas_amount < 3 <= len(self.controller.townhalls):
                return True
            return (self.controller.time > 900 or self.controller.spires) or (
                    self.controller.hydradens and gas_amount < 8
            )

    async def handle(self):
        """Just finish the action of building the extractor"""
        self.controller.add_action(self.drone.build(EXTRACTOR, self.geyser))
        return True
