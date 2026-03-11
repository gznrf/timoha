import re

class Validators:
    """Класс с методами валидации"""

    @staticmethod
    def validate_login(login):
        """Проверка логина"""
        if not login or len(login) < 3:
            return False, "Логин должен содержать не менее 3 символов"
        if not re.match("^[a-zA-Z0-9_]+$", login):
            return False, "Логин может содержать только буквы, цифры и знак подчеркивания"
        return True, ""

    @staticmethod
    def validate_password(password):
        """Проверка пароля"""
        if not password or len(password) < 6:
            return False, "Пароль должен содержать не менее 6 символов"
        return True, ""

    @staticmethod
    def validate_role(role):
        """Проверка роли"""
        return role in ["Администратор", "Пользователь"]