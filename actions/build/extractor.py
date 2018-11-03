"""Everything related to building logic for the extractors goes here"""
from sc2.constants import EXTRACTOR


class BuildExtractor:
    """Can be improved, the ratio mineral-vespene still sightly off"""

    def __init__(self, ai):
        self.ai = ai
        self.drone = None
        self.geyser = None

    async def should_handle(self, iteration):
        """Couldnt find another way to build the geysers its way to inefficient,
         also the logic can be improved, sometimes it over collect vespene sometime it under collect"""
        local_controller = self.ai
        finished_bases = local_controller.townhalls.ready
        if (local_controller.vespene * 1.25 > local_controller.minerals) or (
            not (finished_bases and local_controller.can_afford(EXTRACTOR))
        ):
            return False

        gas = local_controller.extractors
        gas_amount = len(gas)  # so it calculate just once per step
        vgs = local_controller.state.vespene_geyser.closer_than(10, finished_bases.random)
        extractor_in_queue = local_controller.already_pending(EXTRACTOR)
        for geyser in vgs:
            self.drone = local_controller.select_build_worker(geyser.position)
            if not self.drone:
                return False
            if not extractor_in_queue:
                if not gas and local_controller.pools:
                    self.geyser = geyser
                    return True
                if gas_amount < 3 <= len(local_controller.bases):
                    self.geyser = geyser
                    return True
            if (local_controller.time > 900 or local_controller.spires) and gas_amount < 11:
                self.geyser = geyser
                return True
            if local_controller.hydradens and gas_amount < 5 and not extractor_in_queue:
                self.geyser = geyser
                return True
            if local_controller.pits and gas_amount < 8 and not extractor_in_queue:
                self.geyser = geyser
                return True
        return False

    async def handle(self, iteration):
        """Just finish the action of building the extractor"""
        self.ai.add_action(self.drone.build(EXTRACTOR, self.geyser))
        return True
