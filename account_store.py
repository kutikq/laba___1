import os
import struct
from dataclasses import dataclass, field

MAXNAME = 20
MAXPASS = 10

# '<' — без выравнивания/паддинга (как в письме: ровно 36 байт)
# 20s - имя, i - длина пароля (4 байта), 10s - пароль, ? - блокировка, ? - ограничения
_RECORD_FORMAT = "<20si10s??"
RECORD_SIZE = struct.calcsize(_RECORD_FORMAT)  # 36 байт
assert RECORD_SIZE == 36, RECORD_SIZE

ADMIN_NAME = "ADMIN"


@dataclass
class Account:
    """Учётная запись пользователя (аналог AccountType из методички)."""

    user_name: str
    pass_len: int = 0
    user_pass: str = ""
    block: bool = False
    restrict: bool = True

    def pack(self) -> bytes:
        name_bytes = self.user_name.encode("cp1251", errors="replace")[: MAXNAME - 1]
        pass_bytes = self.user_pass.encode("cp1251", errors="replace")[: MAXPASS - 1]
        return struct.pack(
            _RECORD_FORMAT,
            name_bytes.ljust(MAXNAME, b"\x00"),
            self.pass_len,
            pass_bytes.ljust(MAXPASS, b"\x00"),
            self.block,
            self.restrict,
        )

    @staticmethod
    def unpack(data: bytes) -> "Account":
        name_raw, pass_len, pass_raw, block, restrict = struct.unpack(
            _RECORD_FORMAT, data
        )
        name = name_raw.split(b"\x00", 1)[0].decode("cp1251", errors="replace")
        password = pass_raw.split(b"\x00", 1)[0].decode("cp1251", errors="replace")
        return Account(
            user_name=name,
            pass_len=pass_len,
            user_pass=password,
            block=block,
            restrict=restrict,
        )

    def max_name_len(self) -> int:
        return MAXNAME - 1

    def max_pass_len(self) -> int:
        return MAXPASS - 1


class AccountStore:
    """
    Работа с двоичным файлом учётных записей.

    Аналог глобальных AccFile/UserAcc/RecCount из методички, но
    инкапсулированный в класс вместо глобальных переменных.
    """

    def __init__(self, file_name: str = "security.db"):
        self.file_name = file_name

    # Первый запуск программы
    def file_exists(self) -> bool:
        return os.path.exists(self.file_name)

    def create_with_admin(self) -> None:
        admin = Account(
            user_name=ADMIN_NAME,
            pass_len=0,
            user_pass="",
            block=False,
            restrict=True,
        )
        with open(self.file_name, "wb") as f:
            f.write(admin.pack())

    # Последовательный перебор записей
    def iter_accounts(self):
        """Генератор (индекс_с_нуля, Account) по всем записям файла."""
        with open(self.file_name, "rb") as f:
            index = 0
            while True:
                data = f.read(RECORD_SIZE)
                if len(data) < RECORD_SIZE:
                    break
                yield index, Account.unpack(data)
                index += 1

    def count(self) -> int:
        size = os.path.getsize(self.file_name)
        return size // RECORD_SIZE

    def find_by_name(self, name: str):
        for index, account in self.iter_accounts():
            if account.user_name == name:
                return index, account
        return None, None

    def name_exists(self, name: str) -> bool:
        index, _ = self.find_by_name(name)
        return index is not None

    # Чтение / запись одной записи по номеру (аналог seekp/seekg + read/write)
    def read_at(self, index: int) -> Account:
        with open(self.file_name, "rb") as f:
            f.seek(index * RECORD_SIZE)
            data = f.read(RECORD_SIZE)
            return Account.unpack(data)

    def write_at(self, index: int, account: Account) -> None:
        """Запись/перезапись учётной записи с заданным номером (с начала файла)."""
        with open(self.file_name, "r+b") as f:
            f.seek(index * RECORD_SIZE)
            f.write(account.pack())

    def append(self, account: Account) -> int:
        """Добавление новой учётной записи в конец файла. Возвращает её индекс."""
        index = self.count()
        with open(self.file_name, "ab") as f:
            f.write(account.pack())
        return index
