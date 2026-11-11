# git-practice1-variant5

Учебное Python-приложение из практической работы № 1. В практической
работе № 2 в репозиторий добавлен CI/CD на GitHub Actions.
Изменения по версиям перечислены в [истории версий](CHANGELOG.md).

## Запуск приложения

Для приложения и CI используется Python 3.12 и стандартная библиотека.
Команды выполняются из корня репозитория.

```bash
python main.py
python main.py --status-json
python main.py --version
python main.py --help
python -m scripts.check_project
```

Приложение выводит название и статус настройки PostgreSQL. Модули уведомлений
и отчётов возвращают демонстрационные строки.

`--status-json` возвращает JSON с ключами `name`, `version` и
`database_status`. `--version` печатает только номер версии. Эти режимы
запускаются отдельно. Для списка поддерживаемых параметров используйте `--help`.

## Документация

```bash
python -m scripts.build_docs --output build/docs
```

Откройте `build/docs/index.html` в браузере. В HTML попадают версия из
`config.py`, сигнатуры и описания публичных функций. В GitHub Actions также
добавляется SHA проверяемого коммита.

## CI/CD

`.github/workflows/main.yml` проверяет запуск приложения и собирает HTML
при push в любую ветвь и при открытии или обновлении pull request в `main`.
Скрипт проверки запускает `main.py --status-json` и сверяет значения полей.
Документация доступна в разделе **Artifacts** как `project-docs`.

Готовые pull request из ветвей `development` и `release` этого репозитория
вливаются в `main` заданием **Merge verified pull request** после успешной
проверки. Задание сверяет ревизии ветвей и запускает контрольный CI на `main`
после слияния. Черновики и pull request из форков проходят без этого задания.

Для публикации тега откройте **Actions → Python CI/CD → Run workflow**,
выберите `main` и отметьте `publish_tag`. После проверки GitHub создаст
тег вида `v0.3.0` из версии в `config.py` на проверенном коммите `main`.
