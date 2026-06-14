# Диагностика

## Хаб не отвечает

Проверьте:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8790/api/devices
```

Если хаб запущен на другом адресе, укажите его:

```powershell
$env:VACUUM_HUB_URL = "http://192.168.8.10:8790"
```

## Ошибка `Check device key or version`

Обычно это значит, что `local_key` устарел или выбран неправильный Tuya LAN protocol version.

Частая причина - пылесос удалили из приложения и привязали заново. После такой операции `device_id` может остаться прежним, но `local_key` меняется.

Что сделать:

1. Снова привяжите аккаунт Smart Life / Tuya Smart / Tuya Home к Tuya IoT Project через QR-код.
2. Убедитесь, что дата-центр проекта совпадает с дата-центром аккаунта приложения.
3. Получите новый `local_key` через Device Management API или `tinytuya wizard`.
4. Обновите локальный хаб.
5. Повторите проверку `GET /api/devices`.

## Устройство не появляется в Tuya IoT Project

Проверьте:

- выбран правильный дата-центр проекта;
- пылесос добавлен именно в тот аккаунт приложения, QR-кодом которого вы авторизуетесь;
- вы не используете гостевой доступ к устройству;
- приложение совместимо с Tuya Cloud. Для OEM-приложений может потребоваться Smart Life / Tuya Smart / Tuya Home.

## MCP запускается, но инструментов не видно

Проверьте путь в `C:\Users\<USER>\.codex\config.toml`.

Пример:

```toml
[mcp_servers.tuvio-vacuum]
command = "python"
args = ["D:\\path\\to\\tuvio-vacuum-mcp-skill\\mcp_server\\vacuum_mcp_server.py"]
startup_timeout_ms = 20000

[mcp_servers.tuvio-vacuum.env]
VACUUM_HUB_URL = "http://127.0.0.1:8790"
```

После изменения конфига перезапустите Codex.
