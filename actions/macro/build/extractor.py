"""Everything related to building logic for the extractors goes here"""
from sc2.constants import EXTRACTOR


class BuildExtractor:
    """Can probably be improved,
    but I think the problem is more on the vespene collection than the extractor building"""

    def __init__(self, main):
        self.main = main
        self.drone = self.geyser = None

    async def should_handle(self):
        """Couldn't find another way to build the geysers its heavily based on Burny's approach,
         still trying to find the optimal number"""

        if (
            self.main.vespene * 1.25 > self.main.minerals
            or not self.main.building_requirement(EXTRACTOR, self.main.ready_bases)
            or self.main.already_pending(EXTRACTOR)
            or len(self.main.extractors) >= 7
        ):
            return False

        for geyser in self.main.state.vespene_geyser.closer_than(10, self.main.ready_bases.random):
            self.drone = self.main.select_build_worker(geyser.position)
            if not self.drone:
                return False
            self.geyser = geyser
            if not self.main.extractors and self.main.pools or len(self.main.extractors) < 3 <= self.main.base_amount:
                return True
            return self.main.spires or self.main.hydradens

    async def handle(self):
        """Just finish the action of building the extractor"""
        self.main.add_action(self.drone.build(EXTRACTOR, self.geyser))
        return True
