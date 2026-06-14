from __future__ import annotations

import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(BASE_DIR / ".env")


HUB_HOST = os.environ.get("HUB_HOST", "127.0.0.1")
HUB_PORT = int(os.environ.get("HUB_PORT", "8790"))


DPS_LABELS = {
    "1": "power",
    "2": "power_go",
    "3": "mode",
    "4": "direction_control",
    "5": "status",
    "6": "battery",
    "7": "edge_brush",
    "9": "filter",
    "14": "suction",
    "17": "clean_time",
    "18": "fault",
    "20": "cistern",
    "102": "voice_switch",
}


COMMANDS = {
    "power_on": {"1": True},
    "power_off": {"1": False},
    "start": {"2": True},
    "pause": {"2": False},
    "home": {"3": "chargego"},
    "mode_standby": {"3": "standby"},
    "mode_smart": {"3": "smart"},
    "mode_wall_follow": {"3": "wall_follow"},
    "mode_spiral": {"3": "spiral"},
    "direction_forward": {"4": "forward"},
    "direction_backward": {"4": "backward"},
    "direction_left": {"4": "turn_left"},
    "direction_right": {"4": "turn_right"},
    "direction_stop": {"4": "stop"},
    "reset_edge_brush": {"8": True},
    "reset_filter": {"10": True},
    "find": {"13": True},
    "suction_quiet": {"14": "quiet"},
    "suction_normal": {"14": "normal"},
    "suction_strong": {"14": "strong"},
    "water_low": {"20": "low"},
    "water_middle": {"20": "middle"},
    "water_high": {"20": "high"},
    "voice_on": {"102": True},
    "voice_off": {"102": False},
}


def config() -> dict[str, str]:
    return {
        "device_id": os.environ.get("TUYA_DEVICE_ID", "").strip(),
        "local_key": os.environ.get("TUYA_LOCAL_KEY", "").strip(),
        "ip": os.environ.get("TUYA_DEVICE_IP", "").strip(),
        "version": os.environ.get("TUYA_VERSION", "3.5").strip(),
        "name": os.environ.get("TUYA_DEVICE_NAME", "Tuvio TR07MGBW").strip(),
        "product_id": os.environ.get("TUYA_PRODUCT_ID", "").strip(),
    }


def public_config(cfg: dict[str, str]) -> dict[str, Any]:
    return {
        "device_id": cfg["device_id"],
        "local_key_saved": bool(cfg["local_key"]),
        "local_key": "",
        "product_id": cfg["product_id"],
        "name": cfg["name"],
        "version": cfg["version"],
        "ip": cfg["ip"],
    }


def tcp_open(ip: str, port: int, timeout: float = 1.0) -> bool:
    if not ip:
        return False
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def tuya_device():
    try:
        import tinytuya
    except ImportError as exc:
        raise RuntimeError("tinytuya не установлен. Выполните: pip install -r requirements.txt") from exc

    cfg = config()
    missing = [name for name in ("device_id", "local_key", "ip") if not cfg[name]]
    if missing:
        raise RuntimeError("не заполнены параметры хаба: " + ", ".join(missing))

    device = tinytuya.Device(cfg["device_id"], cfg["ip"], cfg["local_key"])
    device.set_version(float(cfg["version"]))
    return device


def tuya_status() -> dict[str, Any]:
    raw = tuya_device().status()
    dps = raw.get("dps", {}) if isinstance(raw, dict) else {}
    named = {DPS_LABELS.get(str(key), str(key)): value for key, value in dps.items()}
    return {"raw": raw, "dps": dps, "named": named}


def send_command(command: str) -> dict[str, Any]:
    payload = COMMANDS.get(command)
    if payload is None:
        raise RuntimeError(f"неизвестная команда: {command}")
    result = tuya_device().set_multiple_values(payload)
    return {"command": command, "payload": payload, "result": result}


def devices_payload() -> dict[str, Any]:
    cfg = config()
    tuya_live: dict[str, Any] | None
    try:
        tuya_live = tuya_status()
    except Exception as exc:
        tuya_live = {"error": str(exc), "named": {}, "dps": {}, "raw": None}

    online = tcp_open(cfg["ip"], 6668)
    return {
        "devices": [
            {
                "name": cfg["name"],
                "ip": cfg["ip"],
                "online": online,
                "role": "robot_vacuum",
                "tuya_port_6668": online,
                "product_id": cfg["product_id"],
            }
        ],
        "network": {"known": 1, "online": 1 if online else 0},
        "tuya": public_config(cfg),
        "tuya_live": tuya_live,
    }


def json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "TuvioMinimalHub/1.0"

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_json(200, {"ok": True})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self.send_json(200, {"ok": True, "hub": "tuvio-minimal"})
            return
        if path == "/api/devices":
            self.send_json(200, devices_payload())
            return
        self.send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/tuya/command":
            self.send_json(404, {"ok": False, "error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            command = str(payload.get("command", ""))
            result = send_command(command)
            status = tuya_status()
            self.send_json(200, {"ok": True, "result": result, "status": status})
        except Exception as exc:
            self.send_json(400, {"ok": False, "error": str(exc)})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    server = ThreadingHTTPServer((HUB_HOST, HUB_PORT), Handler)
    print(f"Tuvio minimal hub: http://{HUB_HOST}:{HUB_PORT}")
    print("Проверка: GET /api/devices")
    server.serve_forever()


if __name__ == "__main__":
    main()
