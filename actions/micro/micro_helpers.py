"""Every helper for controlling units go here"""
from sc2.constants import EffectId, UnitTypeId
from sc2.position import Point2


class MicroHelpers:
    """Group all helpers, for unit control and targeting here"""

    def attack_close_target(self, unit, enemies):
        """
        It targets lowest hp units on its range, if there is any attack the closest
        Parameters
        ----------
        unit: Unit from the attacking force
        enemies: All enemy targets

        Returns
        -------
        True and the action(attack low hp enemy or any in range) if it meets the conditions
        """
        close_targets = enemies.subgroup(target for target in enemies if unit.target_in_range(target))
        if close_targets:
            self.main.add_action(unit.attack(self.find_closest_lowest_hp(unit, close_targets)))
            return True
        closest_target = enemies.closest_to(unit)
        if closest_target:
            self.main.add_action(unit.attack(closest_target))
            return True
        return None

    def attack_start_location(self, unit):
        """
        It tell to attack the starting location
        Parameters
        ----------
        unit: Unit from the attacking force

        Returns
        -------
        True and the action(attack the starting enemy location) if it meets the conditions
        """
        if self.main.enemy_start_locations and not self.main.enemy_structures:
            self.main.add_action(unit.attack(self.main.enemy_start_locations[0]))
            return True
        return False

    def avoid_disruptor_shots(self, unit):
        """
        If the enemy has disruptor's, run a dodging code. Exclude ultralisks
        Parameters
        ----------
        unit: Unit from the attacking force

        Returns
        -------
        True and the action(dodge the shot) if it meets the conditions
        """
        if unit.type_id == UnitTypeId.ULTRALISK:
            return False
        for disruptor_ball in self.main.enemies.filter(
            lambda enemy: enemy.type_id == UnitTypeId.DISRUPTORPHASED and enemy.distance_to(unit) < 5
        ):
            self.main.add_action(unit.move(self.find_retreat_point(disruptor_ball, unit)))
            return True
        return None

    def avoid_effects(self, unit):
        """Dodge any effects"""
        if not self.main.state.effects or unit.type_id == UnitTypeId.ULTRALISK:
            return False
        effects_radius = {
            EffectId.PSISTORMPERSISTENT: 1.5,
            EffectId.THERMALLANCESFORWARD: 0.3,
            EffectId.NUKEPERSISTENT: 8,
            EffectId.BLINDINGCLOUDCP: 2,
            EffectId.RAVAGERCORROSIVEBILECP: 0.5,
            EffectId.LURKERMP: 0.3,
        }  # Exchange it for '.radius' when the data gets implemented
        ignored_effects = (
            EffectId.SCANNERSWEEP,
            EffectId.GUARDIANSHIELDPERSISTENT,
            EffectId.LIBERATORTARGETMORPHDELAYPERSISTENT,
            EffectId.LIBERATORTARGETMORPHPERSISTENT,
        )  # Placeholder(must find better way to handle some of these)
        for effect in (ef for ef in self.main.state.effects if ef.id not in ignored_effects):
            danger_zone = effects_radius[effect.id] + unit.radius + 0.4
            if unit.position.distance_to_closest(effect.positions) > danger_zone:
                break
            perimeter_of_effect = Point2.center(effect.positions).furthest(list(unit.position.neighbors8))
            self.main.add_action(unit.move(perimeter_of_effect.towards(unit.position, -danger_zone)))
            return True
        return False

    @staticmethod
    def find_closest_lowest_hp(unit, enemies):
        """Find the closest within the lowest hp enemies"""
        return enemies.filter(lambda x: x.health == min(enemy.health for enemy in enemies)).closest_to(unit)

    @staticmethod
    def find_pursuit_point(target, unit) -> Point2:
        """
        Find a point towards the enemy unit
        Parameters
        ----------
        unit: Unit from the attacking force
        target: All enemy targets

        Returns
        -------
        A point that is close to the target
        """
        difference = unit.position - target.position
        return Point2((unit.position.x + (difference.x / 2) * -1, unit.position.y + (difference.y / 2) * -1))

    @staticmethod
    def find_retreat_point(target, unit) -> Point2:
        """
        Find a point away from the enemy unit
        Parameters
        ----------
        unit: Unit from the attacking force
        target: All enemy targets

        Returns
        -------
        A point that is far from the target
        """
        difference = unit.position - target.position
        return Point2((unit.position.x + (difference.x / 2), unit.position.y + (difference.y / 2)))

    async def handling_walls_and_attacking(self, unit, target):
        """
        It micros normally if no wall, if there is one attack it
        (can be improved, it does whats expected but its a regression overall when there is no walls)
        Parameters
        ----------
        unit: Unit from the attacking force
        target: All enemy targets

        Returns
        -------
        True and the action(attack closest or overall micro logic) if it meets the conditions
        """
        if await self.main._client.query_pathing(unit, target.closest_to(unit).position):
            if unit.type_id == UnitTypeId.ZERGLING:
                return self.microing_zerglings(unit, target)
            self.main.add_action(unit.attack(target.closest_to(unit.position)))
            return True
        if self.main.enemies.not_flying:
            self.main.add_action(unit.attack(self.main.enemies.not_flying.closest_to(unit.position)))
            return True

    def hit_and_run(self, target, unit, attack_trigger, run_trigger):
        """
        Attack when the unit can, run while it can't. We outrun the enemy.
        Parameters
        ----------
        target: All enemy targets
        unit: Unit from the attacking force
        attack_trigger: Weapon cooldown trigger value for attacking
        run_trigger: Weapon cooldown trigger value for running away

        Returns
        -------
        True always, along side the actions to attack or to run
        """
        # Only do this when our range > enemy range, our move speed > enemy move speed, and enemy is targeting us.
        our_range = unit.ground_range
        partial_enemy_range = target.ground_range
        if not partial_enemy_range:  # If target is melee it returns None so to avoid crashes we convert it to integer
            partial_enemy_range = 0
        enemy_range = partial_enemy_range + target.radius
        # Our unit should stay just outside enemy range, and inside our range.
        if enemy_range:
            minimum_distance = enemy_range + unit.radius + 0.01
        else:
            minimum_distance = our_range - unit.radius
        if minimum_distance > our_range:  # Check to make sure this range isn't negative.
            minimum_distance = our_range - unit.radius - 0.01
        # If our unit is in that range, and our attack is at least halfway off cooldown, attack.
        if minimum_distance <= unit.distance_to(target) <= our_range and unit.weapon_cooldown <= attack_trigger:
            self.main.add_action(unit.attack(target))
            return True
        # If our unit is too close, or our weapon is on more than a quarter cooldown, run away.
        if unit.distance_to(target) < minimum_distance or unit.weapon_cooldown > run_trigger:
            self.main.add_action(unit.move(self.find_retreat_point(target, unit)))
            return True
        self.main.add_action(unit.move(self.find_pursuit_point(target, unit)))  # If our unit is too far, run towards.
        return True

    def move_to_next_target(self, unit, enemies):
        """
        It helps on the targeting and positioning on the attack
        Parameters
        ----------
        unit: Unit from the attacking force
        enemies: All enemy targets

        Returns
        -------
        True and the action(move to the closest low hp enemy) if it meets the conditions
        """
        targets_in_melee_range = enemies.closer_than(1, unit)
        if targets_in_melee_range:
            self.main.add_action(unit.move(self.find_closest_lowest_hp(unit, targets_in_melee_range)))
            return True
        return None

    def move_to_rallying_point(self, targets, unit):
        """Set the point where the units should gather"""
        if self.main.ready_bases:
            enemy_main_base = self.main.enemy_start_locations[0]
            rally_point = self.main.ready_bases.closest_to(enemy_main_base).position.towards(enemy_main_base, 10)
            if unit.position.distance_to_point2(rally_point) > 5:
                self.main.add_action(unit.move(rally_point))
        elif targets:
            self.main.add_action(unit.attack(targets.closest_to(unit.position)))

    def retreat_unit(self, unit, target):
        """
        Tell the unit to retreat when overwhelmed
        Parameters
        ----------
        unit: Unit from the attacking force
        target: Enemy target

        Returns
        -------
        True and the action(retreat to rally point) if it meets the conditions, False always when suffering air harass
        or if we being attacked(base trade logic)
        """
        if self.main.townhalls.closer_than(15, unit) or self.main.counter_attack_vs_flying:
            return False
        if (
            self.main.townhalls
            and not self.main.close_enemies_to_base
            and not self.main.structures.closer_than(7, unit.position)
            and self.select_enemy_value_table_by_race(unit, target) >= self.combatants_value(unit.position, 1, 5, 13)
        ):
            self.move_to_rallying_point(target, unit)
            self.retreat_units.add(unit.tag)
            return True
        return False

    def stutter_step(self, target, unit):
        """
        Attack when the unit can, run while it can't(We don't outrun the enemy)
        Parameters
        ----------
        unit: Unit from the attacking force
        target: Enemy target

        Returns
        -------
        True always and the action(attack or retreat, its different from hit and run) if it meets the conditions
        """
        if not unit.weapon_cooldown:
            self.main.add_action(unit.attack(target))
            return True
        self.main.add_action(unit.move(self.find_retreat_point(target, unit)))
        return True

    @staticmethod
    def threats_on_trigger_range(targets, unit, trigger_range):
        """
        Identify threats based on given range
        Parameters
        ----------
        targets: All enemy targets
        unit: Unit from the attacking force
        trigger_range: The range from the given unit as center to check for threats within the circle

        Returns
        -------
        A generator with all threats within the range
        """
        for enemy in targets.filter(lambda target: target.distance_to(unit) < trigger_range):
            yield enemy
