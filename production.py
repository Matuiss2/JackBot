from sc2.constants import (
    DRONE,
    EXTRACTOR,
    LAIR,
    LARVA,
    OVERLORD,
    QUEEN,
    SPAWNINGPOOL,
    ULTRALISK,
    ULTRALISKCAVERN,
    ZERGLING,
    ZERGLINGMOVEMENTSPEED,
    ZERGGROUNDARMORSLEVEL3,
)


class production_control:
    def build_overlords(self):
        """We do not get supply blocked, but builds one more overlord than needed at some points"""
        if not self.supply_cap >= 200 and self.supply_left < 8:
            if self.can_afford(OVERLORD):
                base_amount = len(self.townhalls)  # so it just calculate once per loop
                if (
                    len(self.drones.ready) == 14
                    or (len(self.units(OVERLORD)) == 2 and base_amount == 1)
                    or (base_amount == 2 and not self.units(SPAWNINGPOOL))
                ):
                    return False
                if (base_amount in (1, 2) and self.already_pending(OVERLORD)) or (self.already_pending(OVERLORD) >= 2):
                    return False
                self.actions.append(self.units(LARVA).random.train(OVERLORD))
                return True
            return False
        return None

    def build_queens(self):
        """It possibly can get better but it seems good enough for now"""
        queens = self.queens
        hatchery = self.townhalls.exclude_type(LAIR).ready
        if hatchery.noqueue and self.units(SPAWNINGPOOL).ready:
            hatcheries_random = hatchery.noqueue.random
            if (
                len(queens) < len(hatchery) + 1
                and not self.already_pending(QUEEN)
                and self.can_feed(QUEEN)
                and self.can_afford(QUEEN)
            ):
                self.actions.append(hatcheries_random.train(QUEEN))

    def build_ultralisk(self):
        """Good for now but it might need to be changed vs particular
         enemy units compositions"""
        if self.units(ULTRALISKCAVERN).ready:
            if not self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL3) and self.time > 780:
                return False
            if self.can_afford(ULTRALISK) and self.can_feed(ULTRALISK):
                self.actions.append(self.units(LARVA).random.train(ULTRALISK))
                return True
            return False
        return None

    def build_workers(self):  # send to hatchery.py when there is one
        """Good for the beginning, but it doesnt adapt to losses of drones very well"""
        workers_total = len(self.workers)
        larva = self.units(LARVA)
        geysirs = self.units(EXTRACTOR)
        if not self.close_enemies_to_base and self.can_afford(DRONE) and self.can_feed(DRONE):
            if workers_total == 12 and not self.already_pending(DRONE) and self.time < 200:
                self.actions.append(larva.random.train(DRONE))
                return True
            if workers_total in (13, 14, 15) and len(self.units(OVERLORD)) + self.already_pending(OVERLORD) > 1:
                if workers_total == 15 and geysirs and self.units(SPAWNINGPOOL) and self.time < 250:
                    self.actions.append(larva.random.train(DRONE))
                    return True
                self.actions.append(larva.random.train(DRONE))
                return True

            optimal_workers = min(sum([x.ideal_harvesters for x in self.townhalls | geysirs]), 98 - len(geysirs))
            if workers_total + self.already_pending(DRONE) < optimal_workers and self.zerglings:
                self.actions.append(larva.random.train(DRONE))
                return True
        return None

    def build_zerglings(self):
        """good enough for now"""
        larva = self.units(LARVA)
        if self.units(SPAWNINGPOOL).ready:
            if self.time >= 170 and not self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED):
                return False
            if self.can_afford(ZERGLING) and self.can_feed(ZERGLING):
                if self.units(ULTRALISKCAVERN).ready and self.time < 1380:
                    if len(self.ultralisks) * 6 > len(self.zerglings):
                        self.actions.append(larva.random.train(ZERGLING))
                        return True
                else:
                    self.actions.append(larva.random.train(ZERGLING))
                    return True
            return False
        return None

    async def build_units(self):
        """ Build one unit, the most prioritized at the moment """
        if self.units(LARVA):
            available_units_in_order = (
                self.build_overlords,
                self.build_ultralisk,
                self.build_workers,
                self.build_queens,
                self.build_zerglings,
            )
            for build_unit_function in available_units_in_order:
                want_to_built_unit = build_unit_function()
                if want_to_built_unit:
                    break
