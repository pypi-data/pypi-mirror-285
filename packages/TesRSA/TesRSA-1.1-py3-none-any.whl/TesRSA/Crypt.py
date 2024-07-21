from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class Crypt:
    @staticmethod
    def encrypt_content(content: str, public_key: rsa.RSAPublicKey) -> bytes:
        ciphertext = public_key.encrypt(
            content.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    @staticmethod
    def decrypt_content(ciphertext: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext