class User:
    """Класс сущности Пользователь"""

    def __init__(self, id, login, password, role, is_blocked, failed_attempts):
        self.id = id
        self.login = login
        self.password = password
        self.role = role
        self.is_blocked = bool(is_blocked)
        self.failed_attempts = failed_attempts

    def is_admin(self):
        """Проверка, является ли пользователь администратором"""
        return self.role == "Администратор"

    def block(self):
        """Блокировка пользователя"""
        self.is_blocked = True

    def increment_failed_attempts(self):
        """Увеличение счетчика неудачных попыток"""
        self.failed_attempts += 1

    def reset_failed_attempts(self):
        """Сброс счетчика неудачных попыток"""
        self.failed_attempts = 0