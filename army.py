from sc2.constants import (
    ADEPTPHASESHIFT,
    AUTOTURRET,
    BUNKER,
    DISRUPTORPHASED,
    EGG,
    INFESTEDTERRAN,
    INFESTEDTERRANSEGG,
    LARVA,
    OVERSEER,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    SPINECRAWLER,
    ULTRALISK,
    ZERGLING,
)


class army_control:
    async def army_micro(self):
        """Micro function, its just slight better than a-move, need A LOT of improvements.
        Name army_micro because it is in army.py."""
        enemy_build = self.known_enemy_structures
        excluded_units = {ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA, INFESTEDTERRANSEGG, INFESTEDTERRAN, AUTOTURRET}
        filtered_enemies = self.known_enemy_units.not_structure.exclude_type(excluded_units)
        static_defence = self.known_enemy_units.of_type({SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS})
        target = static_defence | filtered_enemies.not_flying
        atk_force = self.units(ZERGLING) | self.units(ULTRALISK)
        for attacking_unit in atk_force:
            if target.closer_than(47, attacking_unit.position):
                self.actions.append(attacking_unit.attack(target.closest_to(attacking_unit.position)))
                continue  # these continues are needed so a unit doesnt get multiple orders per step
            elif enemy_build.closer_than(27, attacking_unit.position):
                self.actions.append(attacking_unit.attack(enemy_build.closest_to(attacking_unit.position)))
                continue
            elif self.time < 235:
                if atk_force.amount <= 25:
                    self.actions.append(
                        attacking_unit.move(self._game_info.map_center.towards(self.enemy_start_locations[0], 11))
                    )
                    continue
                elif attacking_unit.position.distance_to(self.enemy_start_locations[0]) > 0 and atk_force.amount > 25:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
                    continue
            elif self.time < 1000:
                if self.units(ULTRALISK).amount < 4 and self.supply_used not in range(198, 201):
                    self.actions.append(attacking_unit.move(self._game_info.map_center))
                    continue
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
                    continue

            else:
                if enemy_build:
                    self.actions.append(attacking_unit.attack(enemy_build.closest_to(attacking_unit.position)))
                    continue
                elif target:
                    self.actions.append(attacking_unit.attack(target.closest_to(attacking_unit.position)))
                    continue
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))

        for detection in self.units(OVERSEER):
            if atk_force:
                self.actions.append(detection.move(atk_force.closest_to(detection.position)))
