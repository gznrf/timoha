from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush
import random

class PuzzleWidget(QWidget):
    """Виджет для отображения капчи-пазла"""

    puzzle_completed = pyqtSignal(bool)  # Сигнал о завершении сборки пазла

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pieces = []
        self.correct_positions = []
        self.current_positions = []
        self.setup_puzzle()

    def setup_puzzle(self):
        """Настройка пазла 2x2"""
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(2)

        # Создаем 4 части пазла
        for i in range(4):
            button = QPushButton(f"Часть {i+1}")
            button.setFixedSize(100, 100)
            button.clicked.connect(lambda checked, pos=i: self.piece_clicked(pos))
            self.pieces.append(button)
            self.grid_layout.addWidget(button, i // 2, i % 2)

        self.correct_positions = [0, 1, 2, 3]  # Правильный порядок
        self.current_positions = list(range(4))
        self.shuffle_puzzle()

    def shuffle_puzzle(self):
        """Перемешивание частей пазла"""
        random.shuffle(self.current_positions)
        self.update_puzzle_display()

    def piece_clicked(self, position):
        """Обработка клика по части пазла"""
        # Простая логика: при клике меняем местами с соседней частью
        if position % 2 == 0 and position + 1 < 4:  # Меняем с правой
            self.swap_pieces(position, position + 1)
        elif position % 2 == 1:  # Меняем с левой
            self.swap_pieces(position, position - 1)
        elif position == 0:  # Меняем с нижней
            self.swap_pieces(position, position + 2)
        elif position == 1:  # Меняем с нижней
            self.swap_pieces(position, position + 1)
        elif position == 2:  # Меняем с верхней
            self.swap_pieces(position, position - 2)
        elif position == 3:  # Меняем с верхней
            self.swap_pieces(position, position - 2)

    def swap_pieces(self, pos1, pos2):
        """Обмен двух частей пазла местами"""
        if 0 <= pos1 < 4 and 0 <= pos2 < 4:
            self.current_positions[pos1], self.current_positions[pos2] = \
                self.current_positions[pos2], self.current_positions[pos1]
            self.update_puzzle_display()
            self.check_completion()

    def update_puzzle_display(self):
        """Обновление отображения пазла"""
        for i, piece in enumerate(self.pieces):
            piece.setText(f"Часть {self.current_positions[i] + 1}")

    def check_completion(self):
        """Проверка правильности сборки пазла"""
        is_correct = self.current_positions == self.correct_positions
        self.puzzle_completed.emit(is_correct)
        return is_correct

    def reset_puzzle(self):
        """Сброс пазла для новой попытки"""
        self.shuffle_puzzle()