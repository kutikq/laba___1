from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from account_store import Account, AccountStore, ADMIN_NAME
from password_rules import check_password, requirements_text


# Окно входа в систему (PasswordDlg)
class LoginDialog(QDialog):
    def __init__(self, max_name_len: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему")

        self.login_edit = QLineEdit()
        self.login_edit.setMaxLength(max_name_len)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("Введите имя:", self.login_edit)
        form.addRow("Введите пароль:", self.password_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("secondaryButton")
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        # очистка полей и фокус на поле имени при показе окна
        self.login_edit.setText("")
        self.password_edit.setText("")
        self.login_edit.setFocus()

    def _try_accept(self):
        # окно закрывается по "Ok" только если введено имя учётной записи
        if self.login_edit.text() == "":
            return
        self.accept()

    def login(self) -> str:
        return self.login_edit.text()

    def password(self) -> str:
        return self.password_edit.text()



# Окно смены пароля (Form5)
class ChangePasswordDialog(QDialog):
    def __init__(
        self,
        max_pass_len: int,
        require_old: bool,
        correct_old_password: str = "",
        restrict: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Смена пароля")
        self._require_old = require_old
        self._correct_old_password = correct_old_password
        self._restrict = restrict

        self.old_edit = QLineEdit()
        self.old_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_edit = QLineEdit()
        self.new_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_edit.setMaxLength(max_pass_len)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_edit.setMaxLength(max_pass_len)

        form = QFormLayout()
        if require_old:
            form.addRow("Старый пароль", self.old_edit)
        form.addRow("Новый пароль", self.new_edit)
        form.addRow("Подтверждение", self.confirm_edit)

        hint = QLabel(requirements_text())
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("secondaryButton")
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addWidget(buttons)

        self.new_edit.setText("")
        self.confirm_edit.setText("")
        self.new_edit.setFocus()

    def _try_accept(self):
        if self._require_old:
            if self.old_edit.text() != self._correct_old_password:
                QMessageBox.warning(self, "Смена пароля", "Неверный старый пароль!")
                self.old_edit.setFocus()
                return

        # если новый пароль не совпадает с его подтверждением
        if self.new_edit.text() != self.confirm_edit.text():
            QMessageBox.warning(self, "Смена пароля", "Пароли должны совпадать!")
            self.new_edit.setFocus()
            return

        if self.new_edit.text() == "":
            QMessageBox.warning(self, "Смена пароля", "Пароль не может быть пустым!")
            self.new_edit.setFocus()
            return

        # если в введённом пароле не соблюдены установленные администратором
        # ограничения (вариант №12)
        if self._restrict and not check_password(self.new_edit.text()):
            QMessageBox.warning(
                self, "Смена пароля", "Пароль не соответствует ограничениям!\n\n" + requirements_text()
            )
            self.new_edit.setFocus()
            return

        self.accept()

    def new_password(self) -> str:
        return self.new_edit.text()


# Окно добавления нового пользователя (Form4)
class AddUserDialog(QDialog):
    def __init__(self, store: AccountStore, max_name_len: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление пользователя")
        self._store = store

        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(max_name_len)

        form = QFormLayout()
        form.addRow("Имя нового пользователя", self.name_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("secondaryButton")
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.name_edit.setText("")
        self.name_edit.setFocus()

    def _try_accept(self):
        name = self.name_edit.text()
        # если имя пользователя не введено
        if name == "":
            self.name_edit.setFocus()
            return
        # если учётная запись с введённым именем уже существует
        if self._store.name_exists(name):
            QMessageBox.warning(
                self, "Добавление пользователя", f"Пользователь {name}\nуже зарегистрирован!"
            )
            self.name_edit.setFocus()
            return
        self.accept()

    def user_name(self) -> str:
        return self.name_edit.text()


# Окно просмотра/редактирования учётных записей (Form3)
class UsersTableDialog(QDialog):

    def __init__(self, store: AccountStore, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Список пользователей")
        self.resize(480, 360)
        self._store = store

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Имя пользователя", "Блокировка", "Ограничения на пароль"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        self._load()

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._save)
        close_btn = QPushButton("Ok")
        close_btn.setObjectName("secondaryButton")
        close_btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(btn_row)

    def _load(self):
        self.table.setRowCount(0)
        for index, account in self._store.iter_accounts():
            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(account.user_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            block_box = QCheckBox()
            block_box.setChecked(account.block)
            # администратор не может заблокировать сам себя
            if account.user_name == ADMIN_NAME:
                block_box.setEnabled(False)
            block_cell = QHBoxLayout()
            block_widget = self._center_widget(block_box)
            self.table.setCellWidget(row, 1, block_widget)

            restrict_box = QCheckBox()
            restrict_box.setChecked(account.restrict)
            restrict_widget = self._center_widget(restrict_box)
            self.table.setCellWidget(row, 2, restrict_widget)

    @staticmethod
    def _center_widget(widget):
        from PyQt6.QtWidgets import QWidget

        container = QWidget()
        lay = QHBoxLayout(container)
        lay.addWidget(widget)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)
        return container

    def _save(self):
        for row in range(self.table.rowCount()):
            account = self._store.read_at(row)
            block_box = self.table.cellWidget(row, 1).findChild(QCheckBox)
            restrict_box = self.table.cellWidget(row, 2).findChild(QCheckBox)
            account.block = block_box.isChecked()
            account.restrict = restrict_box.isChecked()
            self._store.write_at(row, account)
        QMessageBox.information(self, "Список пользователей", "Изменения сохранены.")


# Окно "О программе"
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")

        text = QLabel(
            "Разработка программы разграничения полномочий пользователей\n"
            "на основе парольной аутентификации\n\n"
            "Автор: Кутенков С. Д., группа ИДБ-23-14\n"
            "Дисциплина: Информационная безопасность\n\n"
            + requirements_text()
        )
        text.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(text)
        layout.addWidget(buttons)
