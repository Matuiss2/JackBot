"""Everything related to the main sc2 end of the game score methods"""


class ScoreDetails:
    """ Accessible in self.state.score during step function
    For more information, see https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/score.proto
    """

    def __init__(self, proto):
        self._data = proto
        self.proto = proto.score_details

    @property
    def score_type(self):
        """Returns all score types"""
        return self._data.score_type

    @property
    def score(self):
        """Score from post game(I think)"""
        return self._data.score

    @property
    def idle_production_time(self):
        """returns the sum of the time that the production facilities stayed idle
         on the game by the player until the call"""
        return self.proto.idle_production_time

    @property
    def idle_worker_time(self):
        """returns the sum of the time that the workers stayed idle on the game by the player until the call"""
        return self.proto.idle_worker_time

    @property
    def total_value_units(self):
        """returns the sum of the unit values on the game by the player until the call"""
        return self.proto.total_value_units

    @property
    def total_value_structures(self):
        """returns the sum of the structures values on the game by the player until the call"""
        return self.proto.total_value_structures

    @property
    def killed_value_units(self):
        """returns the sum of the unit values that were killed on the game by the player until the call"""
        return self.proto.killed_value_units

    @property
    def killed_value_structures(self):
        """returns the sum of the structure values that were killed on the game by the player until the call"""
        return self.proto.killed_value_structures

    @property
    def collected_minerals(self):
        """returns the amount of collected minerals on the game by the player until the call"""
        return self.proto.collected_minerals

    @property
    def collected_vespene(self):
        """returns the amount of collected vespene on the game by the player until the call"""
        return self.proto.collected_vespene

    @property
    def collection_rate_minerals(self):
        """returns the collection rate(by minute) of minerals from the last minute by the player"""
        return self.proto.collection_rate_minerals

    @property
    def collection_rate_vespene(self):
        """returns the collection rate(by minute) of vespene from the last minute by the player"""
        return self.proto.collection_rate_vespene

    @property
    def spent_minerals(self):
        """returns the amount of spent minerals on the game by the player until the call"""
        return self.proto.spent_minerals

    @property
    def spent_vespene(self):
        """returns the amount of spent vespene on the game by the player until the call"""
        return self.proto.spent_vespene

    @property
    def food_used_none(self):
        """returns the supply that's is not used compared to the current supply cap(I think)"""
        return self.proto.food_used.none

    @property
    def food_used_army(self):
        """returns the supply that's is used on army units"""
        return self.proto.food_used.army

    @property
    def food_used_economy(self):
        """returns the supply that's is used on worker and utility units"""
        return self.proto.food_used.economy

    @property
    def food_used_technology(self):
        return self.proto.food_used.technology

    @property
    def food_used_upgrade(self):
        return self.proto.food_used.upgrade

    @property
    def killed_minerals_none(self):
        return self.proto.killed_minerals.none

    @property
    def killed_minerals_army(self):
        """returns the amount of minerals value for the enemy army killed on the game by the player until the call"""
        return self.proto.killed_minerals.army

    @property
    def killed_minerals_economy(self):
        """returns the amount of minerals value for the enemy workers killed on the game by the player until the call"""
        return self.proto.killed_minerals.economy

    @property
    def killed_minerals_technology(self):
        return self.proto.killed_minerals.technology

    @property
    def killed_minerals_upgrade(self):
        """returns the amount of minerals value for the stopped enemy upgrades
         on the game by the player until the call"""
        return self.proto.killed_minerals.upgrade

    @property
    def killed_vespene_none(self):
        return self.proto.killed_vespene.none

    @property
    def killed_vespene_army(self):
        """returns the amount of minerals value for the enemy army killed on the game by the player until the call"""
        return self.proto.killed_vespene.army

    @property
    def killed_vespene_economy(self):
        """returns the amount of vespene value for the enemy workers killed on the game by the player until the call"""
        return self.proto.killed_vespene.economy

    @property
    def killed_vespene_technology(self):
        return self.proto.killed_vespene.technology

    @property
    def killed_vespene_upgrade(self):
        """returns the amount of minerals value for the stopped enemy upgrades
         on the game by the player until the call"""
        return self.proto.killed_vespene.upgrade

    @property
    def lost_minerals_none(self):
        return self.proto.lost_minerals.none

    @property
    def lost_minerals_army(self):
        return self.proto.lost_minerals.army

    @property
    def lost_minerals_economy(self):
        return self.proto.lost_minerals.economy

    @property
    def lost_minerals_technology(self):
        return self.proto.lost_minerals.technology

    @property
    def lost_minerals_upgrade(self):
        return self.proto.lost_minerals.upgrade

    @property
    def lost_vespene_none(self):
        return self.proto.lost_vespene.none

    @property
    def lost_vespene_army(self):
        return self.proto.lost_vespene.army

    @property
    def lost_vespene_economy(self):
        return self.proto.lost_vespene.economy

    @property
    def lost_vespene_technology(self):
        return self.proto.lost_vespene.technology

    @property
    def lost_vespene_upgrade(self):
        return self.proto.lost_vespene.upgrade

    @property
    def friendly_fire_minerals_none(self):
        return self.proto.friendly_fire_minerals.none

    @property
    def friendly_fire_minerals_army(self):
        return self.proto.friendly_fire_minerals.army

    @property
    def friendly_fire_minerals_economy(self):
        return self.proto.friendly_fire_minerals.economy

    @property
    def friendly_fire_minerals_technology(self):
        return self.proto.friendly_fire_minerals.technology

    @property
    def friendly_fire_minerals_upgrade(self):
        return self.proto.friendly_fire_minerals.upgrade

    @property
    def friendly_fire_vespene_none(self):
        return self.proto.friendly_fire_vespene.none

    @property
    def friendly_fire_vespene_army(self):
        return self.proto.friendly_fire_vespene.army

    @property
    def friendly_fire_vespene_economy(self):
        return self.proto.friendly_fire_vespene.economy

    @property
    def friendly_fire_vespene_technology(self):
        return self.proto.friendly_fire_vespene.technology

    @property
    def friendly_fire_vespene_upgrade(self):
        return self.proto.friendly_fire_vespene.upgrade

    @property
    def used_minerals_none(self):
        return self.proto.used_minerals.none

    @property
    def used_minerals_army(self):
        return self.proto.used_minerals.army

    @property
    def used_minerals_economy(self):
        return self.proto.used_minerals.economy

    @property
    def used_minerals_technology(self):
        return self.proto.used_minerals.technology

    @property
    def used_minerals_upgrade(self):
        return self.proto.used_minerals.upgrade

    @property
    def used_vespene_none(self):
        return self.proto.used_vespene.none

    @property
    def used_vespene_army(self):
        return self.proto.used_vespene.army

    @property
    def used_vespene_economy(self):
        return self.proto.used_vespene.economy

    @property
    def used_vespene_technology(self):
        return self.proto.used_vespene.technology

    @property
    def used_vespene_upgrade(self):
        return self.proto.used_vespene.upgrade

    @property
    def total_used_minerals_none(self):
        """returns the average amount of minerals that was stored on the game by the player until the call"""
        return self.proto.total_used_minerals.none

    @property
    def total_used_minerals_army(self):
        """returns the amount of minerals used on army on the game by the player until the call"""
        return self.proto.total_used_minerals.army

    @property
    def total_used_minerals_economy(self):
        """returns the amount of minerals used on drones on the game by the player until the call"""
        return self.proto.total_used_minerals.economy

    @property
    def total_used_minerals_technology(self):
        """returns the amount of minerals used on tech on the game by the player until the call"""
        return self.proto.total_used_minerals.technology

    @property
    def total_used_minerals_upgrade(self):
        """returns the amount of minerals used on upgrades on the game by the player until the call"""
        return self.proto.total_used_minerals.upgrade

    @property
    def total_used_vespene_none(self):
        """returns the average amount of vespene that was stored on the game by the player until the call"""
        return self.proto.total_used_vespene.none

    @property
    def total_used_vespene_army(self):
        """returns the amount of vespene used on army on the game by the player until the call"""
        return self.proto.total_used_vespene.army

    @property
    def total_used_vespene_economy(self):
        """returns the amount of vespene used on drones on the game by the player until the call"""
        return self.proto.total_used_vespene.economy

    @property
    def total_used_vespene_technology(self):
        """returns the amount of vespene used on tech on the game by the player until the call"""
        return self.proto.total_used_vespene.technology

    @property
    def total_used_vespene_upgrade(self):
        """returns the amount of vespene used on upgrades on the game by the player until the call"""
        return self.proto.total_used_vespene.upgrade

    @property
    def total_damage_dealt_life(self):
        """returns the amount of damage dealt to the enemies hp on the game by the player until the call"""
        return self.proto.total_damage_dealt.life

    @property
    def total_damage_dealt_shields(self):
        """returns the amount of damage dealt to the enemies shield on the game by the player until the call"""
        return self.proto.total_damage_dealt.shields

    @property
    def total_damage_dealt_energy(self):
        """returns the amount of damage dealt to the enemies energy on the game by the player until the call"""
        return self.proto.total_damage_dealt.energy

    @property
    def total_damage_taken_life(self):
        """returns the amount of hp lost by attacks(f.e feedback) on the game by the player until the call"""
        return self.proto.total_damage_taken.life

    @property
    def total_damage_taken_shields(self):
        """returns the amount of shield lost by attacks(f.e feedback) on the game by the player until the call"""
        return self.proto.total_damage_taken.shields

    @property
    def total_damage_taken_energy(self):
        """returns the amount of energy lost by attacks(f.e feedback) on the game by the player until the call"""
        return self.proto.total_damage_taken.energy

    @property
    def total_healed_life(self):
        """returns the amount of hp replenished on the game by the player until the call"""
        return self.proto.total_healed.life

    @property
    def total_healed_shields(self):
        """returns the amount of shield replenished on the game by the player until the call"""
        return self.proto.total_healed.shields

    @property
    def total_healed_energy(self):
        """returns the amount of energy replenished on the game by the player until the call"""
        return self.proto.total_healed.energy
