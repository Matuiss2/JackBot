"""Everything related to units behavior changers goes here"""
from sc2.constants import UnitTypeId
from actions.micro.micro_helpers import MicroHelpers
from actions.micro.unit.hydralisk_control import HydraControl


class SpecificUnitsBehaviors(HydraControl, MicroHelpers):
    """Ok for now"""

    def specific_hydra_behavior(self, hydra_targets, unit):
        """
        Group everything related to hydras behavior on attack
        Parameters
        ----------
        hydra_targets: Targets that hydras can reach(almost everything)
        unit: One hydra from the attacking force

        Returns
        -------
        Actions(micro or retreat) if conditions are met False if not
        """
        if hydra_targets and unit.type_id == UnitTypeId.HYDRALISK:
            close_hydra_targets = hydra_targets.closer_than(15, unit.position)
            if close_hydra_targets:
                if self.retreat_unit(unit, close_hydra_targets):
                    return True
                if self.microing_hydras(hydra_targets, unit):
                    return True
        return False

    async def specific_zergling_behavior(self, targets, unit):
        """
        Group everything related to zergling behavior on attack
        Parameters
        ----------
        targets: Targets that zerglings can reach(ground units mostly)
        unit: One zergling from the attacking force

        Returns
        -------
        Actions(micro or retreat) if conditions are met False if not
        """
        if targets:
            close_targets = targets.closer_than(15, unit.position)
            if close_targets:
                if self.retreat_unit(unit, close_targets):
                    return True
                if await self.handling_walls_and_attacking(unit, close_targets):
                    return True
        return False
