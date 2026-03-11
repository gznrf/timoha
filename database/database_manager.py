import sqlite3
from pathlib import Path

class DatabaseManager:
    """Класс для управления базой данных SQLite"""

    def __init__(self):
        db_path = Path(__file__).parent.parent / "users.db"
        self.connection = sqlite3.connect(str(db_path))
        self.create_tables()

    def create_tables(self):
        """Создание таблицы пользователей"""
        cursor = self.connection.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            login TEXT UNIQUE NOT NULL,
                                                            password TEXT NOT NULL,
                                                            role TEXT NOT NULL CHECK(role IN ('Администратор', 'Пользователь')),
                           is_blocked INTEGER DEFAULT 0,
                           failed_attempts INTEGER DEFAULT 0,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           )
                       ''')
        self.connection.commit()

        # Добавление тестового администратора, если таблица пуста
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self.add_user("admin", "admin123", "Администратор")
            self.add_user("user", "user123", "Пользователь")

    def add_user(self, login, password, role):
        """Добавление нового пользователя"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
                (login, password, role)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, login):
        """Получение пользователя по логину"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, login, password, role, is_blocked, failed_attempts FROM users WHERE login = ?",
            (login,)
        )
        row = cursor.fetchone()
        if row:
            from models.user import User
            return User(*row)
        return None

    def update_user(self, user_id, **kwargs):
        """Обновление данных пользователя"""
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        cursor = self.connection.cursor()
        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE id = ?",
            values
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def get_all_users(self):
        """Получение всех пользователей"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, login, role, is_blocked FROM users ORDER BY login")
        rows = cursor.fetchall()

        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'login': row[1],
                'role': row[2],
                'is_blocked': row[3]
            })
        return users

    def __del__(self):
        """Закрытие соединения при уничтожении объекта"""
        if hasattr(self, 'connection'):
            self.connection.close()