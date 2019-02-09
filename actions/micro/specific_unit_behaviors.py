"""Everything related to units behavior changers goes here"""
from sc2.constants import HYDRALISK
from actions.micro.micro_helpers import Micro
from actions.micro.unit.hydralisks import HydraControl


class UnitsBehavior(HydraControl, Micro):
    """Ok for now"""

    def specific_hydra_behavior(self, hydra_targets, unit):
        """Group everything related to hydras behavior on attack"""
        if hydra_targets:
            close_hydra_targets = hydra_targets.closer_than(20, unit.position)
            if unit.type_id == HYDRALISK and close_hydra_targets:
                if self.retreat_unit(unit, close_hydra_targets):
                    return True
                if self.micro_hydras(hydra_targets, unit):
                    return True
        return False

    async def specific_zergling_behavior(self, targets, unit):
        """Group everything related to zergling behavior on attack"""
        if targets:
            close_targets = targets.closer_than(20, unit.position)
            if close_targets:
                if self.retreat_unit(unit, close_targets):
                    return True
                if await self.handling_walls_and_attacking(unit, close_targets):
                    return True
        return False
