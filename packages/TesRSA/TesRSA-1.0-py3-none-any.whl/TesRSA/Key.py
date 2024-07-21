from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


class Key:
    @staticmethod
    def generate_private_key(public_exponent: int, key_size: int):
        return rsa.generate_private_key(public_exponent=public_exponent, key_size=key_size)

    @staticmethod
    def load_private_key(stream: bytes):
        return serialization.load_pem_private_key(stream, password=None)

    @staticmethod
    def load_public_key(stream: bytes):
        return serialization.load_pem_public_key(stream)

    @staticmethod
    def serialize_private_key(private_key: rsa.RSAPrivateKey):
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

    @staticmethod
    def serialize_public_key(public_key: rsa.RSAPublicKey):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )