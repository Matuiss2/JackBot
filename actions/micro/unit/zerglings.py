"""Everything related to controlling zerglings"""
from sc2.constants import BANELING, ZERGLINGATTACKSPEED
from actions.micro.micro_helpers import Micro


class ZerglingControl(Micro):
    """Can be improved in many ways"""

    def baneling_dodge(self, unit, targets):
        """
        Parameters
        ----------
        unit: One zergling from the attacking force
        targets: The enemy zergling targets, it groups almost every enemy unit on the ground

        Returns
        -------
        Chosen action when a baneling is near(attack, move away or pop the baneling)
        """
        """If the enemy has banelings, run baneling dodging code. It can be improved,
         its a little bugged and just avoid the baneling not pop it"""
        self.handling_anti_banelings_group()
        if self.main.enemies.of_type(BANELING):
            banelings = self.baneling_group(unit, targets)
            for baneling in banelings:
                # Check for close banelings and if we've triggered any banelings
                if baneling.distance_to(unit) < 4 and self.baneling_sacrifices:
                    # If we've triggered this specific baneling
                    if baneling in self.baneling_sacrifices.values():
                        # And this zergling is targeting it, attack it
                        if unit in self.baneling_sacrifices and baneling == self.baneling_sacrifices[unit]:
                            self.main.add_action(unit.attack(baneling))
                            return True
                        # Otherwise, run from it.
                        self.main.add_action(unit.move(self.find_retreat_point(baneling, unit)))
                        return True
                    # If this baneling is not targeted yet, trigger it.
                    return self.baneling_trigger(unit, baneling)
                return self.baneling_trigger(unit, baneling)
        return False

    def baneling_group(self, unit, targets):
        """
        Put the banelings on one group
        Parameters
        ----------
        unit: One zergling from the attacking force
        targets: The enemy zergling targets, it groups almost every enemy unit on the ground

        Returns
        -------
        A group that includes every close baneling
        """
        threats = self.trigger_threats(targets, unit, 5)
        for threat in threats:
            if threat.type_id == BANELING:
                yield threat

    def baneling_trigger(self, unit, baneling):
        """
        If we haven't triggered any banelings, trigger it.
        Parameters
        ----------
        unit: One zergling from the attacking force
        baneling: A baneling from the baneling_group

        Returns
        -------
        Action to pop the enemy baneling
        """
        self.baneling_sacrifices[unit] = baneling
        self.main.add_action(unit.attack(baneling))
        return True

    def handling_anti_banelings_group(self):
        """If the sacrificial zergling dies before the missions is over remove him from the group(needs to be fixed)"""
        for zergling in list(self.baneling_sacrifices):
            if zergling not in self.main.units() or self.baneling_sacrifices[zergling] not in self.main.enemies:
                del self.baneling_sacrifices[zergling]

    def micro_zerglings(self, unit, targets):
        """
        Target low hp units smartly, and surrounds when attack cd is down
        Parameters
        ----------
        unit: One zergling from the attacking force
        targets: The enemy zergling targets, it groups almost every enemy unit on the ground

        Returns
        -------
        The chosen action depending on the zergling situation
        """
        if self.baneling_dodge(unit, targets):
            return True
        if self.zergling_modifiers(unit, targets):
            return True
        if self.move_to_next_target(unit, targets):
            return True
        self.main.add_action(unit.attack(targets.closest_to(unit.position)))
        return True

    def zergling_modifiers(self, unit, targets):
        """
        Modifiers for zerglings
        Parameters
        ----------
        unit: One zergling from the attacking force
        targets: The enemy zergling targets, it groups almost every enemy unit on the ground
        Returns
        -------
        The chosen action depending on the modifiers
        """
        if unit.weapon_cooldown <= 8.85 or (
            unit.weapon_cooldown <= 6.35 and self.main.already_pending_upgrade(ZERGLINGATTACKSPEED) == 1
        ):
            return self.attack_close_target(unit, targets)
        return self.move_to_next_target(unit, targets)
