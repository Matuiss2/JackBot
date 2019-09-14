""" Group all classes from macro/build"""
from . import (
    cavern_construction,
    evochamber_construction,
    expansion,
    extractor_construction,
    transformation_to_hive,
    hydraden_construction,
    transformation_to_lair,
    pit_construction,
    pool_construction,
    spine_construction,
    spire_construction,
    spore_construction,
)


def get_build_commands(cmd):
    """ Getter for all commands from macro/build"""
    return (
        pool_construction.PoolConstruction(cmd),
        expansion.Expansion(cmd),
        extractor_construction.ExtractorConstruction(cmd),
        evochamber_construction.EvochamberConstruction(cmd),
        cavern_construction.CavernConstruction(cmd),
        pit_construction.PitConstruction(cmd),
        transformation_to_hive.TransformationToHive(cmd),
        transformation_to_lair.TransformationToLair(cmd),
        spine_construction.SpineConstruction(cmd),
        spore_construction.SporeConstruction(cmd),
        spire_construction.SpireConstruction(cmd),
        hydraden_construction.HydradenConstruction(cmd),
    )
