"""Everything related to controlling hydralisks"""
import math
from sc2.constants import DUTCHMARAUDERSLOW
from actions.micro.micro_helpers import Micro


class HydraControl(Micro):
    """Can be improved(Defense not utility)"""

    def micro_hydras(self, targets, unit):
        """Control the hydras"""
        our_movespeed, our_range = self.hydra_modifiers(unit)
        threats = self.trigger_threats(targets, unit, 17)
        # Find the closest threat.
        closest_threat = None
        closest_threat_distance = math.inf
        for threat in threats:
            if threat.distance_to(unit) < closest_threat_distance:
                closest_threat = threat
                closest_threat_distance = threat.distance_to(unit)
        # If there's a close enemy that does damage,
        if closest_threat:
            # Hit and run if we can.
            enemy_range = closest_threat.ground_range
            if not enemy_range:
                enemy_range = 0
            if our_range > enemy_range + closest_threat.radius and our_movespeed > closest_threat.movement_speed:
                return self.hit_and_run(closest_threat, unit, self.hydra_atk_range)
            return self.stutter_step(closest_threat, unit)
        # If there isn't a close enemy that does damage,
        return self.attack_close_target(unit, targets)

    def hydra_modifiers(self, unit):
        """Group modifiers for hydras"""
        our_movespeed = unit.movement_speed
        our_range = unit.ground_range + unit.radius
        if self.hydra_atk_range:
            our_range += 1
        # If we've researched Muscular Augments, our movespeed is 125% of base.
        if self.hydra_move_speed:
            our_movespeed *= 1.25
        # If we're on creep, it's 30% more.
        if self.controller.has_creep(unit):
            our_movespeed *= 1.30
        # If we've been hit with Marauder's Concussive Shells, our movespeed is half.
        if unit.has_buff(DUTCHMARAUDERSLOW):
            our_movespeed *= 0.5
        return our_movespeed, our_range
