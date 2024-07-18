import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Coroutine, Protocol, cast

import aiohttp
from websockets.exceptions import ConnectionClosed
from aiohttp import web

import relationalai
from relationalai.clients.client import ResourceProvider
from relationalai.debugging import encode_log_message

PROJECT_ROOT = Path(relationalai.__file__).resolve()

# This is weird and dynamic because the frontend directory is in different
# places depending on whether you're running with `-e`, or install a package.
max_ancestor_steps = 3
FRONTEND_PATH = PROJECT_ROOT
while not (FRONTEND_PATH / "frontend").exists() and max_ancestor_steps > 0:
    FRONTEND_PATH = FRONTEND_PATH.parent
    max_ancestor_steps -= 1

HTTP_DIST_DIR = FRONTEND_PATH / "frontend" / "debugger" / "dist"

# The maximum number of messages to be sent at once when catching a new client up
MAX_BATCH_SIZE = 500

_resources: ResourceProvider|None = None

def get_resources() -> ResourceProvider:
    if not _resources:
        raise Exception("Unable to acquire resources")

    return _resources

#------------------------------------------------------------------------------
# Program Connections
#------------------------------------------------------------------------------

connected_program = None

async def handle_program(req: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(req)

    global connected_program
    if connected_program:
        print("Refusing to connect to new program until previous one finishes.")
        await ws.close()

    connected_program = ws
    print("Program connected")
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await broadcast(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                err = ws.exception()
                if err:
                    raise err
            else:
                raise Exception("Unknown message type", msg.type)
    finally:
        print("Program disconnected")
        connected_program = None

    return ws

#------------------------------------------------------------------------------
# Browser Client Connections
#------------------------------------------------------------------------------

connected_clients: set[web.WebSocketResponse] = set()

async def handle_client(req: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(req)
    connected_clients.add(ws)
    try:
        for i in range(0, len(buffered_broadcasts), MAX_BATCH_SIZE):
            chunk = ",".join(buffered_broadcasts[i:i + MAX_BATCH_SIZE])
            await ws.send_str(f"[{chunk}]")

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await handle_client_action(msg.data, ws)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                err = ws.exception()
                if err:
                    raise err
            else:
                raise Exception("Unknown message type", msg.type)

    except ConnectionClosed as e:
        print(f"Client disconnected with reason: {e}")
    finally:
        connected_clients.remove(ws)

    return ws

class NoSuchActionError(KeyError):
    def __init__(self, action: str|None):
        super().__init__(f"Got action request from client for non-existent action of type '{action}'")

async def handle_client_action(msg: Any, ws: web.WebSocketResponse):
    parsed = None
    try:
        parsed = json.loads(msg)
        action_type = parsed.get("type")
        action = client_actions.get(action_type)
        if not action:
            raise NoSuchActionError(action_type)
        kwargs = {k: v for k, v in parsed.items() if k != "type" and k != "rpc_id"}
        res = action(ws, **kwargs) or {}

    except Exception as e:
        print("Error:", str(e))
        res = {"error": str(e)}

    if parsed:
        if asyncio.iscoroutine(res):
            res = await res

        res = cast(dict, res)
        res["event"] = "rpc_response"
        res["rpc_id"] = parsed.get("rpc_id")

        def dump_json(v):
            return json.dumps(v, default=encode_log_message)

        await ws.send_json([res], None, dumps=dump_json)

#------------------------------------------------------------------------------
# Browser Client Actions
#------------------------------------------------------------------------------

ClientActionReturn = Coroutine[Any, Any, dict|None]|dict|None

class ClientAction(Protocol):
    def __call__(self, ws: web.WebSocketResponse, **kwargs: Any) -> ClientActionReturn:
        ...

client_actions: dict[str, ClientAction] = {}

def client_action(name: str|None = None):
    def decorator(fn: Callable[..., ClientActionReturn]):
        client_actions[name or fn.__name__] = fn

    return decorator

@client_action()
def clear(_):
    buffered_broadcasts.clear()

@client_action()
def list_transactions(_, **kwargs):
    return {"transactions": get_resources().list_transactions(**kwargs)}

@client_action()
def list_imports(_, **kwargs):
    return {"imports": get_resources().list_imports(**kwargs)}

@client_action()
def get_imports_status(_, **kwargs):
    return {"imports_status": get_resources().get_imports_status(**kwargs)}

#------------------------------------------------------------------------------
# Event Log
#------------------------------------------------------------------------------

buffered_broadcasts = []

async def broadcast(message):
    buffered_broadcasts.append(message)
    if connected_clients:
        tasks = [asyncio.create_task(client.send_str(f"[{message}]" )) for client in connected_clients]
        await asyncio.wait(tasks)

#------------------------------------------------------------------------------
# Server
#------------------------------------------------------------------------------

async def serve_index(_):
    return web.FileResponse(HTTP_DIST_DIR / "index.html")

runner: web.AppRunner|None = None
async def run_server(host: str, port: int):
    global runner
    if runner:
        await runner.shutdown()

    app = web.Application()
    app.router.add_get("/ws/program", handle_program)
    app.router.add_get("/ws/client", handle_client)
    app.router.add_get("/", serve_index)
    app.router.add_static("/", HTTP_DIST_DIR, show_index=False)  # Serving static files from DIR
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    print(f"Server started at http://{host}:{port}")

    return runner

def start_server(host: str, port: int, profile:str|None = None):
    global _resources
    _resources = relationalai.Resources(profile)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_server(host, port))
    loop.run_forever()


def stop_server():
    global runner
    if not runner:
        return

    loop = asyncio.get_running_loop()
    loop.run_until_complete(broadcast(json.dumps({"event": "debug_server_closed"})))
    loop.run_until_complete(runner.shutdown())
    runner = None
