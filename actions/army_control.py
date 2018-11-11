"""Everything related to controlling army units goes here"""
import math
from sc2.constants import (
    ADEPTPHASESHIFT,
    AUTOTURRET,
    BUNKER,
    DISRUPTORPHASED,
    DRONE,
    DUTCHMARAUDERSLOW,
    EGG,
    EVOLVEMUSCULARAUGMENTS,
    INFESTEDTERRAN,
    INFESTEDTERRANSEGG,
    LARVA,
    MUTALISK,
    HYDRALISK,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    PROBE,
    QUEEN,
    SCV,
    SPINECRAWLER,
    ZERGLING,
    ZERGLINGATTACKSPEED,
)
from sc2.position import Point2
from .micro import Micro


def find_pursuit_point(target, unit) -> Point2:
    """Find a point towards the enemy unit"""
    deltax = unit.position.x - target.position.x
    deltay = unit.position.y - target.position.y
    return Point2((unit.position.x + ((deltax / 2) * -1), unit.position.y + ((deltay / 2) * -1)))


def find_retreat_point(target, unit) -> Point2:
    """Find a point away from the enemy unit"""
    deltax = unit.position.x - target.position.x
    deltay = unit.position.y - target.position.y
    return Point2((unit.position.x + (deltax / 2), unit.position.y + (deltay / 2)))


def trigger_threats(targets, unit, trigger_range):
    """Identify threats based on range"""
    threats_list = []
    for enemy in targets:
        if enemy.distance_to(unit) < trigger_range:
            threats_list.append(enemy)
    return threats_list


class ArmyControl(Micro):
    """Can be improved"""

    def __init__(self, ai):
        self.ai = ai
        self.retreat_units = set()
        self.rally_point = None
        self.zergling_atk_speed = False
        self.hydra_move_speed = False

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            local_controller.zerglings
            | local_controller.ultralisks
            | local_controller.mutalisks
            | local_controller.hydras
        )

    async def handle(self, iteration):  # needs further refactoring(too-many-branches)
        """It surrounds and target low hp units, also retreats when overwhelmed,
         it can be improved a lot but is already much better than a-move
        Name army_micro because it is in army.py."""
        local_controller = self.ai
        action = local_controller.add_action
        enemy_building = local_controller.enemy_structures
        map_center = local_controller.game_info.map_center
        bases = local_controller.townhalls
        self.behavior_changing_upgrades_check()
        if bases.ready:
            self.rally_point = bases.ready.closest_to(map_center).position.towards(map_center, 10)
        # enemy_detection = enemy_units.not_structure.of_type({OVERSEER, OBSERVER})
        combined_enemies, targets, atk_force, hydra_targets = self.set_unit_groups()
        for attacking_unit in atk_force:
            if self.dodge_effects(attacking_unit):
                continue
            unit_position = attacking_unit.position
            attack_command = attacking_unit.attack
            if self.anti_proxy_trigger(attacking_unit):
                if self.attack_enemy_proxy_units(targets, attacking_unit):
                    continue
                else:
                    action(attacking_unit.move(local_controller.spines.closest_to(attacking_unit)))
                    continue
            if self.anti_terran_bm(attacking_unit):
                continue
            if attacking_unit.tag in self.retreat_units and bases:
                self.has_retreated(attacking_unit)
                continue
            if attacking_unit.type_id == HYDRALISK and hydra_targets and hydra_targets.closer_than(17, unit_position):
                if self.retreat_unit(attacking_unit, combined_enemies):
                    continue
                if self.micro_hydras(hydra_targets, attacking_unit):
                    continue
            if targets and targets.closer_than(17, unit_position):
                if self.retreat_unit(attacking_unit, combined_enemies):
                    continue
                if await self.handling_walls_and_attacking(attacking_unit, targets):
                    continue
            elif enemy_building.closer_than(30, unit_position):
                action(attack_command(enemy_building.closest_to(unit_position)))
                continue
            elif local_controller.time < 1000 and not local_controller.close_enemies_to_base:
                self.idle_unit(attacking_unit)
                continue
            else:
                if self.keep_attacking(attacking_unit, targets):
                    continue
                elif bases:
                    self.move_to_rallying_point(attacking_unit)

    def move_to_rallying_point(self, unit):
        """Set the point where the units should gather"""
        if unit.position.distance_to_point2(self.rally_point) > 5:
            self.ai.add_action(unit.move(self.rally_point))

    def has_retreated(self, unit):
        """Identify if the unit has retreated"""
        if self.ai.townhalls.closer_than(15, unit.position):
            self.retreat_units.remove(unit.tag)

    def retreat_unit(self, unit, combined_enemies):
        """Tell the unit to retreat when overwhelmed"""
        local_controller = self.ai
        if (
            local_controller.townhalls
            and not local_controller.close_enemies_to_base
            and not local_controller.structures.closer_than(7, unit.position)
            and len(combined_enemies.closer_than(20, unit.position))
            >= len(local_controller.zerglings.closer_than(13, unit.position))
            + len(local_controller.ultralisks.closer_than(13, unit.position)) * 8
            + len(local_controller.hydras.closer_than(13, unit.position)) * 3
        ):
            self.move_to_rallying_point(unit)
            self.retreat_units.add(unit.tag)
            return True
        return False

    def micro_zerglings(self, targets, unit):
        """Target low hp units smartly, and surrounds when attack cd is down"""
        if self.zergling_atk_speed:  # more than half of the attack time with adrenal glands (0.35)
            if unit.weapon_cooldown <= 0.25 * 22.4:  # 22.4 = the game speed times the frames per sec
                return self.attack_close_target(unit, targets)
            return self.move_to_next_target(unit, targets)
        if unit.weapon_cooldown <= 0.35 * 22.4:  # more than half of the attack time with adrenal glands (0.35)
            return self.attack_close_target(unit, targets)
        if self.move_to_next_target(unit, targets):
            return True
        self.ai.add_action(unit.attack(targets.closest_to(unit.position)))
        return True

    def micro_hydras(self, targets, unit):
        """Control the hydras"""
        our_movespeed = unit.movement_speed
        # If we've researched Muscular Augments, our movespeed is 125% of base.
        if self.hydra_move_speed:
            our_movespeed *= 1.25
        # If we're on creep, it's 30% more.
        if self.ai.has_creep(unit):
            our_movespeed *= 1.30
        # If we've been hit with Marauder's Concussive Shells, our movespeed is half.
        if unit.has_buff(DUTCHMARAUDERSLOW):
            our_movespeed *= 0.5
        threats = trigger_threats(targets, unit, 10)
        if threats:
            # Find the closest threat.
            closest_threat = None
            closest_threat_distance = math.inf
            for threat in threats:
                if threat.distance_to(unit) < closest_threat_distance and threat.ground_dps:
                    closest_threat = threat
                    closest_threat_distance = threat.distance_to(unit)
            # If there's a close enemy that does damage,
            if closest_threat:
                our_range = unit.ground_range + unit.radius
                enemy_range = closest_threat.ground_range + closest_threat.radius
                # For flying enemies,
                if closest_threat.is_flying:
                    our_range = unit.air_range + unit.radius
                    # Hit and run if we can.
                    if our_range > enemy_range and our_movespeed > closest_threat.movement_speed:
                        return self.hit_and_run(closest_threat, unit)
                    return self.stutter_step(closest_threat, unit)
                # For ground enemies hit and run if we can.
                if our_range > enemy_range and our_movespeed > closest_threat.movement_speed:
                    return self.hit_and_run(closest_threat, unit)
                return self.stutter_step(closest_threat, unit)
            # If there isn't a close enemy that does damage,
            return self.attack_close_target(unit, targets)
        # If enemies aren't that near.
        return self.attack_close_target(unit, targets)

    def hit_and_run(self, target, unit):
        """Attack when the unit can, run while it can't. We outrun the enemy."""
        # Only do this when our range > enemy range, our movespeed > enemy movespeed, and enemy is targeting us.
        local_controller = self.ai
        action = local_controller.add_action
        unit_is_air = unit.is_flying
        target_is_air = target.is_flying
        if target_is_air:
            our_range = unit.air_range + unit.radius
        else:
            our_range = unit.ground_range + unit.radius
        if unit_is_air:
            enemy_range = target.air_range + target.radius
        else:
            enemy_range = target.ground_range + target.radius
        # Our unit should stay just outside enemy range, and inside our range.
        if enemy_range > 1:
            minimum_distance = enemy_range + unit.radius + 0.1
            maximum_distance = our_range
        else:
            minimum_distance = our_range - unit.radius
            maximum_distance = our_range
        # If our unit is in that range, attack.
        if minimum_distance <= unit.distance_to(target) <= maximum_distance:
            action(unit.attack(target))
            return True
        # If our unit is too close, run away.
        if unit.distance_to(target) < minimum_distance:
            retreat_point = find_retreat_point(target, unit)
            action(unit.move(retreat_point))
            return True
        # If our unit is too far, run towards.
        pursuit_point = find_pursuit_point(target, unit)
        action(unit.move(pursuit_point))
        return True

    def stutter_step(self, target, unit):
        """Attack when the unit can, run while it can't. We don't outrun the enemy."""
        local_controller = self.ai
        action = local_controller.add_action
        if not unit.weapon_cooldown:
            action(unit.attack(target))
            return True
        retreat_point = find_retreat_point(target, unit)
        action(unit.move(retreat_point))
        return True

    def idle_unit(self, unit):
        """Control the idle units, by gathering then or telling then to attack"""
        local_controller = self.ai
        if (
            len(local_controller.ultralisks.ready) < 4
            and local_controller.supply_used not in range(198, 201)
            and len(local_controller.zerglings.ready) + len(local_controller.hydras) * 2 < 41
            and local_controller.townhalls
            and self.retreat_units
        ):
            if not local_controller.counter_attack_vs_flying:
                self.move_to_rallying_point(unit)
                return True
        if not local_controller.close_enemy_production or local_controller.time >= 480:
            enemy_building = local_controller.enemy_structures
            if enemy_building and local_controller.townhalls:
                self.attack_closest_building(unit)
            else:
                self.attack_startlocation(unit)
        return False

    def attack_closest_building(self, unit):
        """Attack the starting location"""
        local_controller = self.ai
        enemy_building = local_controller.enemy_structures.not_flying
        if enemy_building:
            local_controller.add_action(
                unit.attack(enemy_building.closest_to(local_controller.furthest_townhall_to_map_center))
            )

    def attack_startlocation(self, unit):
        """It tell to attack the starting location"""
        local_controller = self.ai
        if local_controller.enemy_start_locations:
            local_controller.add_action(unit.attack(local_controller.enemy_start_locations[0]))

    def anti_proxy_trigger(self, unit):
        """It triggers the anti-proxy logic"""
        local_controller = self.ai
        spines = local_controller.spines
        return (
            local_controller.close_enemy_production
            and spines
            and not spines.closer_than(2, unit)
            and (local_controller.time <= 480 or len(local_controller.zerglings) <= 14)
        )

    def attack_enemy_proxy_units(self, targets, unit):
        """Attack the proxy army if it get too close to the ramp"""
        return (
            targets
            and targets.closer_than(5, unit)
            and unit.type_id == ZERGLING
            and self.micro_zerglings(targets, unit)
        )

    def set_unit_groups(self):
        """Set the targets, combined_enemies and atk_force"""
        targets = None
        hydra_targets = None
        combined_enemies = None
        local_controller = self.ai
        enemy_units = local_controller.enemies
        enemy_building = local_controller.enemy_structures
        if enemy_units:
            excluded_units = {
                ADEPTPHASESHIFT,
                DISRUPTORPHASED,
                EGG,
                LARVA,
                INFESTEDTERRANSEGG,
                INFESTEDTERRAN,
                AUTOTURRET,
            }
            filtered_enemies = enemy_units.not_structure.exclude_type(excluded_units)
            static_defence = enemy_building.of_type({SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS})
            combined_enemies = filtered_enemies.exclude_type({DRONE, SCV, PROBE}) | static_defence
            targets = static_defence | filtered_enemies.not_flying
            hydra_targets = static_defence | filtered_enemies
        atk_force = (
            local_controller.zerglings
            | local_controller.ultralisks
            | local_controller.mutalisks
            | local_controller.hydras
        )
        if local_controller.floating_buildings_bm and local_controller.supply_used >= 199:
            atk_force = atk_force | local_controller.queens
        return combined_enemies, targets, atk_force, hydra_targets

    def anti_terran_bm(self, unit):
        """Logic for countering the floating buildings bm"""
        local_controller = self.ai
        enemy_building = local_controller.enemy_structures
        flying_buildings = enemy_building.flying
        if unit.type_id in (MUTALISK, QUEEN, HYDRALISK) and flying_buildings:
            local_controller.add_action(unit.attack(flying_buildings.closest_to(unit.position)))
            return True
        return False

    async def handling_walls_and_attacking(self, unit, target):
        """It micros normally if no wall, if there is one attack it"""
        local_controller = self.ai
        unit_position = unit.position
        closest_target = target.closest_to
        attack_command = unit.attack
        action = local_controller.add_action
        if await local_controller.client.query_pathing(unit, closest_target(unit).position):
            if unit.type_id == ZERGLING:
                return self.micro_zerglings(target, unit)
            action(attack_command(closest_target(unit_position)))
            return True
        action(attack_command(local_controller.enemies.not_flying.closest_to(unit_position)))
        return True

    def keep_attacking(self, unit, target):
        """It keeps the attack going if it meets the requirements no matter what"""
        local_controller = self.ai
        unit_position = unit.position
        attack_command = unit.attack
        action = local_controller.add_action
        enemy_building = local_controller.enemy_structures
        if not self.retreat_units or local_controller.close_enemies_to_base or local_controller.time >= 1000:
            if enemy_building:
                action(attack_command(enemy_building.closest_to(unit_position)))
                return True
            if target:
                action(attack_command(target.closest_to(unit_position)))
                return True
            self.attack_startlocation(unit)
            return True
        return False

    def behavior_changing_upgrades_check(self):
        """Check for upgrades the will change how the units behavior are calculated"""
        local_controller = self.ai
        if not self.zergling_atk_speed and local_controller.hives:
            self.zergling_atk_speed = local_controller.already_pending_upgrade(ZERGLINGATTACKSPEED) == 1
        if not self.hydra_move_speed and local_controller.hydradens:
            self.hydra_move_speed = local_controller.already_pending_upgrade(EVOLVEMUSCULARAUGMENTS) == 1
