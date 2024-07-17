# import asyncio
# from loguru import logger

# import sys, os

# sys.path.append(os.path.abspath(os.curdir))
# from ablelabs.neon.utils.network.tcp_server import TcpServer
# from ablelabs.neon.utils.decorators import log_func_args_async
# from ablelabs.neon.controllers.suitable.sara.api.robot_router import (
#     RobotRouter as BaseRobotRouter,
# )

# # from neon.common.suitable.robot_context import *
# from ablelabs.neon.common.path import Path
# from ablelabs.neon.common.suitable.enums import LocationType, Axis
# from ablelabs.neon.common.suitable.struct import Location, Speed, FlowRate

# # from neon.common.suitable.robot_controller import *


# class RobotRouter(BaseRobotRouter):
#     def __init__(
#         self,
#         tcp_server: TcpServer,
#         robot_context: RobotContext,
#         # robot_controller: RobotController,
#     ) -> None:
#         super().__init__(tcp_server=tcp_server)
#         self._robot_context = robot_context
#         # self._robot_controller = robot_controller
#         # self._robot_command = robot_controller._robot_command
#         # self._pipette_command = robot_controller._pipette_command
#         # self._axis_command = robot_controller._axis_command
#         # self._balance_command = robot_controller._balance_command

#     # set api

#     # robot api
#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def robot_wait_boot(self):
#         await self._robot_controller.wait_boot()

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.debug)
#     async def robot_stop(self):
#         await self._robot_controller.stop()

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.debug)
#     async def robot_clear_error(self):
#         await self._robot_controller.clear_error()

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.debug)
#     async def robot_pause(self):
#         await self._robot_controller.pause()

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.debug)
#     async def robot_resume(self):
#         await self._robot_controller.resume()

#     @log_func_args_async(log_after_func=logger.debug)
#     async def robot_is_connected(self):
#         robot_driver = self._robot_controller._robot_driver
#         is_axis_connected = all(
#             motor.is_connected() for motor in robot_driver.motors.values()
#         )
#         is_balance_connected = (
#             robot_driver.balance is not None and robot_driver.balance.is_connected()
#         )
#         is_dio_connected = (
#             robot_driver.dio is not None and robot_driver.dio.is_connected()
#         )
#         return (
#             is_axis_connected,
#             is_balance_connected,
#             is_dio_connected,
#         )

#     @log_func_args_async(log_after_func=logger.debug)
#     async def robot_get_environment(self):
#         (temperature, pressure, humidity) = self._robot_controller.get_environment()
#         return (temperature, pressure, humidity)

#     # state api
#     @log_func_args_async(log_before_func=logger.debug, log_after_func=logger.info)
#     async def state_get_current_motion(self):
#         return await self._robot_controller.get_current_motion()

#     @log_func_args_async(log_before_func=logger.debug, log_after_func=logger.info)
#     async def state_get_estimated_time(self):
#         raise NotImplementedError()  # sypark

#     # motion api
#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_initialize(self):
#         await self._robot_controller.initialize()

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_delay(self, sec: float):
#         await self._robot_command.delay(sec=sec)

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_move_to_ready(self):
#         await self._robot_controller.move_to_ready()

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_move_to(
#         self,
#         location: Location,
#         pipette_cone: int = 1,
#         optimize: bool = False,
#     ):
#         await self._pipette_command.move_to(
#             location=location,
#             pipette_cone=pipette_cone,
#             optimize=optimize,
#         )

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_pick_up_tip(
#         self,
#         location: Location,
#         pipette_cone: int,
#         optimize: bool = False,
#     ):
#         await self._pipette_command.pick_up_tip(
#             location=location,
#             pipette_cone=pipette_cone,
#             optimize=optimize,
#         )

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_drop_tip(
#         self,
#         location: Location,
#         pipette_cone: int,
#         optimize: bool = False,
#     ):
#         await self._pipette_command.drop_tip(
#             location=location,
#             pipette_cone=pipette_cone,
#             optimize=optimize,
#         )

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_rise_tip(
#         self,
#         height_offset: float,
#         z_speed: Speed,
#     ):
#         await self._pipette_command.rise_tip(
#             height_offset=height_offset,
#             z_speed=z_speed,
#         )

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_aspirate(
#         self,
#         volume: float,
#         location: Location = None,
#         pipette_cone: int = 1,
#         flow_rate: FlowRate = None,
#         blow_out_flow_rate: FlowRate = None,
#         optimize: bool = False,
#     ):
#         await self._pipette_command.aspirate(
#             volume=volume,
#             location=location,
#             pipette_cone=pipette_cone,
#             flow_rate=flow_rate,
#             blow_out_flow_rate=blow_out_flow_rate,
#             optimize=optimize,
#         )

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_dispense(
#         self,
#         volume: float,
#         location: Location = None,
#         pipette_cone: int = 1,
#         flow_rate: FlowRate = None,
#         optimize: bool = False,
#     ):
#         await self._pipette_command.dispense(
#             volume=volume,
#             location=location,
#             pipette_cone=pipette_cone,
#             flow_rate=flow_rate,
#             optimize=optimize,
#         )

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_mix(
#         self,
#         volume: float,
#         iteration: int,
#         location: Location = None,
#         pipette_cone: int = 1,
#         flow_rate: FlowRate = None,
#         blow_out_flow_rate: FlowRate = None,
#         delay: float = 0.0,
#         optimize: bool = False,
#     ):
#         await self._pipette_command.mix(
#             volume=volume,
#             iteration=iteration,
#             location=location,
#             pipette_cone=pipette_cone,
#             flow_rate=flow_rate,
#             blow_out_flow_rate=blow_out_flow_rate,
#             delay=delay,
#             optimize=optimize,
#         )

#     @log_func_args_async(log_before_func=logger.info, log_after_func=logger.info)
#     async def motion_blow_out(
#         self,
#         flow_rate: FlowRate = None,
#     ):
#         await self._pipette_command.blow_out(
#             flow_rate=flow_rate,
#         )

#     # axis api
#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_get_position(self, axis: Axis, floor_digit: int = 1):
#         return await self._axis_command.get_position(axis=axis, floor_digit=floor_digit)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_set_speed(self, axis: Axis, value: float):
#         return await self._axis_command.set_speed(axis=axis, value=value)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_set_accel(self, axis: Axis, value: float):
#         return await self._axis_command.set_accel(axis=axis, value=value)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_set_decel(self, axis: Axis, value: float):
#         return await self._axis_command.set_decel(axis=axis, value=value)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_enable(self, axis: Axis):
#         await self._axis_command.enable(axis=axis)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_disable(self, axis: Axis):
#         await self._axis_command.disable(axis=axis)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_stop(self, axis: Axis):
#         await self._axis_command.stop(axis=axis)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_home(self, axis: Axis):
#         await self._axis_command.home(axis=axis)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_jog(self, axis: Axis, value: float):
#         await self._axis_command.jog(axis=axis, value=value)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_step(self, axis: Axis, value: float):
#         await self._axis_command.step(axis=axis, value=value)

#     @log_func_args_async(log_after_func=logger.debug)
#     async def axis_move(self, axis: Axis, value: float):
#         await self._axis_command.move(axis=axis, value=value)

#     @log_func_args_async(log_before_func=logger.debug, log_after_func=logger.debug)
#     async def axis_wait_home_done(self, axis: Axis):
#         await self._axis_command.wait_home_done(axis=axis)

#     @log_func_args_async(log_before_func=logger.debug, log_after_func=logger.debug)
#     async def axis_wait_move_done(self, axis: Axis):
#         await self._axis_command.wait_move_done(axis=axis)


# async def build_api(
#     robot_context: RobotContext,
#     robot_controller: RobotController,
#     ip: str = "localhost",
#     port: int = 1234,
# ):
#     # log_func = logger.debug
#     log_func = logger.trace

#     tcp_server = TcpServer(name="tcp_server", log_func=log_func)
#     messenger_server = MessengerServer(
#         tcp_server=tcp_server,
#         robot_context=robot_context,
#         robot_controller=robot_controller,
#     )

#     async def on_connected():
#         # await robot.initialize()
#         pass

#     tcp_server.on_connected.append(on_connected)

#     async def on_received(msg: str):
#         pass

#     tcp_server.on_received.append(on_received)

#     async def send_api(msg: str):
#         # await tcp_server.send(msg)
#         pass

#     robot_controller._robot_command.send_api = send_api
#     await tcp_server.open(ip=ip, port=port)


# async def main():
#     logger.remove()
#     # logger.add(sys.stdout, level="TRACE")
#     logger.add(sys.stdout, level="INFO", backtrace=False)
#     # logger.add(sys.stdout, level="DEBUG", backtrace=True)
#     logger.add("logs/trace.log", level="TRACE")
#     logger.add("logs/debug.log", level="DEBUG")
#     logger.add("logs/info.log", level="INFO")
#     logger.add("logs/warning.log", level="WARNING")

#     ip = "localhost"
#     port = 1234

#     path = Path(required_dirs=["robot", "resources", "platform_autocal"])
#     robot_context = RobotContext(path=path)
#     robot_context.load_data(do_log=False)
#     robot_driver = RobotDriver(
#         robot_context=robot_context,
#     )
#     robot_command = RobotCommand(
#         robot_context=robot_context,
#         robot_driver=robot_driver,
#     )
#     dio_command = DIOCommand(
#         robot_context=robot_context,
#         robot_driver=robot_driver,
#     )
#     axis_command = AxisCommand(
#         robot_context=robot_context,
#         robot_driver=robot_driver,
#         robot_command=robot_command,
#     )
#     pipette_command = PipetteCommand(
#         robot_context=robot_context,
#         robot_command=robot_command,
#         axis_command=axis_command,
#     )
#     robot_controller = RobotController(
#         robot_context=robot_context,
#         robot_driver=robot_driver,
#         robot_command=robot_command,
#         dio_command=dio_command,
#         axis_command=axis_command,
#         pipette_command=pipette_command,
#     )
#     await build_api(
#         robot_context=robot_context,
#         robot_controller=robot_controller,
#         ip=ip,
#         port=port,
#     )
#     tasks = robot_controller.build_tasks()


# if __name__ == "__main__":
#     loop = asyncio.new_event_loop()
#     loop.set_debug(True)
#     loop.create_task(main())
#     loop.run_forever()
