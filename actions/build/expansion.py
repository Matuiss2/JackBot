from sc2.constants import HATCHERY


class BuildExpansion:
    def __init__(self, ai):
        self.ai = ai

        self.send_worker = 1
        self.did_send_worker = 2

        self.worker_to_first_base = False
        self.expand_now = False

    async def should_handle(self, iteration):
        """Good for now, maybe the 7th or more hatchery can be postponed
         for when extra mining patches or production are needed """
        base_amount = len(self.ai.townhalls)  # so it just calculate once per loop
        if not self.worker_to_first_base and base_amount < 2 and self.ai.minerals > 225:
            self.worker_to_first_base = self.send_worker
            return True

        self.expand_now = False

        if (
            self.ai.townhalls
            and self.ai.can_afford(HATCHERY)
            and not self.ai.close_enemies_to_base
            and not self.ai.close_enemy_production
            and not self.ai.already_pending(HATCHERY)
            and not (self.ai.known_enemy_structures.closer_than(50, self.ai.start_location) and self.ai.time < 300)
        ):

            if base_amount <= 4:
                if base_amount == 2:
                    if self.ai.time > 330 or len(self.ai.zerglings) > 31:
                        self.expand_now = True
                        return True
                else:
                    # if base_amount == 3:
                    #     await self.build_macrohatch()
                    # else:
                    return True
            elif self.ai.caverns:
                return True

        return False

    async def handle(self, iteration):
        if self.worker_to_first_base == self.send_worker:
            self.ai.actions.append(await self.send_worker_to_next_expansion())
            self.worker_to_first_base = self.did_send_worker
            return True

        if self.expand_now:
            await self.ai.expand_now()
            return True

        for expansion in self.ai.ordered_expansions:
            if await self.ai.can_place(HATCHERY, expansion):
                drone = self.ai.workers.closest_to(expansion)
                self.ai.actions.append(drone.build(HATCHERY, expansion))
                return True

        return False

    async def send_worker_to_next_expansion(self):
        worker = self.ai.workers.gathering.first
        return worker.move(await self.ai.get_next_expansion())
