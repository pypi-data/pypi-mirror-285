import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.enums import Color, LocationType, LocationReference
from ablelabs.neon.utils.format_conversion import floor_decimal


class Speed:
    def __init__(self, unit: str, unit_s: float = None, rate: float = None) -> None:
        self.unit = unit
        self.unit_s = unit_s
        self.rate = rate

    def __str__(self) -> str:
        result = []
        if self.unit_s:
            result.append(f"{self.unit_s}{self.unit}/s")
        if self.rate:
            result.append(f"{floor_decimal(self.rate * 100, digit=1)}%")
        return f"({' '.join(result)})"

    @staticmethod
    def from_mm(mm: float):
        return Speed(unit="mm", unit_s=mm)

    @staticmethod
    def from_rate(rate: float = 1.0):
        return Speed(unit="mm", rate=rate)


class FlowRate(Speed):
    @staticmethod
    def from_ul(ul: float):
        return Speed(unit="ul", unit_s=ul)

    @staticmethod
    def from_rate(rate: float = 1.0):
        return Speed(unit="ul", rate=rate)


class LedBarParam:
    def __init__(
        self,
        color: Color = Color.NONE,
        on_brightness_percent: int = None,
        off_brightness_percent: int = None,
        bar_percent: int = None,
        blink_time_ms: int = None,
    ) -> None:
        self.color = color
        self.on_brightness_percent = on_brightness_percent
        self.off_brightness_percent = off_brightness_percent
        self.bar_percent = bar_percent
        self.blink_time_ms = blink_time_ms


class Location:
    def __init__(
        self,
        location_type: LocationType,
        location_number: int,
        well: str,
        reference: LocationReference,
        offset: tuple[float] = (0, 0, 0),
    ) -> None:
        self.location_type = location_type
        self.location_number = location_number
        self.well = well
        self.reference = reference
        self.offset = offset

    def to(
        self,
        location_number: int = None,
        well: str = None,
        reference: LocationReference = None,
        offset: tuple[float] = None,
    ):
        return Location(
            location_type=self.location_type,
            location_number=(
                location_number if location_number else self.location_number
            ),
            well=well if well else self.well,
            reference=reference if reference else self.reference,
            offset=offset if offset else self.offset,
        )

    def __str__(self) -> str:
        # inspect만으로는 원하는 형태로 만들기가 어려울 듯.
        # result = " ".join(
        #     [
        #         f"{name}={value}"
        #         for name, value in inspect.getmembers(self)
        #         if "__" not in name and not inspect.isfunction(value)
        #     ]
        # )
        # return result
        result = f"{self.location_type}"
        if self.location_number:
            result += f".{self.location_number}"
        if self.well:
            result += f" well={self.well}"
        if self.reference:
            result += f" reference={self.reference}"
        if self.offset and self.offset != (0, 0, 0):
            result += f" offset={self.offset}"
        return result
    
    def __repr__(self) -> str:
        return self.__str__()


if __name__ == "__main__":
    print(
        Location(
            location_type=LocationType.DECK,
            location_number=12,
            well="a6",
            reference=LocationReference.BOTTOM,
            offset=(1, 2, 3),
        )
    )
