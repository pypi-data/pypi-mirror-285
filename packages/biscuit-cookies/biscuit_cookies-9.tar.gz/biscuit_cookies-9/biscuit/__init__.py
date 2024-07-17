from PyQL3.shell import PyConnection
from base64 import b64decode
from pathlib import Path
from json import load
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from win32crypt import CryptUnprotectData

__all__ = [
    'get_key', 'encrypt_value', 'decrypt_value', 'Biscuit'
]

CONV = {
    'host_key': 'domain', 'name': 'name', 'value': 'value', 'path': 'path',
    'expires_utc': 'expires', 'is_secure': 'secure', 'is_httponly': 'httpOnly'
}
DFLT = {
    'creation_utc': '1577826000',
    'is_persistent': '1',
}
REQS = (
    'name', 'value', 'domain', 'path', 'expires'
)


def _excepting(func, exceptions=(Exception,)):
    """
    RU: Декоратор для обработки указанных исключений при выполнении функции.
        Если при выполнении функции возникает одно из указанных исключений,
        функция возвращает None.

    EN: Decorator for handling specified exceptions when executing a function.
        If one of the specified exceptions occurs when executing the function,
        the function returns None.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions:
            return None

    return wrapper


def get_key(
        user_data_dir: (str | Path)
) -> bytes:
    """
    RU: Расшифровывает ключ, используемый для шифрования данных в Chrome.
    EN: Decrypts the key used for encrypting data in Chrome.

    Args:
        user_data_dir (str | Path): Path to the Chrome user data directory.

    Returns:
        bytes: The decrypted key.
    """
    user_data_dir = Path(user_data_dir)
    local_state = user_data_dir / 'Local State'
    with open(local_state, "r", encoding='latin-1') as file:
        local_state = load(file)
    enckey = b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return CryptUnprotectData(enckey, None, None, None, 0)[1]


def decrypt_value(
        key: bytes,
        encrypted_value: bytes
) -> str:
    """
    RU: Расшифровывает зашифрованное значение с помощью предоставленного ключа.
    EN: Decrypts the encrypted value using the provided key.

    Args:
        key (bytes): The decryption key.
        encrypted_value (bytes): The value to be decrypted.

    Returns:
        str: The decrypted value as a string.
    """
    iv = encrypted_value[3:15]
    encrypted_value = encrypted_value[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    return cipher.decrypt(encrypted_value)[:-16].decode()


def encrypt_value(
        key: bytes,
        value: str
) -> bytes:
    """
    RU: Зашифровывает значение с помощью предоставленного ключа.
    EN: Encrypts the value using the provided key.

    Args:
        key (bytes): The encryption key.
        value (str): The value to be encrypted.

    Returns:
        bytes: The encrypted value.
    """
    iv = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, iv)
    encrypted_value, tag = cipher.encrypt_and_digest(value.encode())
    return b'v10' + iv + encrypted_value + tag


class Biscuit:
    """
    RU: Класс для взаимодействия с куками в браузере пользователя.
    EN: A class to interact with cookies in a user's browser.

    Attributes:
        _user_data_dir (Path): The path to the user's data directory.
        _key (bytes): The decryption key.
        _conn (PyConnection): The connection to the database.
    """

    def __init__(self, user_data_dir, profile='Default'):
        """
        RU: Создает все необходимые атрибуты для объекта Biscuit.
        EN: Constructs all the necessary attributes for the Biscuit object.

        Args:
            user_data_dir (str): The path to the user's data directory.
            profile (str, optional): The user's profile. Defaults to 'Default'.
        """
        self._user_data_dir = Path(user_data_dir)
        self._key = get_key(self._user_data_dir)

        cookies_path = (
                self._user_data_dir / profile / 'Network' / 'Cookies'
        )
        if not cookies_path.exists():
            raise FileNotFoundError(cookies_path)
        self._conn = PyConnection(cookies_path)

    def get(
            self,
            where: str = None,
            order: str = None,
            limit: int = None,
            offset: int = None
    ) -> list[dict]:
        """
        RU: Извлекает файлы cookie из базы данных.
        EN: Retrieves cookies from the database.
        """
        rows = self._conn.get('cookies').rows
        columns = tuple(CONV.keys()) + ('encrypted_value',)
        cookies = []
        for cookie in rows.deserialize(
                columns, where, order, limit, offset
        ):
            decrypted_value = _excepting(
                decrypt_value
            )(
                self._key, cookie[-1]
            )
            cookie = dict(zip(CONV.values(), cookie[:-1]))
            if decrypted_value:
                cookie['value'] = decrypted_value
            if not cookie.get('value', None):
                continue
            cookies.append(cookie)
        return cookies

    def add(self, cookies: list[dict]) -> None:
        """
        RU: Добавляет файлы cookie в базу данных.
        EN: Adds cookies to the database.
        """
        table = self._conn.get('cookies')
        columns = table.columns.ids
        for cookie in cookies:
            if not all(item in cookie for item in REQS):
                continue
            values = [
                cookie[CONV[item]] if item in CONV.keys()
                else DFLT.get(item, '') for item in columns
            ]
            _excepting(
                table.rows.insert
            )(
                values=tuple(values)
            )
        self._conn.commit()
