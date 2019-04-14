"""Everything related to controlling hydralisks"""
import math
from sc2.constants import BuffId
from actions.micro.micro_helpers import Micro


class HydraControl(Micro):
    """Some mistakes mostly due to values I believe, can be improved"""

    def hydra_modifiers(self, unit):
        """
        Modifiers for hydras
        Parameters
        ----------
        unit: One hydra from the attacking force

        Returns
        -------
        The speed and range of the hydras after the modifiers
        """
        our_move_speed = unit.movement_speed
        our_range = unit.ground_range + unit.radius
        if self.main.hydra_range:  # If we've researched grooved spines, hydras gets 1 more range.
            our_range += 1
        if self.main.hydra_speed:  # If we've researched muscular augments, our move speed is 25% more.
            our_move_speed *= 1.25
        if self.main.has_creep(unit):
            our_move_speed *= 1.30  # If we're on creep, it's 30% more.
        if unit.has_buff(BuffId.SLOW):
            our_move_speed *= 0.5  # If we've been hit with concussive shells, our move speed is half.
        if unit.has_buff(BuffId.FUNGALGROWTH):
            our_move_speed *= 0.25  # If we've been hit with fungal growth, our move speed is a quarter.
        # movement_speed returns the speed on normal speed not fastest so x 1.4 is necessary
        return our_move_speed * 1.4, our_range

    def micro_hydras(self, targets, unit):
        """
        Control the hydras
        Parameters
        ----------
        targets: The enemy hydra targets, it groups almost every enemy unit
        unit: One hydra from the attacking force

        Returns
        -------
        Choose which action is better for which situation(hit and run, stutter_step or attacking the closest target)
        """
        our_move_speed, our_range = self.hydra_modifiers(unit)
        closest_threat = None  # Find the closest threat.
        closest_threat_distance = math.inf
        for threat in self.trigger_threats(targets, unit, 14):
            if threat.distance_to(unit) < closest_threat_distance:
                closest_threat = threat
                closest_threat_distance = threat.distance_to(unit)
        if closest_threat:
            enemy_range = closest_threat.ground_range
            if not enemy_range:
                enemy_range = 0
            if our_range > enemy_range + closest_threat.radius and our_move_speed > closest_threat.movement_speed * 1.4:
                return self.hit_and_run(closest_threat, unit, 6.45, 3.35)
            return self.stutter_step(closest_threat, unit)
        return self.attack_close_target(unit, targets)  # If there isn't a close enemy that does damage
