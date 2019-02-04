"""Everything related to the expansion logic goes here"""
from sc2.constants import HATCHERY


class BuildExpansion:
    """Can be improved"""

    def __init__(self, main):
        self.controller = main
        self.worker_to_first_base = False
        self.base_amount = None

    async def should_handle(self):
        """Fourth base sometimes are not build at the expected time maybe reduce the lock for it,
         also maybe the 7th or more hatchery can be postponed for when extra mining patches or production are needed """
        base = self.controller.townhalls
        self.base_amount = len(base)
        game_time = self.controller.time

        if (
            base
            and self.controller.can_afford(HATCHERY)
            and not self.controller.close_enemies_to_base
            and (not self.controller.close_enemy_production or game_time > 690)
        ):
            hatcheries_in_progress = self.controller.already_pending(HATCHERY)
            if (
                self.controller.minerals >= 1250
                and hatcheries_in_progress < 2
                and self.base_amount + hatcheries_in_progress < len(self.controller.expansion_locations)
                and self.base_amount > 5
            ):
                return True
            if not hatcheries_in_progress:
                if self.base_amount <= 5:
                    if self.base_amount == 4:
                        return len(self.controller.hydras) > 7
                    return len(self.controller.zerglings) > 21 or game_time >= 285 if self.base_amount == 2 else True
                return self.controller.caverns
            return False
        return False

    async def handle(self):
        """Expands to the nearest expansion location using the nearest drone to it"""
        action = self.controller.add_action
        if not self.worker_to_first_base and self.base_amount < 2 and self.controller.minerals > 225:
            self.worker_to_first_base = True
            action(self.controller.drones.random.move(await self.controller.get_next_expansion()))
            return True
        for expansion in self.controller.ordered_expansions:
            if await self.controller.can_place(HATCHERY, expansion):
                enemy_units = self.controller.ground_enemies
                if enemy_units and enemy_units.closer_than(15, expansion):
                    return False
                drones = self.controller.drones
                if drones:
                    action(drones.closest_to(expansion).build(HATCHERY, expansion))
                    return True
        return False
