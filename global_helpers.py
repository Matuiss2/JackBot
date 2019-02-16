"""Every helper for the bot goes here"""
from sc2.constants import HIVE


class Globals:
    """Global wrappers"""

    def can_train(self, unit_type, requirement=True, larva=True):
        """Global requirements for creating an unit"""
        if self.hives and not self.caverns:
            return False
        if self.pits.ready and not self.hives and not self.already_pending(HIVE, all_units=True):
            return False
        return (not larva or self.larvae) and self.can_afford(unit_type) and requirement

    def can_build_unique(self, unit_type, building, requirement=True, all_units=False):
        """Global requirements for building unique buildings"""
        return (
            self.can_afford(unit_type)
            and not building
            and self.building_requirement(unit_type, requirement, one_at_time=True, morphing=all_units)
        )

    async def place_building(self, building):
        """Build it behind the mineral line if there is space"""
        position = await self.get_production_position()
        if not position:
            print("wanted position unavailable")
            return None
        selected_drone = self.select_build_worker(position)
        if selected_drone:
            self.add_action(selected_drone.build(building, position))

    def can_upgrade(self, upgrade, research, host_building):
        """Global requirements for upgrades"""
        return not self.already_pending_upgrade(upgrade) and self.can_afford(research) and host_building

    def building_requirement(self, unit_type, requirement=True, one_at_time=False, morphing=False):
        """Global requirements for building every structure"""
        if one_at_time and self.already_pending(unit_type, all_units=morphing):
            return False
        return requirement and self.can_afford(unit_type)
