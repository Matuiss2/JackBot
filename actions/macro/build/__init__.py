""" Group all classes from macro/build"""
from . import (
    cavern_construction,
    evochamber_construction,
    expansion,
    extractor_construction,
    hydraden_construction,
    pit_construction,
    pool_construction,
    spine_construction,
    spire_construction,
    spore_construction,
    transformation_to_hive,
    transformation_to_lair,
)


def get_build_commands(cmd):
    """ Getter for all commands from macro/build"""
    return (
        cavern_construction.CavernConstruction(cmd),
        evochamber_construction.EvochamberConstruction(cmd),
        expansion.Expansion(cmd),
        extractor_construction.ExtractorConstruction(cmd),
        hydraden_construction.HydradenConstruction(cmd),
        pit_construction.PitConstruction(cmd),
        pool_construction.PoolConstruction(cmd),
        spine_construction.SpineConstruction(cmd),
        spire_construction.SpireConstruction(cmd),
        spore_construction.SporeConstruction(cmd),
        transformation_to_hive.TransformationToHive(cmd),
        transformation_to_lair.TransformationToLair(cmd),
    )
