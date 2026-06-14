# Контракт локального хаба

MCP-сервер из этого репозитория не подключается к Tuya Cloud напрямую. Он вызывает локальный хаб по HTTP. По умолчанию используется:

```text
http://127.0.0.1:8790
```

Адрес можно изменить переменной окружения:

```powershell
$env:VACUUM_HUB_URL = "http://127.0.0.1:8790"
```

## Обязательные endpoints

### `GET /api/devices`

Должен вернуть JSON со статусом пылесоса. MCP использует поле `tuya_live.named`.

Минимальный пример:

```json
{
  "tuya_live": {
    "named": {
      "power": true,
      "power_go": false,
      "mode": "standby",
      "direction_control": "forward",
      "status": "charging",
      "battery": 99,
      "edge_brush": 94,
      "filter": 94,
      "suction": "strong",
      "clean_time": 0,
      "fault": 0,
      "cistern": "high",
      "voice_switch": true
    }
  }
}
```

### `POST /api/tuya/command`

Должен принять JSON:

```json
{"command":"find"}
```

И вернуть:

```json
{
  "ok": true,
  "status": {
    "named": {
      "status": "charging",
      "battery": 99
    }
  }
}
```

Если команда не выполнена, верните:

```json
{
  "ok": false,
  "error": "описание ошибки"
}
```

## Команды, которые ожидает MCP

- `power_on`, `power_off`;
- `start`, `pause`, `home`, `find`;
- `mode_standby`, `mode_smart`, `mode_wall_follow`, `mode_spiral`;
- `direction_forward`, `direction_backward`, `direction_left`, `direction_right`, `direction_stop`;
- `suction_quiet`, `suction_normal`, `suction_strong`;
- `water_low`, `water_middle`, `water_high`;
- `voice_on`, `voice_off`;
- `reset_edge_brush`, `reset_filter`.

## Безопасность

Хаб может хранить `device_id`, `local_key`, Tuya Client Secret и пароль роутера, но не должен отдавать эти значения через публичные ответы API. MCP-серверу достаточно статуса и результата команды.
