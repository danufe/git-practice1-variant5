"""Статус настройки подключения к PostgreSQL."""


def get_status() -> str:
    """Вернуть сообщение о текущем состоянии настройки подключения."""
    return "PostgreSQL connection is not configured"
