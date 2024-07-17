import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.suitable.enums import Axis

PIPETTE_COUNT: int = 8
PIPETTE_NUMBERS = [i + 1 for i in range(PIPETTE_COUNT)]

AXIS_YS = [Axis.Y[pipette_number] for pipette_number in PIPETTE_NUMBERS]
AXIS_ZS = [Axis.Z[pipette_number] for pipette_number in PIPETTE_NUMBERS]
AXIS_PS = [Axis.P[pipette_number] for pipette_number in PIPETTE_NUMBERS]

Y_MIN_INTERVAL_MM = 9.0

SLEEP_CHECK_COM_PORT = 3
SLEEP_CHECK_HW_STATUS = 1
SLEEP_UPDATE_DIO_LOOP = 0.5
SLEEP_LOOP = 0.1
SLEEP_AFTER_TIMEOUT = 5