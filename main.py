import os
import sys

if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_PLATFORM", "windows:darkmode=0")


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from account_store import Account, AccountStore, ADMIN_NAME, MAXNAME, MAXPASS
from dialogs import (
    AboutDialog,
    AddUserDialog,
    ChangePasswordDialog,
    LoginDialog,
    UsersTableDialog,
)
from style import apply_app_style

SECFILE = "security.db"
MAX_LOGIN_ATTEMPTS = 3  # три попытки ввода пароля, третья неверная завершает работу


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №1")
        self.resize(520, 360)

        self.store = AccountStore(SECFILE)
        self._current_user = None
        self._current_index = None
        self._is_admin = False
        self._enter_count = 0

        self._build_ui()
        self._ensure_file_created()


    # Инициализация интерфейса
    def _build_ui(self):
        menu_bar = self.menuBar()

        users_menu = menu_bar.addMenu("&Пользователи")
        self.change_password_action = users_menu.addAction("Смена пароля")
        self.change_password_action.triggered.connect(self.on_change_password)
        self.change_password_action.setEnabled(False)

        self.new_user_action = users_menu.addAction("Новый пользователь")
        self.new_user_action.triggered.connect(self.on_new_user)
        self.new_user_action.setEnabled(False)

        self.all_users_action = users_menu.addAction("Все пользователи")
        self.all_users_action.triggered.connect(self.on_all_users)
        self.all_users_action.setEnabled(False)

        users_menu.addSeparator()
        exit_action = users_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)

        help_menu = menu_bar.addMenu("&Справка")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.on_about)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_button = QPushButton("Вход в систему")
        self.login_button.setFixedSize(220, 44)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Вход в систему не выполнен")

    def _ensure_file_created(self):
        # если файл с учётными записями пользователей не существует
        # (первый запуск программы)
        if not self.store.file_exists():
            self.store.create_with_admin()

    # Обработка нажатия кнопки «Вход в систему»
    def on_login_clicked(self):
        dlg = LoginDialog(max_name_len=MAXNAME - 1, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        name = dlg.login()
        password = dlg.password()

        index, account = self.store.find_by_name(name)

        # если совпадения не найдено (достигнут конец файла)
        if index is None:
            QMessageBox.warning(self, "Вход в систему", "Вы не зарегистрированы!")
            return

        if account.pass_len == 0:
            # если пароль отсутствует (первый вход пользователя в программу)
            change_dlg = ChangePasswordDialog(
                max_pass_len=MAXPASS - 1,
                require_old=False,
                restrict=account.restrict,
                parent=self,
            )
            if change_dlg.exec() != QDialog.DialogCode.Accepted:
                # если пользователь не ввёл пароль, то выход из функции
                return
            new_password = change_dlg.new_password()
            account.user_pass = new_password
            account.pass_len = len(new_password.encode("cp1251", errors="replace"))
            self.store.write_at(index, account)
        else:
            # сравнение пароля из учётной записи и введённого пароля
            if password != account.user_pass:
                self._enter_count += 1
                # если пароли не совпадают и число попыток превысило 2
                if self._enter_count >= MAX_LOGIN_ATTEMPTS:
                    self.login_button.setEnabled(False)
                    QMessageBox.critical(self, "Вход в систему", "Вход в программу невозможен!")
                else:
                    QMessageBox.warning(self, "Вход в систему", "Неверный пароль!")
                return
            # если пароли совпадают, то продолжение работы

        # если учётная запись заблокирована администратором
        if account.block:
            QMessageBox.warning(self, "Вход в систему", "Вы заблокированы!")
            return

        # успешный вход - сохранение состояния сеанса
        self._current_user = account.user_name
        self._current_index = index
        self._is_admin = account.user_name == ADMIN_NAME
        self._enter_count = 0

        # проверка полномочий пользователя
        if self._is_admin:
            self.all_users_action.setEnabled(True)
            self.new_user_action.setEnabled(True)
        self.change_password_action.setEnabled(True)

        # скрытие кнопки «Вход»
        self.login_button.setVisible(False)

        role = " (администратор)" if self._is_admin else ""
        self.statusBar().showMessage(f"Пользователь: {self._current_user}{role}")

    # Команда «Смена пароля»
    def on_change_password(self):
        account = self.store.read_at(self._current_index)
        dlg = ChangePasswordDialog(
            max_pass_len=MAXPASS - 1,
            require_old=True,
            correct_old_password=account.user_pass,
            restrict=account.restrict,
            parent=self,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new_password = dlg.new_password()
        account.user_pass = new_password
        account.pass_len = len(new_password.encode("cp1251", errors="replace"))
        self.store.write_at(self._current_index, account)
        QMessageBox.information(self, "Смена пароля", "Пароль изменён.")

    # Команда «Новый пользователь»
    def on_new_user(self):
        dlg = AddUserDialog(self.store, max_name_len=MAXNAME - 1, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        name = dlg.user_name()
        new_account = Account(
            user_name=name,
            pass_len=0,
            user_pass="",
            block=False,
            restrict=True,
        )
        self.store.append(new_account)

    # Команда «Все пользователи»
    def on_all_users(self):
        dlg = UsersTableDialog(self.store, parent=self)
        dlg.exec()

    # Справка
    def on_about(self):
        AboutDialog(self).exec()


def main():
    app = QApplication(sys.argv)
    apply_app_style(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
