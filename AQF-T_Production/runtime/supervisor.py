"""
Supervisor + Heartbeat — V1.2 P0-1
Process guardian: crash detection / auto-restart / heartbeat / state recovery
"""
import time, signal, threading, sys, json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, Optional

@dataclass
class ComponentStatus:
    name: str
    alive: bool = False
    last_heartbeat: str = ""
    restart_count: int = 0
    max_restarts: int = 3
    errors: list = field(default_factory=list)

class Heartbeat:
    def __init__(self, name: str):
        self.name = name; self._last_beat: float = 0; self._lock = threading.Lock()
    def beat(self):
        with self._lock: self._last_beat = time.time()
    def age_seconds(self) -> float:
        with self._lock: return float("inf") if self._last_beat == 0 else time.time() - self._last_beat
    @property
    def is_alive(self, timeout: float = 30.0) -> bool:
        return self.age_seconds() < timeout

class Supervisor:
    def __init__(self, heartbeat_timeout: float = 30.0, max_restarts: int = 3):
        self.components: dict[str, ComponentStatus] = {}
        self.heartbeats: dict[str, Heartbeat] = {}
        self._running = False; self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.heartbeat_timeout = heartbeat_timeout; self.max_restarts = max_restarts
        self.snapshot_path = Path("runtime/supervisor_state.json")
        self._start_fns: dict[str, Callable] = {}
        self._stop_fns: dict[str, Callable] = {}
        self._check_fns: dict[str, Callable] = {}
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def register(self, name, start_fn, stop_fn=None, check_fn=None):
        with self._lock:
            self.components[name] = ComponentStatus(name=name, max_restarts=self.max_restarts)
            self.heartbeats[name] = Heartbeat(name)
            self._start_fns[name] = start_fn
            self._stop_fns[name] = stop_fn or (lambda: None)
            self._check_fns[name] = check_fn or (lambda: True)

    def start(self) -> bool:
        self._running = True
        for name in list(self.components.keys()):
            print(f"[Supervisor] Starting {name}...")
            try:
                self._start_fns[name]()
                self.components[name].alive = True
                self.components[name].last_heartbeat = datetime.now().isoformat()
                self.heartbeats[name].beat()
                print(f"[Supervisor] {name} - OK")
            except Exception as e:
                self.components[name].errors.append(str(e))
                print(f"[Supervisor] {name} - FAILED: {e}")
                if not self._try_restart(name): return False
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start(); self._save_snapshot(); return True

    def stop(self):
        self._running = False
        if self._thread: self._thread.join(timeout=5)
        for name in reversed(list(self.components.keys())):
            try: self._stop_fns[name]()
            except Exception: pass
        self._save_snapshot(); print("[Supervisor] Stopped.")

    def _monitor_loop(self):
        while self._running:
            time.sleep(5)
            with self._lock:
                for name, status in list(self.components.items()):
                    hb = self.heartbeats.get(name)
                    if hb is None: continue
                    if status.alive and not hb.is_alive(self.heartbeat_timeout):
                        print(f"[Supervisor] {name} - HEARTBEAT LOST ({hb.age_seconds():.0f}s)")
                        status.alive = False; self._try_restart(name)
                    if status.alive and name in self._check_fns:
                        try:
                            if not self._check_fns[name]():
                                print(f"[Supervisor] {name} - HEALTH FAILED")
                                status.alive = False; self._try_restart(name)
                        except Exception as e:
                            print(f"[Supervisor] {name} - HEALTH ERROR: {e}")
                            status.alive = False; self._try_restart(name)

    def _try_restart(self, name: str) -> bool:
        status = self.components[name]; status.restart_count += 1
        if status.restart_count > status.max_restarts:
            print(f"[Supervisor] {name} - MAX RESTARTS EXCEEDED"); return False
        print(f"[Supervisor] {name} - RESTARTING ({status.restart_count}/{status.max_restarts})...")
        try:
            self._start_fns[name](); status.alive = True
            status.last_heartbeat = datetime.now().isoformat()
            self.heartbeats[name].beat()
            print(f"[Supervisor] {name} - RECOVERED"); return True
        except Exception as e:
            status.errors.append(str(e)); return False

    def _save_snapshot(self):
        try:
            data = {"timestamp": datetime.now().isoformat(), "components": {
                name: {"alive": s.alive, "restart_count": s.restart_count,
                       "last_heartbeat": s.last_heartbeat, "errors": s.errors[-5:]}
                for name, s in self.components.items()}}
            self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.snapshot_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception: pass

    def status(self) -> dict:
        return {name: {"alive": s.alive, "restarts": s.restart_count,
                       "heartbeat_age": round(self.heartbeats[name].age_seconds(), 1)}
                for name, s in self.components.items()}

    def _handle_shutdown(self, signum, frame):
        print(f"\n[Supervisor] Signal {signum}. Shutting down...")
        self.stop(); sys.exit(0)
