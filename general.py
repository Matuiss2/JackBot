from sc2.constants import (
    CANCEL,
    CANCEL_MORPHLAIR,
    CANCEL_MORPHHIVE,
    CANCEL_MORPHOVERSEER,
    HATCHERY,
    HIVE,
    INFESTATIONPIT,
    LAIR,
    MORPH_OVERSEER,
    OVERLORD,
    OVERLORDCOCOON,
    OVERSEER,
    ULTRALISKCAVERN,
    UPGRADETOHIVE_HIVE,
    UPGRADETOLAIR_LAIR,
    ZERGLINGATTACKSPEED,
    ZERGGROUNDARMORSLEVEL3,
    ZERGMELEEWEAPONSLEVEL3,
)


class extra_things:
    def __init__(self):
        self.location_index = 0

    def cancel_attacked_hatcheries(self):
        """find the hatcheries that are building, and have low health and cancel then,
        can be better, its easy to burst 150 hp, but if I put more it might cancel itself,
        will look into that later"""
        if self.known_enemy_structures.closer_than(50, self.start_location) and self.time < 300:
            for building in self.units(HATCHERY).filter(lambda x: 0.2 < x.build_progress < 1 and x.health < 400):
                self.actions.append(building(CANCEL))

    async def detection(self):
        """Morph overseers"""
        lords = self.units(OVERLORD)
        if (
            (self.units(LAIR) or self.units(HIVE))
            and self.can_afford(OVERSEER)
            and lords
            and not self.units(OVERSEER)
            and not any([await self.is_morphing(h) for h in self.units(OVERLORDCOCOON)])
        ):
            self.actions.append(lords.random(MORPH_OVERSEER))

    def finding_bases(self):
        """Find hidden bases, slowly"""
        if self.time >= 720 and self.time % 20 == 0:
            location = self.locations[self.location_index]
            if self.workers:
                self.actions.append(self.workers.closest_to(location).move(location))
                self.location_index = (self.location_index + 1) % len(self.locations)

    async def is_morphing(self, homecity):
        """Check if a base or overlord is morphing, good enough for now"""
        abilities = await self.get_available_abilities(homecity)
        morphing_upgrades = (CANCEL_MORPHLAIR, CANCEL_MORPHHIVE, CANCEL_MORPHOVERSEER)
        for morph in morphing_upgrades:
            if morph in abilities:
                return True
        return False

    async def morphing_townhalls(self):
        """Works well, maybe the timing can be improved"""
        if not (
            all(
                self.units(ULTRALISKCAVERN).ready and i == 1
                for i in (
                    self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL3),
                    self.already_pending_upgrade(ZERGMELEEWEAPONSLEVEL3),
                    self.already_pending_upgrade(ZERGLINGATTACKSPEED),
                )
            )
        ):
            lair = self.units(LAIR)
            hive = self.units(HIVE)
            base = self.units(HATCHERY)
            # Hive
            if (
                self.units(INFESTATIONPIT).ready
                and not hive
                and self.can_afford(HIVE)
                and not any([await self.is_morphing(h) for h in lair])
                and lair.ready.idle
            ):
                self.actions.append(lair.ready.idle.first(UPGRADETOHIVE_HIVE))
            # Lair
            if (
                len(self.townhalls) >= 3
                and self.can_afford(UPGRADETOLAIR_LAIR)
                and not (lair or hive)
                and not any([await self.is_morphing(h) for h in base])
                and self.units(HATCHERY).ready.idle
            ):
                self.actions.append(base.ready.idle.furthest_to(self._game_info.map_center)(UPGRADETOLAIR_LAIR))
