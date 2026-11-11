"""Консольный запуск учебного приложения."""

from config import APP_NAME
from database import get_status


def main() -> None:
    """Вывести название приложения и сообщение о статусе PostgreSQL."""
    print("Application:", APP_NAME)
    print(get_status())
    print("Program updated by person3")
    print("Changes from person3")


if __name__ == "__main__":
    main()
