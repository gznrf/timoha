from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QGroupBox, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from database.database_manager import DatabaseManager
from widgets.puzzle_widget import PuzzleWidget
from views.admin_window import AdminWindow

class LoginWindow(QMainWindow):
    """Главное окно авторизации"""

    def __init__(self):
        super().__init__()
        self.database = DatabaseManager()
        self.failed_attempts_count = 0  # Счетчик неудачных попыток подряд
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("ООО 'Заказчик' - Авторизация")
        self.setMinimumSize(500, 600)  # Увеличил размер для картинок

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной макет
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel("Авторизация в системе")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Группа ввода данных
        input_group = QGroupBox("Введите учетные данные")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        # Поле логина
        login_layout = QHBoxLayout()
        login_label = QLabel("Логин:")
        login_label.setFixedWidth(80)
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите логин")
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_edit)
        input_layout.addLayout(login_layout)

        # Поле пароля
        password_layout = QHBoxLayout()
        password_label = QLabel("Пароль:")
        password_label.setFixedWidth(80)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Введите пароль")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        input_layout.addLayout(password_layout)

        main_layout.addWidget(input_group)

        # Группа капчи
        captcha_group = QGroupBox("Проверка: соберите пазл")
        captcha_layout = QVBoxLayout(captcha_group)

        # Инструкция
        instruction_label = QLabel("Нажимайте на части пазла для их перемещения")
        instruction_label.setWordWrap(True)
        instruction_label.setAlignment(Qt.AlignCenter)
        captcha_layout.addWidget(instruction_label)

        # Пазл
        self.puzzle_widget = PuzzleWidget()
        self.puzzle_widget.puzzle_completed.connect(self.on_puzzle_completed)
        captcha_layout.addWidget(self.puzzle_widget, alignment=Qt.AlignCenter)

        # Статус пазла
        self.puzzle_status_label = QLabel("Пазл не собран")
        self.puzzle_status_label.setAlignment(Qt.AlignCenter)
        captcha_layout.addWidget(self.puzzle_status_label)

        main_layout.addWidget(captcha_group)

        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.authenticate)
        main_layout.addWidget(self.login_button)

        # Кнопка сброса пазла
        reset_button = QPushButton("Перемешать пазл")
        reset_button.clicked.connect(self.reset_puzzle)
        main_layout.addWidget(reset_button)

        # Установка порядка табуляции
        self.setTabOrder(self.login_edit, self.password_edit)
        self.setTabOrder(self.password_edit, self.puzzle_widget)
        self.setTabOrder(self.puzzle_widget, self.login_button)

        self.puzzle_solved = False

    def on_puzzle_completed(self, is_correct):
        """Обработка завершения сборки пазла"""
        if is_correct:
            self.puzzle_status_label.setText("✓ Пазл собран правильно")
            self.puzzle_status_label.setStyleSheet("color: green")
            self.puzzle_solved = True
        else:
            self.puzzle_status_label.setText("✗ Пазл собран неправильно")
            self.puzzle_status_label.setStyleSheet("color: red")
            self.puzzle_solved = False

    def reset_puzzle(self):
        """Сброс пазла"""
        self.puzzle_widget.reset_puzzle()
        self.puzzle_status_label.setText("Пазл не собран")
        self.puzzle_status_label.setStyleSheet("")
        self.puzzle_solved = False

    def authenticate(self):
        """Аутентификация пользователя"""
        # Проверка заполнения полей
        login = self.login_edit.text().strip()
        password = self.password_edit.text()

        if not login or not password:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Поля 'Логин' и 'Пароль' обязательны для заполнения",
                QMessageBox.Ok
            )
            return

        # Проверка пазла
        if not self.puzzle_solved:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Необходимо собрать пазл для продолжения",
                QMessageBox.Ok
            )
            self.failed_attempts_count += 1
            self.check_block_status()
            return

        # Поиск пользователя в БД
        user = self.database.get_user(login)

        if not user or user.password != password:
            # Неверный логин или пароль
            QMessageBox.critical(
                self,
                "Ошибка авторизации",
                "Вы ввели неверный логин или пароль.\nПожалуйста проверьте ещё раз введенные данные.",
                QMessageBox.Ok
            )

            self.failed_attempts_count += 1

            if user:
                user.increment_failed_attempts()
                self.database.update_user(user.id, failed_attempts=user.failed_attempts)

            self.check_block_status()
            self.reset_puzzle()
            return

        # Проверка блокировки
        if user.is_blocked:
            QMessageBox.critical(
                self,
                "Доступ запрещен",
                "Вы заблокированы. Обратитесь к администратору.",
                QMessageBox.Ok
            )
            return

        # Успешная авторизация
        user.reset_failed_attempts()
        self.database.update_user(user.id, failed_attempts=0)

        QMessageBox.information(
            self,
            "Успешно",
            "Вы успешно авторизовались",
            QMessageBox.Ok
        )

        # Открытие соответствующего окна
        if user.is_admin():
            self.admin_window = AdminWindow(self.database, user)
            self.admin_window.show()
            self.hide()
        else:
            # Для обычного пользователя просто показываем информационное окно
            QMessageBox.information(
                self,
                "Информация",
                f"Добро пожаловать, {user.login}!\nВаша роль: {user.role}",
                QMessageBox.Ok
            )

    def check_block_status(self):
        """Проверка необходимости блокировки пользователя"""
        if self.failed_attempts_count >= 3:
            # Блокировка последнего пользователя, который пытался войти
            login = self.login_edit.text().strip()
            if login:
                user = self.database.get_user(login)
                if user:
                    user.block()
                    self.database.update_user(user.id, is_blocked=1)

            QMessageBox.critical(
                self,
                "Блокировка",
                "Вы заблокированы. Обратитесь к администратору.",
                QMessageBox.Ok
            )