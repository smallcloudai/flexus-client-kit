import asyncio
import hashlib
import json
import logging
import uuid
from typing import Optional

logger = logging.getLogger("devenv_rpc")

_RESPONSE_QUEUE_MAX = 1000


def _make_session_id(fuser_id: str, devenv_id: str, nonce: str = "") -> str:
    raw = f"{fuser_id}:{devenv_id}:{nonce}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


_RPC_CHANNELS = {"bot", "pod"}


class DevenvRpcSession:
    def __init__(self, devenv_id: str, fuser_id: str, redis=None, nonce: str = ""):
        self.devenv_id = devenv_id
        self.fuser_id = fuser_id
        self.session_id = _make_session_id(fuser_id, devenv_id, nonce)
        self._redis = redis
        self._pubsub = None
        self._connected = False
        self._response_queue: asyncio.Queue = asyncio.Queue(maxsize=_RESPONSE_QUEUE_MAX)
        self._listener_task: Optional[asyncio.Task] = None

    @property
    def cmd_ch(self):
        return f"devenv_{self.session_id}_cmd"

    @property
    def res_ch(self):
        return f"devenv_{self.session_id}_res"

    async def connect(self, redis=None, timeout: float = 120.0,
                      initial_branch: str = "", working_branch: str = ""):
        if redis:
            self._redis = redis
        if not self._redis:
            raise RuntimeError("Redis client required")

        self._pubsub = self._redis.pubsub()
        await self._pubsub.subscribe(self.res_ch)

        self._listener_task = asyncio.create_task(self._listen_loop())
        self._listener_task.add_done_callback(self._on_listener_done)

        connect_msg = {
            "op": "connect",
            "fuser_id": self.fuser_id,
            "devenv_id": self.devenv_id,
            "session_id": self.session_id,
        }
        if initial_branch:
            connect_msg["initial_branch"] = initial_branch
        if working_branch:
            connect_msg["working_branch"] = working_branch
        await self._redis.publish("devenv_control", json.dumps(connect_msg))
        logger.info("devenv rpc connect sent for %s session=%s", self.devenv_id, self.session_id)

        # Wait for pod ready or revived, re-queuing non-pod messages
        deadline = asyncio.get_event_loop().time() + timeout
        deferred: list[dict] = []
        try:
            while asyncio.get_event_loop().time() < deadline:
                try:
                    msg = await asyncio.wait_for(self._response_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    if not self._is_listener_alive():
                        raise RuntimeError("Listener task died during connect")
                    continue
                ch = msg.get("ch", "")
                op = msg.get("op", "")
                if ch == "pod" and op in ("ready", "revived"):
                    self._connected = True
                    logger.info("devenv rpc connected, pod ready for %s", self.devenv_id)
                    return
                if ch == "pod" and op == "error":
                    raise RuntimeError(f"Pod error: {msg.get('error', 'unknown')}")
                if ch == "pod" and op == "progress":
                    logger.info("devenv pod progress: %s", msg.get("text", ""))
                else:
                    deferred.append(msg)
        finally:
            for m in deferred:
                try:
                    self._response_queue.put_nowait(m)
                except asyncio.QueueFull:
                    logger.warning("devenv rpc queue full, dropping deferred message: %s", m.get("op", ""))

        raise TimeoutError(f"Timeout waiting for devenv pod {self.devenv_id}")

    def _on_listener_done(self, task: asyncio.Task):
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            logger.error("devenv rpc listener died unexpectedly: %s", exc)
            self._connected = False

    def _is_listener_alive(self) -> bool:
        return self._listener_task is not None and not self._listener_task.done()

    async def _listen_loop(self):
        try:
            while True:
                try:
                    msg = await self._pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=1.0,
                    )
                except Exception as e:
                    logger.warning("devenv rpc pubsub read error: %s", e)
                    await asyncio.sleep(1.0)
                    continue
                if msg is None:
                    await asyncio.sleep(0.01)
                    continue
                if msg["type"] != "message":
                    continue
                try:
                    data = json.loads(msg["data"])
                except (json.JSONDecodeError, TypeError):
                    continue
                if data.get("ch", "") not in _RPC_CHANNELS:
                    continue
                try:
                    self._response_queue.put_nowait(data)
                except asyncio.QueueFull:
                    logger.warning("devenv rpc queue full, dropping: ch=%s op=%s", data.get("ch", ""), data.get("op", ""))
        except asyncio.CancelledError:
            pass

    async def _send(self, ch: str, op: str, **kwargs):
        if not self._is_listener_alive():
            raise RuntimeError("DevenvRpcSession listener is not running")
        payload = {"ch": ch, "op": op, **kwargs}
        await self._redis.publish(self.cmd_ch, json.dumps(payload))

    async def _wait_response(self, ch: str, op: str, timeout: float = 300.0, request_id: str | None = None) -> dict:
        deadline = asyncio.get_event_loop().time() + timeout
        unmatched: list[dict] = []
        try:
            while asyncio.get_event_loop().time() < deadline:
                if not self._is_listener_alive():
                    raise RuntimeError("DevenvRpcSession listener died while waiting for response")
                remaining = max(0.1, deadline - asyncio.get_event_loop().time())
                try:
                    msg = await asyncio.wait_for(self._response_queue.get(), timeout=min(remaining, 5.0))
                except asyncio.TimeoutError:
                    continue
                msg_ch = msg.get("ch", "")
                msg_op = msg.get("op", "")
                if msg_ch == ch and msg_op == op:
                    if request_id and msg.get("request_id") != request_id:
                        unmatched.append(msg)
                        continue
                    return msg
                if msg_ch == ch and msg_op == "error":
                    if request_id and msg.get("request_id") and msg.get("request_id") != request_id:
                        unmatched.append(msg)
                        continue
                    return msg
                unmatched.append(msg)
            raise TimeoutError(f"Timeout waiting for {ch}/{op}")
        finally:
            for m in unmatched:
                try:
                    self._response_queue.put_nowait(m)
                except asyncio.QueueFull:
                    pass

    async def bash(self, command: str, timeout: int = 120) -> tuple[str, int]:
        """Run bash command in the pod. Returns (output, exit_code)."""
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "bash", command=command, timeout=timeout, request_id=request_id)
        resp = await self._wait_response("bot", "bash_result", timeout=timeout + 30, request_id=request_id)
        if resp.get("op") == "error":
            return resp.get("error", "unknown error"), 1
        return resp.get("output", ""), resp.get("exit_code", 1)

    async def discover_bots(self) -> list[dict]:
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "discover", request_id=request_id)
        resp = await self._wait_response("bot", "discovered", timeout=60, request_id=request_id)
        if resp.get("op") == "error":
            return []
        return resp.get("bots", [])

    async def bot_start(self, bot_path: str) -> dict:
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "start", bot_path=bot_path, request_id=request_id)
        return await self._wait_response("bot", "started", timeout=30, request_id=request_id)

    async def bot_stop(self) -> dict:
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "stop", request_id=request_id)
        return await self._wait_response("bot", "stopped", timeout=30, request_id=request_id)

    async def bot_restart(self, bot_path: str) -> dict:
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "restart", bot_path=bot_path, request_id=request_id)
        return await self._wait_response("bot", "started", timeout=30, request_id=request_id)

    async def bot_install(self, bot_path: str) -> dict:
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "install", bot_path=bot_path, request_id=request_id)
        return await self._wait_response("bot", "install_output", timeout=300, request_id=request_id)

    async def bot_logs(self) -> list[str]:
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "logs", request_id=request_id)
        resp = await self._wait_response("bot", "log_lines", timeout=30, request_id=request_id)
        return resp.get("lines", [])

    async def bot_status(self) -> dict:
        request_id = uuid.uuid4().hex[:12]
        await self._send("bot", "status", request_id=request_id)
        return await self._wait_response("bot", "status", timeout=30, request_id=request_id)

    async def kill_pod(self) -> dict:
        request_id = uuid.uuid4().hex[:12]
        await self._send("pod", "kill", request_id=request_id)
        return await self._wait_response("pod", "killed", timeout=60, request_id=request_id)

    async def pod_status(self) -> dict:
        request_id = uuid.uuid4().hex[:12]
        await self._send("pod", "status", request_id=request_id)
        return await self._wait_response("pod", "status", timeout=30, request_id=request_id)

    async def disconnect(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
        if self._pubsub:
            try:
                await self._pubsub.unsubscribe(self.res_ch)
            except Exception:
                pass
            self._pubsub = None
        if self._redis:
            try:
                await self._redis.publish("devenv_control", json.dumps({
                    "op": "disconnect",
                    "session_id": self.session_id,
                    "devenv_id": self.devenv_id,
                    "fuser_id": self.fuser_id,
                }))
            except Exception:
                pass
        self._connected = False
        logger.info("devenv rpc disconnected for %s", self.devenv_id)
