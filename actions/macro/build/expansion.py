"""Everything related to the expansion logic goes here"""
from sc2.constants import HATCHERY


class BuildExpansion:
    """Can be improved"""

    def __init__(self, main):
        self.main = main
        self.worker_to_first_base = False

    async def should_handle(self):
        """Fourth base sometimes are not build at the expected time maybe reduce the lock for it,
         also maybe the 7th or more hatchery can be postponed for when extra mining patches or production are needed """
        base = self.main.townhalls
        game_time = self.main.time
        if (
            base
            and self.main.can_afford(HATCHERY)
            and not self.main.close_enemies_to_base
            and (not self.main.close_enemy_production or game_time > 690)
        ):
            hatcheries_in_progress = self.main.already_pending(HATCHERY)
            if (
                self.main.minerals >= 1250
                and hatcheries_in_progress < 2
                and self.main.base_amount + hatcheries_in_progress < len(self.main.expansion_locations)
                and self.main.base_amount > 5
            ):
                return True
            if not hatcheries_in_progress:
                if self.main.base_amount <= 5:
                    if self.main.base_amount == 4:
                        return self.main.hydra_amount > 9
                    return self.main.zergling_amount > 17 or game_time >= 285 if self.main.base_amount == 2 else True
                return self.main.caverns
            return False
        return False

    async def handle(self):
        """Expands to the nearest expansion location using the nearest drone to it"""
        action = self.main.add_action
        if not self.worker_to_first_base and self.main.base_amount < 2 and self.main.minerals > 225:
            self.worker_to_first_base = True
            action(self.main.drones.random.move(await self.main.get_next_expansion()))
            return True
        drones = self.main.drones
        for expansion in self.main.ordered_expansions:
            if await self.main.can_place(HATCHERY, expansion):
                enemy_units = self.main.ground_enemies
                if enemy_units and enemy_units.closer_than(15, expansion):
                    return False
                if drones:
                    action(drones.closest_to(expansion).build(HATCHERY, expansion))
                    return True
        return False
