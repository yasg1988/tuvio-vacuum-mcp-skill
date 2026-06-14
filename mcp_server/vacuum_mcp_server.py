from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP


HUB_URL = os.environ.get("VACUUM_HUB_URL", "http://127.0.0.1:8790").rstrip("/")

mcp = FastMCP("tuvio-vacuum")


COMMANDS = {
    "power_on",
    "power_off",
    "start",
    "pause",
    "home",
    "find",
    "mode_standby",
    "mode_smart",
    "mode_wall_follow",
    "mode_spiral",
    "direction_forward",
    "direction_backward",
    "direction_left",
    "direction_right",
    "direction_stop",
    "suction_quiet",
    "suction_normal",
    "suction_strong",
    "water_low",
    "water_middle",
    "water_high",
    "voice_on",
    "voice_off",
    "reset_edge_brush",
    "reset_filter",
}

MODE_COMMANDS = {
    "standby": "mode_standby",
    "smart": "mode_smart",
    "auto": "mode_smart",
    "wall_follow": "mode_wall_follow",
    "walls": "mode_wall_follow",
    "spiral": "mode_spiral",
    "spot": "mode_spiral",
    "chargego": "home",
    "home": "home",
}

SUCTION_COMMANDS = {
    "quiet": "suction_quiet",
    "normal": "suction_normal",
    "strong": "suction_strong",
}

WATER_COMMANDS = {
    "low": "water_low",
    "middle": "water_middle",
    "medium": "water_middle",
    "high": "water_high",
}

DIRECTION_COMMANDS = {
    "forward": "direction_forward",
    "backward": "direction_backward",
    "left": "direction_left",
    "right": "direction_right",
    "stop": "direction_stop",
}

RU_VALUES = {
    "charging": "заряжается",
    "charge_done": "заряжен",
    "goto_charge": "едет на базу",
    "cleaning": "убирает",
    "paused": "пауза",
    "standby": "ожидание",
    "sleep": "сон",
    "sleeping": "сон",
    "fault": "ошибка",
    "smart_clean": "автоуборка",
    "wall_clean": "уборка вдоль стен",
    "spot_clean": "уборка пятна",
    "mop_clean": "влажная уборка",
    "smart": "авто",
    "wall_follow": "вдоль стен",
    "spiral": "пятно",
    "chargego": "на базу",
    "forward": "вперед",
    "backward": "назад",
    "turn_left": "влево",
    "turn_right": "вправо",
    "stop": "стоп",
    "quiet": "тихо",
    "normal": "норма",
    "strong": "сильно",
    "low": "минимум",
    "middle": "средне",
    "high": "максимум",
}


def request_json(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{HUB_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"локальный хаб вернул HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"локальный хаб недоступен по адресу {HUB_URL}: {exc.reason}") from exc


def russian(value: Any) -> Any:
    if isinstance(value, bool):
        return "вкл" if value else "выкл"
    if isinstance(value, str):
        return RU_VALUES.get(value, value)
    if value == 0:
        return "нет"
    return value


def compact_status(payload: dict[str, Any]) -> dict[str, Any]:
    live = payload.get("tuya_live") or {}
    named = live.get("named") or {}
    return {
        "status": russian(named.get("status")),
        "mode": russian(named.get("mode")),
        "direction": russian(named.get("direction_control")),
        "battery_percent": named.get("battery"),
        "cleaning": "идет" if named.get("power_go") else "нет",
        "suction": russian(named.get("suction")),
        "water_flow": russian(named.get("cistern")),
        "voice": russian(named.get("voice_switch")),
        "clean_time_minutes": named.get("clean_time"),
        "fault": russian(named.get("fault")),
        "edge_brush_percent": named.get("edge_brush"),
        "filter_percent": named.get("filter"),
        "raw_named": named,
    }


def send(command: str) -> dict[str, Any]:
    if command not in COMMANDS:
        raise ValueError(f"неизвестная команда: {command}")
    payload = request_json("/api/tuya/command", "POST", {"command": command})
    if not payload.get("ok"):
        raise RuntimeError(payload.get("error") or "команда не выполнена")
    status = payload.get("status") or {}
    return {"ok": True, "command": command, "status": compact_status({"tuya_live": status})}


@mcp.tool()
def vacuum_status() -> dict[str, Any]:
    """Вернуть текущий статус робота-пылесоса Tuvio из локального хаба."""
    payload = request_json("/api/devices")
    return compact_status(payload)


@mcp.tool()
def vacuum_command(command: str) -> dict[str, Any]:
    """Выполнить сырую поддерживаемую команду: start, pause, home, find, suction_strong, water_high и т.д."""
    return send(command)


@mcp.tool()
def vacuum_start() -> dict[str, Any]:
    """Начать уборку."""
    return send("start")


@mcp.tool()
def vacuum_pause() -> dict[str, Any]:
    """Поставить уборку на паузу."""
    return send("pause")


@mcp.tool()
def vacuum_home() -> dict[str, Any]:
    """Отправить робот-пылесос на базу."""
    return send("home")


@mcp.tool()
def vacuum_find() -> dict[str, Any]:
    """Включить штатный поиск робота звуком."""
    return send("find")


@mcp.tool()
def vacuum_set_mode(mode: str) -> dict[str, Any]:
    """Установить режим: smart/auto, wall_follow/walls, spiral/spot, standby, home/chargego."""
    command = MODE_COMMANDS.get(mode)
    if not command:
        raise ValueError(f"неподдерживаемый режим: {mode}")
    return send(command)


@mcp.tool()
def vacuum_set_suction(level: str) -> dict[str, Any]:
    """Установить мощность всасывания: quiet, normal, strong."""
    command = SUCTION_COMMANDS.get(level)
    if not command:
        raise ValueError(f"неподдерживаемый уровень мощности: {level}")
    return send(command)


@mcp.tool()
def vacuum_set_water(level: str) -> dict[str, Any]:
    """Установить подачу воды для влажной уборки: low, middle/medium, high."""
    command = WATER_COMMANDS.get(level)
    if not command:
        raise ValueError(f"неподдерживаемый уровень подачи воды: {level}")
    return send(command)


@mcp.tool()
def vacuum_drive(direction: str) -> dict[str, Any]:
    """Ручное движение: forward, backward, left, right, stop."""
    command = DIRECTION_COMMANDS.get(direction)
    if not command:
        raise ValueError(f"неподдерживаемое направление: {direction}")
    return send(command)


@mcp.tool()
def vacuum_set_voice(enabled: bool) -> dict[str, Any]:
    """Включить или выключить штатные голосовые подсказки робота."""
    return send("voice_on" if enabled else "voice_off")


@mcp.tool()
def vacuum_set_power(enabled: bool) -> dict[str, Any]:
    """Включить или выключить питание робота."""
    return send("power_on" if enabled else "power_off")


@mcp.tool()
def vacuum_reset_consumable(consumable: str, confirm: bool = False) -> dict[str, Any]:
    """Сбросить счетчик фильтра или боковой щетки. Требуется confirm=true."""
    if not confirm:
        raise ValueError("для сброса счетчика требуется confirm=true")
    if consumable == "filter":
        return send("reset_filter")
    if consumable in {"edge_brush", "brush"}:
        return send("reset_edge_brush")
    raise ValueError(f"неподдерживаемый расходник: {consumable}")


if __name__ == "__main__":
    mcp.run()
