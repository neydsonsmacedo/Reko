import json
import os
from cryptography.fernet import Fernet


class EncryptionService:
    def __init__(self, data_file='data.json', key_file='key.key'):
        self.data_file = data_file
        self.key_file = key_file
        self.fernet = self._load_or_generate_key()

    def _load_or_generate_key(self) -> Fernet:
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as file:
                key = file.read()
            return Fernet(key)
        else:
            new_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as file:
                file.write(new_key)
            return Fernet(new_key)

    def encrypt_text(self, plain_text: str) -> str:
        text_bytes = plain_text.encode('utf-8')
        encrypted_bytes = self.fernet.encrypt(text_bytes)
        return encrypted_bytes.decode('utf-8')

    def decrypt_text(self, encrypted_text: str) -> str:
        encrypted_bytes = encrypted_text.encode('utf-8')
        decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')

    def save_password(self, service: str, username: str, raw_password: str) -> None:
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        data[service] = {
            'username': username,
            'password': self.encrypt_text(raw_password)
        }

        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=4)

    def get_password(self, service: str) -> dict | None:
        if not os.path.exists(self.data_file):
            return None

        with open(self.data_file, 'r') as file:
            data = json.load(file)

        if service in data:
            entry = data[service]
            decrypted_password = self.decrypt_text(entry['password'])
            return {
                'username': entry['username'],
                'password': decrypted_password
            }

        return None