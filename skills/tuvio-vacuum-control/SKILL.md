---
name: tuvio-vacuum-control
description: Управление локальным Tuvio/Tuya роботом-пылесосом через MCP-сервер и локальный хаб. Use when the user asks in Russian or English to check vacuum status, start/pause cleaning, send the vacuum to base, find it, change suction or water flow, switch voice prompts, use manual drive, reset consumable counters, or automate the Tuvio/TR07MGBW robot vacuum connected through the local hub.
---

# Tuvio Vacuum Control

Используйте MCP-сервер `tuvio-vacuum`, если он доступен. Он обращается к локальному хабу по адресу `http://127.0.0.1:8790` и не должен раскрывать Tuya local key, пароль роутера или токены.

## Рабочий порядок

1. Для проверки состояния вызывайте `vacuum_status`.
2. Для обычных команд используйте отдельные инструменты:
   - начать уборку: `vacuum_start`
   - пауза: `vacuum_pause`
   - на базу: `vacuum_home`
   - найти: `vacuum_find`
   - режим: `vacuum_set_mode`
   - мощность: `vacuum_set_suction`
   - подача воды: `vacuum_set_water`
   - ручное движение: `vacuum_drive`
   - голос: `vacuum_set_voice`
   - питание: `vacuum_set_power`
3. `vacuum_command` используйте только для известной сырой команды, если отдельного инструмента не хватает.
4. Перед сбросом счетчика фильтра или боковой щетки обязательно получите явное подтверждение пользователя. Затем вызывайте `vacuum_reset_consumable` с `confirm=true`.

## Соответствие русских команд

- `начни уборку`, `старт`, `убирайся` -> `vacuum_start`
- `пауза`, `останови уборку` -> `vacuum_pause`
- `на базу`, `домой`, `заряжаться` -> `vacuum_home`
- `найди пылесос`, `подай звук` -> `vacuum_find`
- `тихо`, `тихий режим` -> `vacuum_set_suction(level="quiet")`
- `норма`, `обычная мощность` -> `vacuum_set_suction(level="normal")`
- `сильно`, `максимальная мощность` -> `vacuum_set_suction(level="strong")`
- `вода минимум/средне/максимум` -> `vacuum_set_water(level="low/middle/high")`
- `авто`, `автоуборка` -> `vacuum_set_mode(mode="smart")`
- `вдоль стен`, `по стенам` -> `vacuum_set_mode(mode="wall_follow")`
- `пятно`, `спираль` -> `vacuum_set_mode(mode="spiral")`
- `вперед/назад/влево/вправо/стоп` -> `vacuum_drive`
- `голос включи/выключи` -> `vacuum_set_voice(enabled=true/false)`

## Ограничения

- Не обещайте карту квартиры, уборку по комнатам, запретные зоны, свои голосовые фразы, громкость голоса, выбор языка или датчик остатка воды в баке, если таких функций нет в схеме Tuya.
- Управление водой означает подачу воды на тряпку, а не уровень воды в баке.
- Ручное движение двигает физическое устройство. Используйте его только по явной просьбе пользователя.
- Сброс расходников меняет счетчики обслуживания и требует подтверждения.

## Резервный путь

Если MCP-инструменты недоступны, используйте API локального хаба:

- статус: `GET http://127.0.0.1:8790/api/devices`
- команда: `POST http://127.0.0.1:8790/api/tuya/command` с JSON `{"command":"start"}`

Не выводите и не сохраняйте в ответах `local_key`, пароль роутера или Tuya-токены.
