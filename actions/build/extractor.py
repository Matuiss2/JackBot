from sc2.constants import EXTRACTOR


class BuildExtractor:
    def __init__(self, ai):
        self.ai = ai
        self.drone = None
        self.geyser = None

    async def should_handle(self, iteration):
        """Couldnt find another way to build the geysers its way to inefficient,
         also the logic can be improved, sometimes it over collect vespene sometime it under collect"""
        if self.ai.vespene * 1.5 > self.ai.minerals:
            return False
        if not (self.ai.townhalls.ready and self.ai.can_afford(EXTRACTOR)):
            return False

        gas = self.ai.extractors
        gas_amount = len(gas)  # so it calculate just once per step
        vgs = self.ai.state.vespene_geyser.closer_than(10, self.ai.townhalls.ready.random)
        for geyser in vgs:
            self.drone = self.ai.select_build_worker(geyser.position)
            if not self.drone:
                return False
            if not self.ai.already_pending(EXTRACTOR):
                if not gas and self.ai.pools:
                    self.geyser = geyser
                    return True
            if self.ai.time > 960 and gas_amount < 10:
                self.geyser = geyser
                return True
            pit = self.ai.pits
            if pit and gas_amount < 7 and not self.ai.already_pending(EXTRACTOR):
                self.geyser = geyser
                return True
        return False

    async def handle(self, iteration):
        self.ai.actions.append(self.drone.build(EXTRACTOR, self.geyser))
        return True
