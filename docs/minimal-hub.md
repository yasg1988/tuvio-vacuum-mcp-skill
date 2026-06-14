# Минимальный локальный хаб

В репозитории есть простой HTTP-хаб `hub/minimal_hub.py`. Он подключается к роботу напрямую через Tuya LAN (`tinytuya`) и предоставляет API, который использует MCP-сервер.

## Установка

```powershell
git clone https://github.com/yasg1988/tuvio-vacuum-mcp-skill.git
cd tuvio-vacuum-mcp-skill
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Настройка

Скопируйте пример конфига:

```powershell
Copy-Item hub\.env.example hub\.env
```

Откройте `hub\.env` и заполните:

```text
TUYA_DEVICE_ID=...
TUYA_LOCAL_KEY=...
TUYA_DEVICE_IP=...
TUYA_VERSION=3.5
```

`TUYA_DEVICE_ID` и `TUYA_LOCAL_KEY` получите по инструкции [authorization.md](authorization.md). `hub\.env` нельзя коммитить в GitHub.

## Запуск

```powershell
python hub\minimal_hub.py
```

По умолчанию хаб поднимется на:

```text
http://127.0.0.1:8790
```

## Проверка

Статус:

```powershell
Invoke-RestMethod http://127.0.0.1:8790/api/devices
```

Безопасная команда поиска пылесоса:

```powershell
Invoke-RestMethod http://127.0.0.1:8790/api/tuya/command `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"command":"find"}'
```

Если статус содержит `Check device key or version`, получите новый `local_key` и проверьте `TUYA_VERSION`.

## Подключение MCP

После запуска хаба MCP-сервер можно подключить так:

```toml
[mcp_servers.tuvio-vacuum]
command = "python"
args = ["D:\\path\\to\\tuvio-vacuum-mcp-skill\\mcp_server\\vacuum_mcp_server.py"]
startup_timeout_ms = 20000

[mcp_servers.tuvio-vacuum.env]
VACUUM_HUB_URL = "http://127.0.0.1:8790"
```

## Ограничения

Минимальный хаб не делает сканирование сети, не получает `local_key` из Tuya Cloud и не хранит историю. Его задача - дать рабочий локальный API для одного пылесоса Tuvio/Tuya.
