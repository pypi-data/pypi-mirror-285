from dataclasses import dataclass
import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.suitable.enums import LocationType, LocationReference


@dataclass
class Location:
    location_type: LocationType
    location_number: int
    well: list[str]
    reference: LocationReference
    offset: tuple[float] = (0, 0, 0)


def location(
    location_type: LocationType,
    location_number: int = None,
    well: list[str] = None,
    reference: LocationReference = None,
    offset: tuple[float] = (0, 0, 0),
):
    return Location(
        location_type=location_type,
        location_number=location_number,
        well=well,
        reference=reference,
        offset=offset,
    )
