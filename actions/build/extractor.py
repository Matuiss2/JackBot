"""Everything related to building logic for the extractors goes here"""
from sc2.constants import EXTRACTOR


class BuildExtractor:
    """Can be improved, the ratio mineral-vespene still sightly off"""

    def __init__(self, ai):
        self.controller = ai
        self.drone = None
        self.geyser = None

    async def should_handle(self):
        """Couldn't find another way to build the geysers its way to inefficient,
         still trying to find the optimal number"""
        local_controller = self.controller
        finished_bases = local_controller.townhalls.ready
        if (local_controller.vespene * 1.25 > local_controller.minerals) or (
            not local_controller.building_requirement(EXTRACTOR, finished_bases)
        ):
            return False
        gas = local_controller.extractors
        gas_amount = len(gas)
        for geyser in local_controller.state.vespene_geyser.closer_than(10, finished_bases.random):
            self.drone = local_controller.select_build_worker(geyser.position)
            if not self.drone or local_controller.already_pending(EXTRACTOR) or gas_amount > 10:
                return False
            self.geyser = geyser
            if (not gas and local_controller.pools) or gas_amount < 3 <= len(local_controller.townhalls):
                return True
            return (local_controller.time > 900 or local_controller.spires) or (
                local_controller.hydradens and gas_amount < 7
            )

    async def handle(self):
        """Just finish the action of building the extractor"""
        self.controller.add_action(self.drone.build(EXTRACTOR, self.geyser))
        return True
