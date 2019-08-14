"""Everything related to building logic for the spores goes here"""
from sc2.constants import UnitTypeId


class SporeConstruction:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements build the spores"""
        spore_building_trigger = (
            self.main.flying_enemies
            and not (len(self.main.spores) > self.main.ready_base_amount or self.main.close_enemies_to_base)
            and (au for au in self.main.flying_enemies if au.can_attack_ground)
        )
        if self.main.ready_bases:
            return (
                (spore_building_trigger or self.main.time >= 420)
                and not self.main.already_pending(UnitTypeId.SPORECRAWLER)
                and self.main.building_requirement(UnitTypeId.SPORECRAWLER, self.main.settled_pool)
            )

    async def handle(self):
        """Build the spore right on the middle of the base"""
        for base in self.main.ready_bases:
            spore_position = self.main.state.resources.closer_than(10, base).center.towards(base, 1)
            selected_drone = self.main.select_build_worker(spore_position)
            if (
                not self.main.ground_enemies.closer_than(20, spore_position)
                and selected_drone
                and not self.main.spores.closer_than(15, spore_position)
            ):
                self.main.add_action(selected_drone.build(UnitTypeId.SPORECRAWLER, spore_position))
