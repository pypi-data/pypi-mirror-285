import asyncio
from loguru import logger

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
# from neon.utils.decorators import log_func_args_async
from ablelabs.neon.controllers.suitable.sara.api.robot_router import RobotRouter
from ablelabs.neon.controllers.suitable.sara.api.set_api import SetAPI
from ablelabs.neon.controllers.suitable.sara.api.state_api import StateAPI
from ablelabs.neon.controllers.suitable.sara.api.motion_api import MotionAPI
from ablelabs.neon.controllers.suitable.sara.api.axis_api import AxisAPI
from ablelabs.neon.common.suitable.constants import PIPETTE_NUMBERS
from ablelabs.neon.common.suitable.enums import LocationType, Axis, LocationReference
from ablelabs.neon.common.suitable.struct import Speed, FlowRate, location


class RobotAPI(MessengerClient):
    def __init__(self) -> None:
        tcp_client = TcpClient(name="tcp_client", log_func=logger.trace)
        super().__init__(tcp_client)
        self._set_api = SetAPI(tcp_client=tcp_client)
        self._state_api = StateAPI(tcp_client=tcp_client)
        self._motion_api = MotionAPI(tcp_client=tcp_client)
        self._axis_api = AxisAPI(tcp_client=tcp_client)

    @property
    def set(self):
        return self._set_api

    @property
    def state(self):
        return self._state_api

    @property
    def motion(self):
        return self._motion_api

    @property
    def axis(self):
        return self._axis_api

    # @log_func_args_async(log_before_func=logger.info, log_after_func=logger.debug)
    async def connect(self, ip, port):
        while True:
            try:
                await self._tcp_client.connect(ip=ip, port=port)
            except ConnectionRefusedError as e:
                await asyncio.sleep(1)
                continue
            else:
                break

    @run_server_func(RobotRouter.robot_wait_boot)
    async def wait_boot(self):
        pass

    @run_server_func(RobotRouter.robot_stop)
    async def stop(self):
        pass

    @run_server_func(RobotRouter.robot_clear_error)
    async def clear_error(self):
        pass

    @run_server_func(RobotRouter.robot_pause)
    async def pause(self):
        pass

    @run_server_func(RobotRouter.robot_resume)
    async def resume(self):
        pass

    @run_server_func(RobotRouter.robot_is_connected)
    async def is_connected(self):
        pass

    @run_server_func(RobotRouter.robot_get_environment)
    async def get_environment(self):
        pass


async def main():
    # import subprocess

    # subprocess.Popen(
    #     [r".venv\Scripts\python.exe", r"robot\src\controllers\suitable\sara\router.py"]
    # )

    logger.remove()
    # logger.add(sys.stdout, level="TRACE")
    # logger.add(sys.stdout, level="DEBUG", backtrace=False)
    logger.add(sys.stdout, level="INFO", backtrace=False)
    # logger.add("logs/trace.log", level="TRACE")
    # logger.add("logs/debug.log", level="DEBUG")
    logger.add("logs/info.log", level="INFO")

    ip = "localhost"
    port = 1234

    robot_api = RobotAPI()
    await robot_api.connect(ip=ip, port=port)

    # await robot_api.motion.initialize()

    robot_api.set.pipettes({n: "1ch1000ul" for n in PIPETTE_NUMBERS})
    robot_api.set.tips({n: "tip_1000" for n in PIPETTE_NUMBERS})
    robot_api.set.labwares(
        {
            1: "bioneer_384_qc_plate",
            2: "spl_dw_reservoir",
            3: "ablelabs_tiprack_1000ul",
            4: "spl_96_deep_well_plate",
            10: "spl_96_deep_well_plate",
            16: "spl_96_deep_well_plate",
            22: "spl_96_deep_well_plate",
            5: "ablelabs_tiprack_1000ul",
            11: "ablelabs_tiprack_1000ul",
            17: "ablelabs_tiprack_1000ul",
            23: "ablelabs_tiprack_1000ul",
            6: "ablelabs_tiprack_200ul",
            12: "ablelabs_tiprack_200ul",
            18: "ablelabs_tiprack_200ul",
            24: "ablelabs_tiprack_200ul",
        }
    )
    robot_api.set.update_pipette_attrs(
        {n: {"blow_out_volume": 20} for n in PIPETTE_NUMBERS}
    )

    await robot_api.stop()
    await robot_api.clear_error()  # stop 하고
    await robot_api.pause()
    await robot_api.resume()
    logger.info(f"is_connected = {await robot_api.is_connected()}")
    logger.info(f"get_environment = {await robot_api.get_environment()}")

    async def get_current_motion():
        while True:
            logger.info(
                f"get_current_motion = {await robot_api.state.get_current_motion()}"
            )

    getter_tasks = [
        asyncio.create_task(getter)
        for getter in [
            get_current_motion(),
        ]
    ]
    for getter_task in getter_tasks:
        getter_task.cancel()
    # if any([isinstance(task.result(), Exception) for task in tasks]):
    #     return

    await robot_api.motion.initialize()
    await robot_api.motion.move_to(
        pipette_number=[1, 2, 3],
        location=location(
            location_type=LocationType.DECK,
            location_number=[4, 4, 4],
            well=["a1", "b1", "c1"],
        ),
    )

    await robot_api.motion.pick_up_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.DECK,
            location_number=[3, 3, 3, 3, 3, 3, 3, 3],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.DECK,
            location_number=[3, 3, 3, 3, 3, 3, 3, 3],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.WASTE,
        ),
    )

    await robot_api.motion.aspirate(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=200,
        location=location(
            location_type=LocationType.DECK,
            location_number=[2, 2, 2, 2, 2, 2, 2, 2],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
        blow_out_flow_rate=FlowRate.from_ul(50),
    )
    await robot_api.motion.rise_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        height_offset=5,
        z_speed=Speed.from_mm(2),
    )
    await robot_api.motion.dispense(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=200,
        location=location(
            location_type=LocationType.DECK,
            location_number=[4, 4, 4, 4, 4, 4, 4, 4],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
    )
    await robot_api.motion.mix(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=100,
        iteration=2,
        # location=location(
        #     location_type=LocationType.DECK,
        #     location_number=[4, 4, 4, 4, 4, 4, 4, 4],
        #     well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        #     reference=LocationReference.BOTTOM,
        # ),
        flow_rate=FlowRate.from_ul(70),
        delay=0.1,
    )
    await robot_api.motion.blow_out(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        flow_rate=FlowRate.from_ul(200),
    )

    await robot_api.motion.aspirate(
        pipette_number=[1, 2, 3],
        volume=[200, 100, 50],
        location=location(
            location_type=LocationType.DECK,
            location_number=[2, 2, 2],
            well=["a1", "b1", "c1"],
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=[FlowRate.from_ul(100), FlowRate.from_ul(80), FlowRate.from_ul(60)],
        blow_out_flow_rate=FlowRate.from_ul(50),
    )
    await robot_api.motion.blow_out(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        flow_rate=FlowRate.from_ul(200),
    )
    # await robot_api.motion.move_to_ready()

    position = await robot_api.axis.get_position(axis=Axis.X)  # mm
    await robot_api.axis.set_speed(axis=Axis.X, value=10)  # mm/sec
    await robot_api.axis.set_accel(axis=Axis.X, value=10)  # mm/sec2
    await robot_api.axis.set_decel(axis=Axis.X, value=10)  # mm/sec2
    await robot_api.axis.disable(axis=Axis.X)
    await robot_api.axis.enable(axis=Axis.X)
    await robot_api.axis.stop(axis=Axis.X)
    await robot_api.axis.home(axis=Axis.X)
    await robot_api.axis.wait_home_done(axis=Axis.X)
    await robot_api.axis.jog(axis=Axis.X, value=10)  # mm/sec
    await robot_api.axis.step(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)
    await robot_api.axis.move(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    loop.create_task(main())
    loop.run_forever()
