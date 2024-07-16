from cryptography.fernet import Fernet
import os

KEY = b"Y9_k5HsxyFAjZ1QcwxeB36IAWVjQW-VVb6_quqaLWDQ="
encrypted = False


def encrypt_data(data: str) -> str:
    if encrypted:
        cipher_suite = Fernet(KEY)
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    else:
        return data


def decrypt_data(encrypted_data: str) -> str:
    if encrypted:
        cipher_suite = Fernet(KEY)
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    else:
        return encrypted_data


def get_credentials_file_path():
    home_dir = os.path.expanduser("~")
    credentials_dir = os.path.join(home_dir, ".thunder_dependencies")
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir, exist_ok=True)
    credentials_file_path = os.path.join(credentials_dir, ".thunder")
    return credentials_file_path


def save_tokens(id_token, refresh_token, uid) -> None:
    credentials_file_path = get_credentials_file_path()
    with open(credentials_file_path, "w", encoding="utf-8") as file:
        file.write(encrypt_data(id_token) + "\n")
        file.write(encrypt_data(refresh_token) + "\n")
        file.write(uid)


def delete_data():
    credentials_file_path = get_credentials_file_path()
    try:
        os.remove(credentials_file_path)
    except OSError:
        pass
