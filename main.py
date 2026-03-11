#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from views.login_window import LoginWindow
import os
import sys
from PyQt5.QtCore import QLibraryInfo
def main():
    """Точка входа в приложение"""
    if sys.platform == 'darwin':
        # Автоматически определяем путь к плагинам
        plugin_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
        print(f"Установлен путь к плагинам Qt: {plugin_path}")
    # Включение поддержки высокого разрешения для Mac
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("AuthApp_Заказчик")
    app.setOrganizationName("ООО Заказчик")

    # Установка стиля для Mac OS
    app.setStyle('Fusion')

    # Создание и отображение главного окна
    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()