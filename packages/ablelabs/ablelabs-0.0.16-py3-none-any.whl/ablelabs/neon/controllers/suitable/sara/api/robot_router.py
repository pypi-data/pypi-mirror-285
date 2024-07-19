from typing import Any

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerServer
from ablelabs.neon.common.suitable.enums import Axis
from ablelabs.neon.common.suitable.struct import Location, Speed, FlowRate


class RobotRouter(MessengerServer):
    async def robot_wait_boot(self):
        pass

    async def robot_stop(self):
        pass

    async def robot_clear_error(self):
        pass

    async def robot_pause(self):
        pass

    async def robot_resume(self):
        pass

    async def robot_is_connected(self):
        pass

    async def robot_get_environment(self):
        pass

    # set api
    async def set_pipettes(self, value: dict[int, str | None]):
        pass

    async def set_tips(self, value: dict[int, str | None]):
        pass

    async def set_labwares(self, value: dict[int, str | None]):
        pass

    async def set_update_pipette_attrs(self, value: dict[int, dict]):
        pass

    # state api
    async def state_get_current_motion(self):
        pass

    async def state_get_estimated_time(self):
        pass

    # motion api
    async def motion_initialize(self):
        pass

    async def motion_delay(self, sec: float):
        pass

    async def motion_move_to_ready(self):
        pass

    async def motion_move_to(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_pick_up_tip(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_drop_tip(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_rise_tip(
        self,
        pipette_number: list[int],
        height_offset: float | list[float],
        z_speed: Speed | list[Speed],
        optimize: bool = False,
    ):
        pass

    async def motion_aspirate(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        blow_out_flow_rate: FlowRate = None,
        optimize: bool = False,
    ):
        pass

    async def motion_dispense(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        optimize: bool = False,
    ):
        pass

    async def motion_mix(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        iteration: int,
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        delay: float = 0.0,
        optimize: bool = False,
    ):
        pass

    async def motion_blow_out(
        self,
        pipette_number: list[int],
        flow_rate: FlowRate | list[FlowRate] = None,
    ):
        pass

    # axis api
    async def axis_get_position(self, axis: Axis, floor_digit: int = 1):
        pass

    async def axis_set_speed(self, axis: Axis, value: float):
        pass

    async def axis_set_accel(self, axis: Axis, value: float):
        pass

    async def axis_set_decel(self, axis: Axis, value: float):
        pass

    async def axis_enable(self, axis: Axis):
        pass

    async def axis_disable(self, axis: Axis):
        pass

    async def axis_stop(self, axis: Axis):
        pass

    async def axis_home(self, axis: Axis):
        pass

    async def axis_jog(self, axis: Axis, value: float):
        pass

    async def axis_step(self, axis: Axis, value: float):
        pass

    async def axis_move(self, axis: Axis, value: float):
        pass

    async def axis_wait_home_done(self, axis: Axis):
        pass

    async def axis_wait_move_done(self, axis: Axis):
        pass
