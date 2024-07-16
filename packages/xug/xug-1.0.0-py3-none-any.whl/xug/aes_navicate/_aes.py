from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import binascii

aes_key = b"libcckeylibcckey"
aes_iv = b"libcciv libcciv "


def encrypt(string):
    '''加密'''
    backend = default_backend()
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=backend)
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(string.encode()) + padder.finalize()

    result = encryptor.update(padded_data) + encryptor.finalize()
    return binascii.hexlify(result).upper().decode()


# 解密
def decrypt(upper_string):
    '''解密'''
    backend = default_backend()
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=backend)
    decryptor = cipher.decryptor()

    encrypted_data = binascii.unhexlify(upper_string.lower())
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    try:
        data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    except ValueError as e:
        print("Decryption error: Invalid padding bytes.")
        raise e

    return data.decode()


if __name__ == "__main__":
    print(encrypt("明文"))
    print(decrypt("CFCB9D0434693474F8C70FC796C7F0F3"))
