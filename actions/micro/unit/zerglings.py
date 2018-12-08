"""Everything related to controlling hydralisks"""
from sc2.constants import BANELING

from actions.micro.micro_helpers import Micro


class ZerglingControl(Micro):
    """Can be improved(Defense not utility)"""

    def micro_zerglings(self, unit, targets):
        """Target low hp units smartly, and surrounds when attack cd is down"""
        if self.baneling_dodge(unit, targets):
            return True
        if self.zergling_modifiers(unit, targets):
            return True
        if self.move_to_next_target(unit, targets):
            return True
        self.controller.add_action(unit.attack(targets.closest_to(unit.position)))
        return True

    def baneling_dodge(self, unit, targets):
        """If the enemy has banelings, run baneling dodging code."""
        local_controller = self.controller
        action = local_controller.add_action
        banelings = self.baneling_group(unit, targets)
        self.handling_anti_banelings_group()
        if local_controller.enemies.of_type(BANELING):
            for baneling in banelings:
                # Check for close banelings
                if baneling.distance_to(unit) < 4:
                    # If we've triggered any banelings
                    if self.baneling_sacrifices:
                        # If we've triggered this specific baneling
                        if baneling in self.baneling_sacrifices.values():
                            # And this zergling is targeting it, attack it
                            if unit in self.baneling_sacrifices and baneling == self.baneling_sacrifices[unit]:
                                action(unit.attack(baneling))
                                return True
                            # Otherwise, run from it.
                            retreat_point = self.find_retreat_point(baneling, unit)
                            action(unit.move(retreat_point))
                            return True
                        # If this baneling is not targeted yet, trigger it.
                        return self.baneling_trigger(unit, baneling)
                    return self.baneling_trigger(unit, baneling)
        return False

    def zergling_modifiers(self, unit, targets):
        """Group modifiers for zerglings"""
        if self.zergling_atk_speed:  # more than half of the attack time with adrenal glands (0.35)
            if unit.weapon_cooldown <= 0.25 * 22.4:  # 22.4 = the game speed times the frames per sec
                return self.attack_close_target(unit, targets)
            return self.move_to_next_target(unit, targets)
        if unit.weapon_cooldown <= 0.35 * 22.4:  # more than half of the attack time with adrenal glands (0.35)
            return self.attack_close_target(unit, targets)
        return False

    def baneling_group(self, unit, targets):
        """Put the banelings on one group"""
        threats = self.trigger_threats(targets, unit, 5)
        # Check for banelings
        for threat in threats:
            if threat.type_id == BANELING:
                yield threat

    def handling_anti_banelings_group(self):
        """If the sacrificial zergling dies before the missions is over remove him from the group"""
        local_controller = self.controller
        for zergling in list(self.baneling_sacrifices):
            if (
                zergling not in local_controller.units()
                or self.baneling_sacrifices[zergling] not in local_controller.enemies
            ):
                del self.baneling_sacrifices[zergling]

    def baneling_trigger(self, unit, baneling):
        """If we haven't triggered any banelings, trigger it."""
        self.baneling_sacrifices[unit] = baneling
        self.controller.add_action(unit.attack(baneling))
        return True
