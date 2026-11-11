# git-practice1-variant5

Учебное Python-приложение из практической работы № 1. В практической
работе № 2 в репозиторий добавлен CI/CD на GitHub Actions.
Изменения по версиям перечислены в [истории версий](CHANGELOG.md).

## Запуск приложения

Для приложения и тестов нужен Python 3.12. Используется стандартная библиотека.
Команды выполняются из корня репозитория.

```bash
python main.py
python main.py --status-json
python main.py --version
python main.py --help
python -m unittest discover -s tests -v
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

`.github/workflows/main.yml` запускает тесты и сборку HTML при push в любую
ветвь, при push тега `v*` и при обновлении pull request в `main`. Документация
доступна в разделе **Artifacts** успешного запуска как `project-docs`.

Готовые pull request из ветвей `development` и `release` этого репозитория
вливаются в `main` заданием **Merge tested pull request** после успешной
проверки. Задание сверяет ревизии ветвей и запускает контрольный CI на `main`
после слияния. Черновики и pull request из форков проходят без этого задания.

Для публикации версии из `main` откройте **Actions → Python CI/CD → Run
workflow**, выберите ветвь `main` и отметьте `publish_release`. Версия тега
берётся из `config.py`. После успешной проверки workflow публикует релиз
GitHub и прикладывает `documentation.zip`. При push тега `v*` публикация
также запускается после сверки тега с версией приложения.
