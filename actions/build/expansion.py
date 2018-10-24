"""Everything related to the expansion logic goes here"""
from sc2.constants import HATCHERY


class BuildExpansion:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

        self.send_worker = 1
        self.did_send_worker = 2

        self.worker_to_first_base = False
        self.expand_now = False

    async def should_handle(self, iteration):
        """Good for now, maybe the 7th or more hatchery can be postponed
         for when extra mining patches or production are needed """
        local_controller = self.ai
        base = local_controller.townhalls
        base_amount = len(base)  # so it just calculate once per loop
        game_time = local_controller.time
        if not self.worker_to_first_base and base_amount < 2 and local_controller.minerals > 225:
            self.worker_to_first_base = self.send_worker
            return True

        self.expand_now = False

        if (
            base
            and local_controller.can_afford(HATCHERY)
            and not local_controller.close_enemies_to_base
            and (not local_controller.close_enemy_production or game_time > 690)
            and not local_controller.already_pending(HATCHERY)
        ):  # Too many booleans on 1 if statement (separating don't work because it cause another pylint error)

            if not (
                local_controller.known_enemy_structures.closer_than(50, local_controller.start_location)
                and game_time < 300
            ):

                if base_amount <= 4:
                    if base_amount == 2:
                        if game_time > 330 or len(local_controller.zerglings) > 31:
                            self.expand_now = True
                            return True
                    else:
                        # if base_amount == 3:
                        #     await self.build_macrohatch()
                        # else:
                        return True
                elif local_controller.caverns:
                    return True

        return False

    async def handle(self, iteration):
        """Expands to the nearest expansion location using the nearest drone to it"""
        local_controller = self.ai
        action = local_controller.add_action
        if self.worker_to_first_base == self.send_worker:
            action(await self.send_worker_to_next_expansion())
            self.worker_to_first_base = self.did_send_worker
            return True

        if self.expand_now:
            await local_controller.expand_now()
            return True

        for expansion in local_controller.ordered_expansions:
            if await local_controller.can_place(HATCHERY, expansion):
                drone = local_controller.workers.closest_to(expansion)
                action(drone.build(HATCHERY, expansion))
                return True

        return False

    async def send_worker_to_next_expansion(self):
        """Send the worker to the first expansion so its placed faster"""
        local_controller = self.ai
        worker = local_controller.workers.gathering.first
        return worker.move(await local_controller.get_next_expansion())
