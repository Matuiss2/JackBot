"""Everything related to controlling hydralisks"""
import math
from sc2.constants import EVOLVEGROOVEDSPINES, EVOLVEMUSCULARAUGMENTS, FUNGALGROWTH, SLOW
from actions.micro.micro_helpers import Micro


class HydraControl(Micro):
    """Some mistakes mostly due to values I believe, can be improved"""

    def micro_hydras(self, targets, unit):
        """Control the hydras"""
        our_move_speed, our_range = self.hydra_modifiers(unit)
        threats = self.trigger_threats(targets, unit, 14)
        closest_threat = None  # Find the closest threat.
        closest_threat_distance = math.inf
        for threat in threats:
            if threat.distance_to(unit) < closest_threat_distance:
                closest_threat = threat
                closest_threat_distance = threat.distance_to(unit)
        if closest_threat:
            enemy_range = closest_threat.ground_range
            if not enemy_range:
                enemy_range = 0
            if our_range > enemy_range + closest_threat.radius and our_move_speed > closest_threat.movement_speed:
                return self.hit_and_run(closest_threat, unit, our_range)
            return self.stutter_step(closest_threat, unit)
        return self.attack_close_target(unit, targets)  # If there isn't a close enemy that does damage

    def hydra_modifiers(self, unit):
        """Modifiers for hydras"""
        our_move_speed = unit.movement_speed
        our_range = unit.ground_range + unit.radius
        if self.main.already_pending_upgrade(EVOLVEGROOVEDSPINES) == 1:
            our_range += 1  # If we've researched grooved spines, hydras gets 1 more range.
        if self.main.already_pending_upgrade(EVOLVEMUSCULARAUGMENTS) == 1:
            our_move_speed *= 1.25  # If we've researched muscular augments, our move speed is 25% more.
        if self.main.has_creep(unit):
            our_move_speed *= 1.30  # If we're on creep, it's 30% more.
        if unit.has_buff(SLOW):
            our_move_speed *= 0.5  # If we've been hit with concussive shells, our move speed is half.
        if unit.has_buff(FUNGALGROWTH):
            our_move_speed *= 0.25  # If we've been hit with fungal growth, our move speed is a quarter.
        return our_move_speed, our_range
