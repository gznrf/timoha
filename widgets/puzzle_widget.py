import os
import random
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon

class PuzzleWidget(QWidget):
    """Виджет для отображения капчи-пазла с выбором двух частей"""

    puzzle_completed = pyqtSignal(bool)  # Сигнал о завершении сборки пазла

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pieces = []
        self.correct_positions = [0, 1, 2, 3]  # Правильный порядок
        self.current_positions = []
        self.selected_piece_index = -1  # Индекс выбранной части (-1 = ничего не выбрано)
        self.images_loaded = False
        self.setup_puzzle()

    def get_image_paths(self):
        """Получение путей к изображениям"""
        # Путь к папке с изображениями
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(current_dir, 'resources', 'images')

        # Проверяем существование папки
        if not os.path.exists(images_dir):
            os.makedirs(images_dir, exist_ok=True)
            print(f"Создана папка для изображений: {images_dir}")
            return []

        # Ищем файлы 1.png, 2.png, 3.png, 4.png
        image_paths = []
        for i in range(1, 5):
            img_path = os.path.join(images_dir, f"{i}.png")
            if os.path.exists(img_path):
                image_paths.append(img_path)
            else:
                print(f"Файл не найден: {img_path}")
                return []

        return image_paths

    def load_images(self):
        """Загрузка изображений для пазла"""
        image_paths = self.get_image_paths()

        if len(image_paths) == 4:
            self.images_loaded = True
            return image_paths
        else:
            self.images_loaded = False
            return None

    def setup_puzzle(self):
        """Настройка пазла 2x2"""
        # Основной макет
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(5)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)

        # Загружаем изображения
        image_paths = self.load_images()

        # Создаем 4 части пазла
        piece_size = 120  # Размер каждой части

        for i in range(4):
            piece = QPushButton()
            piece.setFixedSize(piece_size, piece_size)
            piece.setCursor(Qt.PointingHandCursor)

            # Сохраняем индекс как свойство кнопки
            piece.setProperty("piece_index", i)

            # Если изображения загружены, используем их
            if image_paths and i < len(image_paths):
                pixmap = QPixmap(image_paths[i])
                if not pixmap.isNull():
                    # Масштабируем изображение под размер кнопки
                    scaled_pixmap = pixmap.scaled(
                        piece_size - 10,
                        piece_size - 10,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    piece.setIcon(QIcon(scaled_pixmap))
                    piece.setIconSize(QSize(piece_size - 10, piece_size - 10))
                    piece.setText("")  # Убираем текст
                else:
                    piece.setText(f"Часть {i+1}")
            else:
                piece.setText(f"Часть {i+1}")

            # Устанавливаем стиль для кнопок
            self.update_piece_style(piece, False)

            piece.clicked.connect(self.piece_clicked)
            self.pieces.append(piece)
            self.grid_layout.addWidget(piece, i // 2, i % 2)

        # Добавляем информационную метку
        self.info_label = QLabel("👆 Нажмите на первую часть, затем на вторую для обмена")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #2a82da; font-size: 11px; margin-top: 5px;")
        self.grid_layout.addWidget(self.info_label, 2, 0, 1, 2)

        self.current_positions = list(range(4))
        self.shuffle_puzzle()

        # Если изображения не загружены, показываем предупреждение
        if not self.images_loaded:
            warning_label = QLabel("⚠️ Изображения не найдены\nПоложите файлы 1.png - 4.png в папку resources/images/")
            warning_label.setStyleSheet("color: red; font-size: 10px;")
            warning_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(warning_label, 3, 0, 1, 2)

    def update_piece_style(self, piece, is_selected):
        """Обновление стиля кнопки"""
        if is_selected:
            piece.setStyleSheet("""
                QPushButton {
                    border: 4px solid #2a82da;
                    border-radius: 5px;
                    background-color: #e0f0ff;
                }
                QPushButton:hover {
                    border: 4px solid #1a6ab0;
                }
            """)
        else:
            piece.setStyleSheet("""
                QPushButton {
                    border: 2px solid #4a4a4a;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                }
                QPushButton:hover {
                    border: 2px solid #2a82da;
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)

    def shuffle_puzzle(self):
        """Перемешивание частей пазла"""
        random.shuffle(self.current_positions)
        self.update_puzzle_display()
        self.selected_piece_index = -1  # Сбрасываем выбор

    def piece_clicked(self):
        """Обработка клика по части пазла"""
        # Получаем индекс нажатой кнопки
        button = self.sender()
        clicked_index = button.property("piece_index")

        # Если это первый выбор
        if self.selected_piece_index == -1:
            # Выбираем первую часть
            self.selected_piece_index = clicked_index
            self.update_piece_style(self.pieces[clicked_index], True)
            self.info_label.setText(f"✅ Выбрана часть {clicked_index + 1}. Теперь выберите часть для обмена")
        else:
            # Это второй выбор - меняем местами
            if self.selected_piece_index != clicked_index:
                # Меняем местами
                self.swap_pieces(self.selected_piece_index, clicked_index)

                # Сбрасываем выделение первой части
                self.update_piece_style(self.pieces[self.selected_piece_index], False)
                self.selected_piece_index = -1
                self.info_label.setText("👆 Нажмите на первую часть, затем на вторую для обмена")
            else:
                # Если нажали на ту же часть - отменяем выбор
                self.update_piece_style(self.pieces[self.selected_piece_index], False)
                self.selected_piece_index = -1
                self.info_label.setText("👆 Нажмите на первую часть, затем на вторую для обмена")

    def swap_pieces(self, pos1, pos2):
        """Обмен двух частей пазла местами"""
        if 0 <= pos1 < 4 and 0 <= pos2 < 4:
            # Меняем местами в массиве позиций
            self.current_positions[pos1], self.current_positions[pos2] = \
                self.current_positions[pos2], self.current_positions[pos1]

            # Обновляем отображение
            self.update_puzzle_display()
            self.check_completion()

    def update_puzzle_display(self):
        """Обновление отображения пазла"""
        image_paths = self.get_image_paths()

        for i, piece in enumerate(self.pieces):
            actual_piece_index = self.current_positions[i]

            if image_paths and len(image_paths) > actual_piece_index:
                pixmap = QPixmap(image_paths[actual_piece_index])
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        piece.width() - 10,
                        piece.height() - 10,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    piece.setIcon(QIcon(scaled_pixmap))
                    piece.setIconSize(QSize(piece.width() - 10, piece.height() - 10))
                    piece.setText("")
                else:
                    piece.setText(f"Часть {actual_piece_index + 1}")
                    piece.setIcon(QIcon())
            else:
                piece.setText(f"Часть {actual_piece_index + 1}")
                piece.setIcon(QIcon())

    def check_completion(self):
        """Проверка правильности сборки пазла"""
        is_correct = self.current_positions == self.correct_positions

        # Визуальный фидбек
        if is_correct:
            for piece in self.pieces:
                piece.setStyleSheet("""
                    QPushButton {
                        border: 4px solid #00aa00;
                        border-radius: 5px;
                        background-color: #f0fff0;
                    }
                """)
            self.info_label.setText("✅ Пазл собран правильно! Можно авторизоваться")
            self.info_label.setStyleSheet("color: #00aa00; font-size: 11px; font-weight: bold;")
        else:
            # Возвращаем обычный стиль для всех частей
            for piece in self.pieces:
                if piece.property("piece_index") == self.selected_piece_index:
                    self.update_piece_style(piece, True)
                else:
                    self.update_piece_style(piece, False)
            self.info_label.setText("👆 Нажмите на первую часть, затем на вторую для обмена")
            self.info_label.setStyleSheet("color: #2a82da; font-size: 11px;")

        self.puzzle_completed.emit(is_correct)
        return is_correct

    def reset_puzzle(self):
        """Сброс пазла для новой попытки"""
        self.shuffle_puzzle()

        # Сбрасываем выделение
        if self.selected_piece_index != -1:
            self.update_piece_style(self.pieces[self.selected_piece_index], False)
            self.selected_piece_index = -1

        # Сбрасываем информационную метку
        self.info_label.setText("👆 Нажмите на первую часть, затем на вторую для обмена")
        self.info_label.setStyleSheet("color: #2a82da; font-size: 11px;")