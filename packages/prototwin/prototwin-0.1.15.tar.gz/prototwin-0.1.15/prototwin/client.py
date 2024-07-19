from typing import Self, Callable
from ctypes.wintypes import LARGE_INTEGER
from enum import IntEnum
import asyncio
import time
import ctypes
import struct
import prototwin_cmdbuff

from websockets.client import connect
from websockets.frames import OP_BINARY

# Maximum buffer size
_sz = 65536 * 8

# Native command buffer functions
_g = prototwin_cmdbuff.get
_s = prototwin_cmdbuff.set
_c = prototwin_cmdbuff.clear
_ws = prototwin_cmdbuff.write_size
_rs = prototwin_cmdbuff.read_size
_t = prototwin_cmdbuff.tick
_y = prototwin_cmdbuff.sync
_r = prototwin_cmdbuff.reset
_i = prototwin_cmdbuff.initialize
_l = prototwin_cmdbuff.load
_ce = prototwin_cmdbuff.create_environments
_re = prototwin_cmdbuff.reset_environment
_u = prototwin_cmdbuff.update

kernel32 = ctypes.windll.kernel32

def _sleep(seconds):
    """
    Precise sleep.

    Args:
        seconds (float): The number of seconds to sleep.
    """
    handle = kernel32.CreateWaitableTimerExW(None, None, 0x00000002, 0x1F0003)
    kernel32.SetWaitableTimer(handle, ctypes.byref(LARGE_INTEGER(int(seconds * -10000000))), 0, None, None, 0)
    kernel32.WaitForSingleObject(handle, 0xFFFFFFFF)
    kernel32.CancelWaitableTimer(handle)

class Pattern(IntEnum):
    NONE = 0
    LINEAR_X = 1,
    LINEAR_Z = 2,
    GRID = 3

class Client:
    def __init__(self, ws) -> None:
        """
        ProtoTwin Connect Python Client.

        Args:
            ws (WebSocketClientPrototcol): The websocket client
        """
        self._ws = ws
        self._wb = bytearray(_sz)
        prototwin_cmdbuff.provide(self._wb, _sz)

    def count(self) -> int:
        """
        The number of signals most recently received from ProtoTwin Connect.

        Returns:
            int: The number of signals.
        """
        return (_rs() - 12) / 8
    
    def get(self, address: int) -> bool|int|float:
        """
        Reads the value of a signal at the specified address.

        Args:
            address (int): The signal address.

        Returns:
            bool|int|float: The signal value.
        """
        return _g(address)

    def set(self, address: int, value: bool|int|float) -> None:
        """
        Writes a value to a signal at the specified address.  

        Args:
            address (int): The signal address.
            value (bool | int | float): The value to write.
        """
        return _s(address, value)
    
    async def load(self, path: str) -> None:
        """
        Loads a model.

        Args:
            path (str): The path to the model.
        """
        _l(path)
        await self._ws.write_frame(True, OP_BINARY, memoryview(self._wb)[:_ws()])
        _c()
        await self._ws.recv()
    
    async def reset(self) -> None:
        """
        Resets the simulation.
        """
        _r()
        await self._ws.write_frame(True, OP_BINARY, memoryview(self._wb)[:_ws()])
        _c()
        await self._ws.recv()

    async def initialize(self) -> None:
        """
        Manually initializes the simulation.
        """
        _i()
        await self._ws.write_frame(True, OP_BINARY, memoryview(self._wb)[:_ws()])
        _c()
        self._rb = await self._ws.recv()
        _u(self._rb)

    async def create_environments(self, entity_name: str, environment_count: int, *, pattern: Pattern = Pattern.NONE, spacing: float = 1) -> tuple[int, int]:
        """
        Creates multiple environments as duplicates of the entity with the specified name.

        Args:
            entity_name (str): The name of the entity to serve as the source for the environments.
            environment_count (int): The number of environments to create.
            pattern (Pattern, optional): The layout pattern that should be used when creating the environments. Defaults to Pattern.NONE.
            spacing (float, optional): The pattern spacing between environments. Defaults to 0.

        Returns:
            tuple[int, int, int, int]: The sgnal offset and stride for the environments along with the first and last signal address for the source environment.
        """
        _ce(entity_name, environment_count, pattern, spacing)
        await self._ws.write_frame(True, OP_BINARY, memoryview(self._wb)[:_ws()])
        _c()
        data = await self._ws.recv()
        offset = struct.unpack("I", data[12:16])[0]
        stride = struct.unpack("I", data[16:20])[0]
        first = struct.unpack("I", data[20:24])[0]
        last = struct.unpack("I", data[24:28])[0]
        return (offset, stride, first, last)

    async def reset_environment(self, environment_index: int) -> None:
        """
        Resets a specific environment back to its initial state.

        Args:
            environment_index (int): The index for the environment to reset.
        """
        _re(environment_index)
        await self._ws.write_frame(True, OP_BINARY, memoryview(self._wb)[:_ws()])
        _c()
        self._rb = await self._ws.recv()
        _u(self._rb)

    async def sync(self) -> None:
        """
        Synchronizes signals without stepping the simulation.
        """
        _y()
        await self._ws.write_frame(True, OP_BINARY, memoryview(self._wb)[:_ws()])
        _c()
        self._rb = await self._ws.recv()
        _u(self._rb)

    async def step(self) -> None:
        """
        Steps the simulation forward in time by one time-step.
        """
        _t()
        await self._ws.write_frame(True, OP_BINARY, memoryview(self._wb)[:_ws()])
        _c()
        self._rb = await self._ws.recv()
        _u(self._rb)

    async def start_step(self) -> None:
        """
        Starts the process of stepping the simulation forward in time.

        This may be used in combination with :func:`prototwin.Client.step_completed`
        to do some computation whilst the simulation is stepping.
        """
        _t()
        await self._ws.write_frame(True, OP_BINARY, self._wb)
        _c()

    async def step_completed(self) -> None:
        """
        Waits for the step to complete.
        
        Must only be called after :func:`prototwin.Client.start_step`
        """
        self._rb = await self._ws.recv()
        _u(self._rb)

    async def run(self, cb: Callable[[Self, float, float], bool|None]) -> None:
        """
        Runs the simulation a real-time speed.

        Args:
            cb (Callable[[Self, float, float], bool | None]): The callback function, executed every time-step.
        """
        start = time.perf_counter()
        t = 0
        dt = 0.01
        while True:
            await self.step()
            if cb(self, dt, t) == False:
                return
            t += dt
            st = t - (time.perf_counter() - start)
            if st > 0:
                _sleep(st)

async def start(location = "ProtoTwinConnect", *, port: int = 8084, dev: bool = False, tools: bool = False) -> Client|None:
    """
    Starts an instance of ProtoTwin Connect.

    Args:
        location (str, optional): The path to the ProtoTwin Connect executable. Defaults to "ProtoTwinConnect".
        dev (bool, optional): Whether to use the development environment. Defaults to False.

    Returns:
        Client|None: The created client, connected to the ProtoTwin Connect instance.
    """
    args = ["-runner"]
    if (dev):
        args.append("-dev")
    if (tools):
        args.append("-tools")
    if (port != 8084):
        args.append("-port=" + str(port))
    await asyncio.create_subprocess_exec(location, *args)
    await asyncio.sleep(2) # Allow a small amount of time to settle
    try:
        ws = await connect("ws://localhost:" + str(port), compression=None, user_agent_header="Python")
        await ws.recv() # Wait for ready signal
        client = Client(ws)
        return client
    except:
        return None
    
async def attach(*, port: int = 8084) -> Client|None:
    """
    Creates a client attached to a currently running instance of ProtoTwin Connect.

    Returns:
        Client|None: The created client.
    """
    try:
        ws = await connect("ws://localhost:" + str(port), compression=None, user_agent_header="Python")
        await ws.recv() # Wait for ready signal
        client = Client(ws)
        return client
    except:
        return None