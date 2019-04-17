"""Everything related to calculate the creep spreading goes here"""
import math
from sc2.constants import AbilityId
from sc2.data import ActionResult
from sc2.position import Point2


class CreepControl:
    """It spreads creeps, finds 'optimal' locations for it(have trouble with ramps, many improvements can be made)"""

    def __init__(self):
        self.used_tumors = []
        self.valid_placements = self.unit_ability = None

    async def place_tumor(self, unit):
        """ Find a nice placement for the tumor and build it if possible, avoid expansion locations
        Makes creep to the enemy base, needs a better value function for the spreading, it gets stuck on ramps"""
        # Make sure unit can make tumor and what ability it is
        abilities = await self.get_available_abilities(unit)
        if AbilityId.BUILD_CREEPTUMOR_QUEEN in abilities:
            self.unit_ability = AbilityId.BUILD_CREEPTUMOR_QUEEN
        elif AbilityId.BUILD_CREEPTUMOR_TUMOR in abilities:
            self.unit_ability = AbilityId.BUILD_CREEPTUMOR_TUMOR
        else:
            return None
        # defining vars
        location_attempts = 30
        spread_distance = 8
        location = unit.position
        # Define random positions around unit
        positions = [
            Point2(
                (
                    location.x + spread_distance * math.cos(math.pi * alpha * 2 / location_attempts),
                    location.y + spread_distance * math.sin(math.pi * alpha * 2 / location_attempts),
                )
            )
            for alpha in range(location_attempts)
        ]
        # check if any of the positions are valid
        creep_mask = await self._client.query_building_placement(
            self._game_data.abilities[AbilityId.ZERGBUILD_CREEPTUMOR.value], positions
        )
        # filter valid results
        valid_placements = [p for idx, p in enumerate(positions) if creep_mask[idx] == ActionResult.Success]
        final_destiny = self.enemy_start_locations[0]
        if valid_placements:
            if self.tumors:
                self.valid_placements = sorted(
                    valid_placements,
                    key=lambda pos: pos.distance_to_closest(self.tumors) - pos.distance_to_point2(final_destiny),
                    reverse=True,
                )
            else:
                self.valid_placements = sorted(valid_placements, key=lambda pos: pos.distance_to_point2(final_destiny))
            self.avoid_blocking_expansions(unit)
            if self.unit_ability == AbilityId.BUILD_CREEPTUMOR_TUMOR:
                self.used_tumors.append(unit.tag)

    def avoid_blocking_expansions(self, unit):
        """ This is very expensive to the cpu, need optimization, keeps creep outside expansion locations"""
        for c_location in self.valid_placements:
            if all(c_location.distance_to_point2(el) > 8.5 for el in self.expansion_locations):
                if self.unit_ability == AbilityId.BUILD_CREEPTUMOR_QUEEN or not self.tumors:
                    self.add_action(unit(self.unit_ability, c_location))
                    break
                if c_location.distance_to_closest(self.tumors) >= 4:
                    self.add_action(unit(self.unit_ability, c_location))
                    break
