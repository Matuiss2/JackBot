"""Everything related to army bahvior"""
from sc2.constants import (
    ADEPTPHASESHIFT,
    AUTOTURRET,
    BUNKER,
    DISRUPTORPHASED,
    EFFECT_INJECTLARVA,
    EGG,
    INFESTEDTERRAN,
    INFESTEDTERRANSEGG,
    LARVA,
    OVERSEER,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    QUEEN,
    QUEENSPAWNLARVATIMER,
    SPINECRAWLER,
    ULTRALISK,
    ZERGLING,
)


class army_control:
    def army_micro(self):
        """Micro function, its just slight better than a-move, need A LOT of improvements.
        Name army_micro because it is in army.py."""
        targets = 0
        enemy_build = self.known_enemy_structures
        if self.known_enemy_units:
            excluded_units = {
                ADEPTPHASESHIFT,
                DISRUPTORPHASED,
                EGG,
                LARVA,
                INFESTEDTERRANSEGG,
                INFESTEDTERRAN,
                AUTOTURRET,
            }
            filtered_enemies = self.known_enemy_units.not_structure.exclude_type(excluded_units)
            static_defence = self.known_enemy_units.of_type({SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS})
            targets = static_defence | filtered_enemies.not_flying
        atk_force = self.units(ZERGLING) | self.units(ULTRALISK)
        # enemy_detection = self.known_enemy_units.not_structure.of_type({OVERSEER, OBSERVER})
        for attacking_unit in atk_force:
            if targets and targets.closer_than(17, attacking_unit.position):
                in_range_targets = targets.in_attack_range_of(attacking_unit)
                if in_range_targets:
                    self.attack_lowhp(attacking_unit, in_range_targets)
                    continue  # these continues are needed so a unit doesnt get multiple orders per step
                else:
                    self.actions.append(attacking_unit.attack(targets.closest_to(attacking_unit.position)))
            elif enemy_build.closer_than(37, attacking_unit.position):
                self.actions.append(attacking_unit.attack(enemy_build.closest_to(attacking_unit.position)))
                continue
            elif self.time < 1000 and not self.close_enemies_to_base:
                if (
                    len(self.units(ULTRALISK).ready) < 4
                    and self.supply_used not in range(198, 201)
                    and len(self.units(ZERGLING).ready) < 41
                    and self.townhalls
                ):
                    self.actions.append(
                        attacking_unit.move(
                            self.townhalls.closest_to(self._game_info.map_center).position.towards(
                                self._game_info.map_center, 11
                            )
                        )
                    )
                    continue
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
                    continue
            else:
                if enemy_build:
                    self.actions.append(attacking_unit.attack(enemy_build.closest_to(attacking_unit.position)))
                    continue
                elif targets:
                    self.actions.append(attacking_unit.attack(targets.closest_to(attacking_unit.position)))
                    continue
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
        if self.units(OVERSEER):
            selected_ov = self.units(OVERSEER).first
            if atk_force:
                self.actions.append(selected_ov.move(atk_force.closest_to(selected_ov.position)))
            else:
                self.actions.append(selected_ov.move(self.townhalls.closest_to(selected_ov.position)))

    async def queens_abilities(self):
        """Injection and creep spread"""
        queens = self.units(QUEEN)
        hatchery = self.townhalls
        if hatchery:
            # lowhp_ultralisks = self.units(ULTRALISK).filter(lambda lhpu: lhpu.health_percentage < 0.27)
            for queen in queens.idle:
                # if not lowhp_ultralisks.closer_than(8, queen.position):
                selected = hatchery.closest_to(queen.position)
                if queen.energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                    self.actions.append(queen(EFFECT_INJECTLARVA, selected))
                    continue
                elif queen.energy >= 26:
                    await self.place_tumor(queen)

                # elif queen.energy >= 50:
                #     self.actions.append(queen(TRANSFUSION_TRANSFUSION, lowhp_ultralisks.closest_to(queen.position)))

            for hatch in hatchery.ready.noqueue:
                if not queens.closer_than(4, hatch):
                    for queen in queens:
                        if not self.townhalls.closer_than(4, queen):
                            self.actions.append(queen.move(hatch.position))
                            break
