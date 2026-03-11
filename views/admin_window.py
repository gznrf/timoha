from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialog, QDialogButtonBox, QLineEdit,
                             QComboBox, QHeaderView, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from models.user import User

class UserDialog(QDialog):
    """Диалог для добавления/редактирования пользователя"""

    def __init__(self, database, user=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса диалога"""
        if self.user:
            self.setWindowTitle("Редактирование пользователя")
        else:
            self.setWindowTitle("Добавление нового пользователя")

        self.setMinimumSize(300, 200)

        layout = QVBoxLayout(self)

        # Группа ввода
        input_group = QGroupBox("Данные пользователя")
        input_layout = QVBoxLayout(input_group)

        # Логин
        login_layout = QHBoxLayout()
        login_label = QLabel("Логин:")
        login_label.setFixedWidth(80)
        self.login_edit = QLineEdit()
        if self.user:
            self.login_edit.setText(self.user.login)
            self.login_edit.setEnabled(False)  # Нельзя изменить логин
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_edit)
        input_layout.addLayout(login_layout)

        # Пароль (только для нового пользователя)
        if not self.user:
            password_layout = QHBoxLayout()
            password_label = QLabel("Пароль:")
            password_label.setFixedWidth(80)
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.Password)
            password_layout.addWidget(password_label)
            password_layout.addWidget(self.password_edit)
            input_layout.addLayout(password_layout)

        # Роль
        role_layout = QHBoxLayout()
        role_label = QLabel("Роль:")
        role_label.setFixedWidth(80)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Пользователь", "Администратор"])
        if self.user:
            index = 0 if self.user.role == "Пользователь" else 1
            self.role_combo.setCurrentIndex(index)
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        input_layout.addLayout(role_layout)

        layout.addWidget(input_group)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_user_data(self):
        """Получение данных пользователя из диалога"""
        return {
            'login': self.login_edit.text().strip(),
            'password': getattr(self, 'password_edit', None).text() if hasattr(self, 'password_edit') else None,
            'role': self.role_combo.currentText()
        }

class AdminWindow(QMainWindow):
    """Рабочий стол администратора"""

    def __init__(self, database, user):
        super().__init__()
        self.database = database
        self.current_user = user
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle(f"ООО 'Заказчик' - Панель администратора ({self.current_user.login})")
        self.setMinimumSize(600, 400)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной макет
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel("Управление пользователями")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Логин", "Роль", "Статус"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.users_table)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить пользователя")
        self.add_button.clicked.connect(self.add_user)
        buttons_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_user)
        buttons_layout.addWidget(self.edit_button)

        self.unblock_button = QPushButton("Снять блокировку")
        self.unblock_button.clicked.connect(self.unblock_user)
        buttons_layout.addWidget(self.unblock_button)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_users)
        buttons_layout.addWidget(self.refresh_button)

        main_layout.addLayout(buttons_layout)

    def load_users(self):
        """Загрузка списка пользователей в таблицу"""
        users = self.database.get_all_users()

        self.users_table.setRowCount(len(users))

        for row, user_data in enumerate(users):
            # ID
            id_item = QTableWidgetItem(str(user_data['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.users_table.setItem(row, 0, id_item)

            # Логин
            login_item = QTableWidgetItem(user_data['login'])
            self.users_table.setItem(row, 1, login_item)

            # Роль
            role_item = QTableWidgetItem(user_data['role'])
            role_item.setTextAlignment(Qt.AlignCenter)
            self.users_table.setItem(row, 2, role_item)

            # Статус
            status = "Заблокирован" if user_data['is_blocked'] else "Активен"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            if user_data['is_blocked']:
                status_item.setForeground(Qt.red)
            self.users_table.setItem(row, 3, status_item)

    def add_user(self):
        """Добавление нового пользователя"""
        dialog = UserDialog(self.database)

        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_user_data()

            # Проверка заполнения полей
            if not data['login'] or not data['password']:
                QMessageBox.warning(
                    self,
                    "Предупреждение",
                    "Все поля должны быть заполнены",
                    QMessageBox.Ok
                )
                return

            # Проверка наличия пользователя
            existing_user = self.database.get_user(data['login'])
            if existing_user:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Пользователь с логином '{data['login']}' уже существует",
                    QMessageBox.Ok
                )
                return

            # Добавление пользователя
            success = self.database.add_user(
                data['login'],
                data['password'],
                data['role']
            )

            if success:
                QMessageBox.information(
                    self,
                    "Успешно",
                    f"Пользователь '{data['login']}' успешно добавлен",
                    QMessageBox.Ok
                )
                self.load_users()
            else:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    "Не удалось добавить пользователя",
                    QMessageBox.Ok
                )

    def edit_user(self):
        """Редактирование выбранного пользователя"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите пользователя для редактирования",
                QMessageBox.Ok
            )
            return

        user_id = int(self.users_table.item(current_row, 0).text())
        user = self.database.get_user(self.users_table.item(current_row, 1).text())

        if user:
            dialog = UserDialog(self.database, user)

            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_user_data()

                # Обновление роли
                if user.role != data['role']:
                    self.database.update_user(user_id, role=data['role'])

                    QMessageBox.information(
                        self,
                        "Успешно",
                        "Данные пользователя обновлены",
                        QMessageBox.Ok
                    )
                    self.load_users()

    def unblock_user(self):
        """Снятие блокировки пользователя"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите пользователя для разблокировки",
                QMessageBox.Ok
            )
            return

        user_id = int(self.users_table.item(current_row, 0).text())
        user_login = self.users_table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Снять блокировку с пользователя '{user_login}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.database.update_user(user_id, is_blocked=0, failed_attempts=0)
            QMessageBox.information(
                self,
                "Успешно",
                f"Блокировка пользователя '{user_login}' снята",
                QMessageBox.Ok
            )
            self.load_users()