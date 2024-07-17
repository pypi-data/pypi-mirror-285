import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.suitable.sara.api.robot_router import RobotRouter


class StateAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.state_get_current_motion)
    async def get_current_motion(self):
        pass

    @run_server_func(RobotRouter.state_get_estimated_time)
    async def get_estimated_time(self):
        pass
