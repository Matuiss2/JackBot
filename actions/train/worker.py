from sc2.constants import DRONE, OVERLORD


class TrainWorker:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Should this action be handled"""
        workers_total = len(self.ai.workers)
        geysirs = self.ai.extractors

        if not self.ai.close_enemies_to_base and self.ai.can_train(DRONE):
            if workers_total == 12 and not self.ai.already_pending(DRONE) and self.ai.time < 200:
                return True
            if workers_total in (13, 14, 15) and len(self.ai.overlords) + self.ai.already_pending(OVERLORD) > 1:
                if workers_total == 15 and geysirs and self.ai.pools and self.ai.time < 250:
                    return True
                return True
            optimal_workers = min(sum([x.ideal_harvesters for x in self.ai.townhalls | geysirs]), 98 - len(geysirs))
            if workers_total + self.ai.already_pending(DRONE) < optimal_workers and len(self.ai.zerglings) > 13:
                return True
        return False

    async def handle(self, iteration):
        self.ai.actions.append(self.ai.larvae.random.train(DRONE))
        return True
