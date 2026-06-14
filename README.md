# Tuvio Vacuum MCP + Skill

MCP-сервер и Codex skill для управления роботом-пылесосом Tuvio/Tuya через локальный хаб.

Проект не содержит ключей, токенов, QR-кодов и приватного состояния. MCP-сервер обращается к уже настроенному локальному хабу, а хаб хранит Tuya `device_id` и `local_key` у вас на компьютере.

## Что внутри

- `mcp_server/vacuum_mcp_server.py` - MCP-сервер `tuvio-vacuum`;
- `skills/tuvio-vacuum-control/SKILL.md` - skill для Codex;
- `examples/codex-config.example.toml` - пример секции для `~/.codex/config.toml`;
- `docs/authorization.md` - как получить авторизацию пылесоса до установки MCP;
- `docs/install.md` - установка MCP и skill;
- `docs/capabilities.md` - список возможностей.

## Быстрый старт

1. Получите `device_id` и `local_key` пылесоса и настройте локальный хаб. Подробно: [docs/authorization.md](docs/authorization.md).
2. Убедитесь, что хаб отвечает:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8790/api/devices
```

3. Установите зависимости:

```powershell
pip install -r requirements.txt
```

4. Добавьте MCP-сервер в `C:\Users\<USER>\.codex\config.toml` по примеру из [examples/codex-config.example.toml](examples/codex-config.example.toml).
5. Скопируйте `skills/tuvio-vacuum-control` в `C:\Users\<USER>\.codex\skills`.
6. Перезапустите Codex.

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

Этот MCP-сервер не реализует сам Tuya Cloud и не извлекает `local_key`. Он является безопасной прослойкой между Codex/MCP и уже работающим локальным хабом.

Карта квартиры, комнаты, запретные зоны, свои голосовые фразы, громкость голоса, выбор языка и датчик остатка воды в баке не поддерживаются, если их не отдает ваш Tuya-хаб.
