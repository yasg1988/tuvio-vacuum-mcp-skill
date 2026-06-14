# Tuvio Vacuum MCP + Skill

MCP-сервер и Codex skill для управления роботом-пылесосом Tuvio/Tuya через локальный хаб.

Проект не содержит ключей, токенов, QR-кодов и приватного состояния. MCP-сервер обращается к уже настроенному локальному хабу, а хаб хранит Tuya `device_id` и `local_key` у вас на компьютере.

## Что внутри

- `mcp_server/vacuum_mcp_server.py` - MCP-сервер `tuvio-vacuum`;
- `hub/minimal_hub.py` - минимальный локальный HTTP-хаб для одного пылесоса;
- `skills/tuvio-vacuum-control/SKILL.md` - skill для Codex;
- `examples/codex-config.example.toml` - пример секции для `~/.codex/config.toml`;
- `docs/authorization.md` - как получить авторизацию пылесоса до установки MCP;
- `docs/minimal-hub.md` - как запустить встроенный минимальный хаб;
- `docs/install.md` - установка MCP и skill;
- `docs/capabilities.md` - список возможностей.

## Быстрый старт

1. Получите `device_id` и `local_key` пылесоса. Подробно: [docs/authorization.md](docs/authorization.md).
2. Установите зависимости:

```powershell
pip install -r requirements.txt
```

3. Запустите встроенный минимальный хаб или свой совместимый хаб. Подробно: [docs/minimal-hub.md](docs/minimal-hub.md).
4. Убедитесь, что хаб отвечает:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8790/api/devices
```

5. Добавьте MCP-сервер в `C:\Users\<USER>\.codex\config.toml` по примеру из [examples/codex-config.example.toml](examples/codex-config.example.toml).
6. Скопируйте `skills/tuvio-vacuum-control` в `C:\Users\<USER>\.codex\skills`.
7. Перезапустите Codex.

## Что нужно новому владельцу Tuvio TR07MGBW

Этот репозиторий содержит MCP-сервер, Codex skill и минимальный локальный HTTP-хаб для одного пылесоса. Если у вас уже есть свой хаб, можно использовать его вместо встроенного.

Для рабочего запуска нужны:

- пылесос, добавленный в Smart Life / Tuya Smart / Tuya Home или совместимое OEM-приложение;
- `device_id` и актуальный `local_key`;
- встроенный хаб из [docs/minimal-hub.md](docs/minimal-hub.md) или свой локальный хаб с API из [docs/hub-api.md](docs/hub-api.md);
- Python 3.10+ и доступ Codex к MCP-серверу.

Если после удаления или повторной привязки пылесоса команды перестали работать с ошибкой вида `Check device key or version`, получите новый `local_key` и обновите конфиг хаба. После перепривязки Tuya часто меняет локальный ключ.

## Команды MCP

- `vacuum_status`
- `vacuum_start`
- `vacuum_pause`
- `vacuum_home`
- `vacuum_find`
- `vacuum_set_mode`
- `vacuum_set_suction`
- `vacuum_set_water`
- `vacuum_drive`
- `vacuum_set_voice`
- `vacuum_set_power`
- `vacuum_reset_consumable`
- `vacuum_command`

## Безопасность

Не коммитьте:

- Tuya `local_key`;
- Tuya Client Secret;
- пароль роутера;
- `hub_state.json`;
- QR-коды авторизации;
- cookies и временные ответы Tuya Cloud.

Для локальных секретов используйте приватный конфиг хаба, `.env` или менеджер секретов.

## Ограничения

Этот MCP-сервер не реализует сам Tuya Cloud и не извлекает `local_key`. Встроенный минимальный хаб тоже не получает ключ автоматически: он использует значения, которые вы укажете локально в `hub/.env`.

Карта квартиры, комнаты, запретные зоны, свои голосовые фразы, громкость голоса, выбор языка и датчик остатка воды в баке не поддерживаются, если их не отдает ваш Tuya-хаб.
