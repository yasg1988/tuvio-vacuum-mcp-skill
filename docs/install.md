# Установка

## 1. Клонирование

```powershell
git clone https://github.com/yasg1988/tuvio-vacuum-mcp-skill.git
cd tuvio-vacuum-mcp-skill
```

## 2. Python-зависимости

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Можно использовать и глобальный Python, если пакет `mcp` уже установлен.

## 3. Проверка локального хаба

Перед запуском MCP убедитесь, что хаб отвечает:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8790/api/devices
```

Если хаб на другом адресе, задайте переменную:

```powershell
$env:VACUUM_HUB_URL = "http://127.0.0.1:8790"
```

Хаб должен поддерживать API из [hub-api.md](hub-api.md). Без такого хаба MCP-сервер запустится, но команды будут возвращать ошибку подключения.

## 4. Подключение MCP в Codex

Откройте файл:

```text
C:\Users\<USER>\.codex\config.toml
```

Добавьте секцию:

```toml
[mcp_servers.tuvio-vacuum]
command = "python"
args = ["D:\\path\\to\\tuvio-vacuum-mcp-skill\\mcp_server\\vacuum_mcp_server.py"]
startup_timeout_ms = 20000

[mcp_servers.tuvio-vacuum.env]
VACUUM_HUB_URL = "http://127.0.0.1:8790"
```

После изменения `config.toml` перезапустите Codex.

## 5. Установка skill

Скопируйте папку:

```text
skills\tuvio-vacuum-control
```

в:

```text
C:\Users\<USER>\.codex\skills\tuvio-vacuum-control
```

После этого перезапустите Codex. Skill будет срабатывать на запросы вроде:

```text
проверь статус пылесоса
отправь пылесос на базу
поставь мощность тихо
включи голос у робота
```

## 6. Быстрая проверка

После перезапуска Codex спросите:

```text
проверь статус пылесоса
```

Если статус не читается, откройте [troubleshooting.md](troubleshooting.md).
