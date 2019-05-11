from . import (
    cavern_construction,
    evochamber_construction,
    expansion,
    extractor_construction,
    hive_transformation,
    hydraden_construction,
    lair_transformation,
    pit_construction,
    pool_construction,
    spine_construction,
    spire_construction,
    spore_construction,
)


def get_build_commands(command):
    return (
        pool_construction.PoolConstruction(command),
        expansion.Expansion(command),
        extractor_construction.ExtractorConstruction(command),
        evochamber_construction.EvochamberConstruction(command),
        cavern_construction.CavernConstruction(command),
        pit_construction.PitConstruction(command),
        hive_transformation.HiveTransformation(command),
        lair_transformation.LairTransformation(command),
        spine_construction.SpineConstruction(command),
        spore_construction.SporeConstruction(command),
        spire_construction.SpireConstruction(command),
        hydraden_construction.HydradenConstruction(command),
    )