"""Everything related to the expansion logic goes here"""
from sc2.constants import HATCHERY


class BuildExpansion:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.worker_to_first_base = False

    async def should_handle(self):
        """Good for now, maybe the 7th or more hatchery can be postponed
         for when extra mining patches or production are needed """
        local_controller = self.controller
        base = local_controller.townhalls
        base_amount = len(base)
        game_time = local_controller.time
        if (
            base
            and local_controller.can_afford(HATCHERY)
            and not local_controller.close_enemies_to_base
            and (not local_controller.close_enemy_production or game_time > 690)
        ):
            if not local_controller.already_pending(HATCHERY):
                if not (
                    local_controller.enemy_structures.closer_than(50, local_controller.start_location)
                    and game_time < 300
                ):
                    if base_amount <= 5:
                        return len(local_controller.zerglings) > 19 or game_time >= 285 if base_amount == 2 else True
                    return local_controller.caverns
                return False
            return False
        return False

    async def handle(self):
        """Expands to the nearest expansion location using the nearest drone to it"""
        local_controller = self.controller
        action = local_controller.add_action
        drones = local_controller.drones
        if not self.worker_to_first_base and len(local_controller.townhalls) < 2 and local_controller.minerals > 225:
            self.worker_to_first_base = True
            action(local_controller.drones.random.move(await local_controller.get_next_expansion()))
            return True
        for expansion in local_controller.ordered_expansions:
            if await local_controller.can_place(HATCHERY, expansion):
                enemy_units = local_controller.ground_enemies
                if enemy_units and enemy_units.closer_than(15, expansion):
                    return False
                if drones:
                    action(drones.closest_to(expansion).build(HATCHERY, expansion))
                    return True
        return False
