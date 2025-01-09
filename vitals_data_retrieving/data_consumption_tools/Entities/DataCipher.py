import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os


class DataCipher:
    def __init__(self):
        if os.path.exists('.env'):
            load_dotenv()
        self.CIPHER_KEY = base64.b64decode(os.environ.get('CIPHER_KEY'))
        self.BLOCK_SIZE = 16

    def encrypt(self, plaintext) -> bytes:
        """
        Encrypt a plaintext string using AES-256 encryption

        :param plaintext: str: Plaintext to encrypt
        :return: bytes: Encrypted ciphertext
        """
        # Generate a random initialization vector (IV)
        iv = os.urandom(self.BLOCK_SIZE)

        # Pad the plaintext to ensure it matches the block size
        padder = padding.PKCS7(self.BLOCK_SIZE * 8).padder()
        padded_plaintext = padder.update(plaintext.encode()) + padder.finalize()

        # Create a Cipher object
        cipher = Cipher(algorithms.AES(self.CIPHER_KEY), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Perform encryption
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        return iv + ciphertext  # Prepend IV to ciphertext for later decryption

    def decrypt(self, ciphertext) -> str:
        """
        Decrypt a ciphertext string using AES-256 decryption

        :param ciphertext: bytes: Ciphertext to decrypt
        :return: str: Decrypted plaintext
        """
        # Extract the IV from the beginning of the ciphertext
        iv = ciphertext[:self.BLOCK_SIZE]
        actual_ciphertext = ciphertext[self.BLOCK_SIZE:]

        # Create a Cipher object
        cipher = Cipher(algorithms.AES(self.CIPHER_KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Perform decryption
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(self.BLOCK_SIZE * 8).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode()
