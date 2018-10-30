"""Everything related to controlling army units goes here"""
from sc2.constants import (
    ADEPTPHASESHIFT,
    AUTOTURRET,
    BUNKER,
    DISRUPTORPHASED,
    DRONE,
    EGG,
    INFESTEDTERRAN,
    INFESTEDTERRANSEGG,
    LARVA,
    MUTALISK,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    PROBE,
    QUEEN,
    SCV,
    SPINECRAWLER,
    ZERGLING,
    ZERGLINGATTACKSPEED,
)

from .micro import Micro


class ArmyControl(Micro):
    """Can be improved"""

    def __init__(self, ai):
        self.ai = ai
        self.retreat_units = set()
        self.rally_point = None
        self.zergling_atk_speed = False

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return local_controller.zerglings | local_controller.ultralisks | local_controller.mutalisks

    async def handle(self, iteration):  # needs further refactoring(too-many-branches, too-many-statements)
        """It surrounds and target low hp units, also retreats when overwhelmed,
         it can be improved a lot but is already much better than a-move
        Name army_micro because it is in army.py."""
        local_controller = self.ai
        action = local_controller.add_action
        enemy_building = local_controller.enemy_structures
        map_center = local_controller.game_info.map_center
        bases = local_controller.townhalls
        close_enemies_to_base = local_controller.close_enemies_to_base
        closest_enemy_building = enemy_building.closest_to
        game_time = local_controller.time
        if not self.zergling_atk_speed and local_controller.hives:
            self.zergling_atk_speed = local_controller.already_pending_upgrade(ZERGLINGATTACKSPEED) == 1
        if bases:
            self.rally_point = bases.closest_to(map_center).position.towards(map_center, 10)
        # enemy_detection = enemy_units.not_structure.of_type({OVERSEER, OBSERVER})
        combined_enemies, targets, atk_force = self.set_unit_groups()
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
            if targets and targets.closer_than(17, unit_position):
                if self.retreat_unit(attacking_unit, combined_enemies):
                    continue
                if await self.handling_walls_and_attacking(attacking_unit, targets):
                    continue
            elif enemy_building.closer_than(30, unit_position):
                action(attack_command(closest_enemy_building(unit_position)))
                continue
            elif game_time < 1000 and not close_enemies_to_base:
                self.idle_unit(attacking_unit)
                continue
            else:
                if not self.retreat_units or close_enemies_to_base or game_time >= 1000:
                    if enemy_building:
                        action(attack_command(closest_enemy_building(unit_position)))
                        continue
                    elif targets:
                        action(attack_command(targets.closest_to(unit_position)))
                        continue
                    else:
                        self.attack_startlocation(attacking_unit)
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
            + len(local_controller.ultralisks.closer_than(13, unit.position)) * 6
        ):
            self.move_to_rallying_point(unit)
            self.retreat_units.add(unit.tag)
            return True
        return False

    def micro_zerglings(self, targets, unit):
        """Target low hp units smartly, and surrounds when attack cd is down"""
        if self.zergling_atk_speed:  # more than half of the attack time with adrenal glands (0.35)
            if unit.weapon_cooldown <= 0.25 * 22.4:  # 22.4 = the game speed times the frames per sec
                if self.attack_close_target(unit, targets):
                    return True
            else:
                if self.move_to_next_target(unit, targets):
                    return True
        elif unit.weapon_cooldown <= 0.35 * 22.4:  # more than half of the attack time with adrenal glands (0.35)
            if self.attack_close_target(unit, targets):
                return True
        else:
            if self.move_to_next_target(unit, targets):
                return True

        self.ai.add_action(unit.attack(targets.closest_to(unit.position)))
        return True

    def idle_unit(self, unit):
        """Control the idle units, by gathering then or telling then to attack"""
        local_controller = self.ai
        if (
            len(local_controller.ultralisks.ready) < 4
            and local_controller.supply_used not in range(198, 201)
            and len(local_controller.zerglings.ready) < 41
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
        combined_enemies = None
        local_controller = self.ai
        enemy_units = local_controller.known_enemy_units
        enemy_building = local_controller.enemy_structures
        zerglings = local_controller.zerglings
        ultralisks = local_controller.ultralisks
        mutalisks = local_controller.mutalisks
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
        atk_force = zerglings | ultralisks | mutalisks
        if local_controller.floating_buildings_bm and local_controller.supply_used >= 199:
            atk_force = zerglings | ultralisks | mutalisks | local_controller.queens
        return combined_enemies, targets, atk_force

    def anti_terran_bm(self, unit):
        """Logic for countering the floating buildings bm"""
        local_controller = self.ai
        enemy_building = local_controller.enemy_structures
        flying_buildings = enemy_building.flying
        if unit.type_id in (MUTALISK, QUEEN) and flying_buildings:
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
                if self.micro_zerglings(target, unit):
                    return True
            else:
                action(attack_command(closest_target(unit_position)))
                return True
        else:
            action(attack_command(local_controller.enemies.not_flying.closest_to(unit_position)))
            return True
