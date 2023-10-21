import base64
import re
import time
from hashlib import md5
from random import randint, random, seed

import httpx
from Cryptodome import Random
from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA


class Cryptor:
    """Provides various functions for encrypting, decrypting and to satisfy Schulportal Hessens security requirements.

    Parameters
    ----------
    client : httpx.Client
        The html client used by `LanisClient`.

    Notes
    -----
    This class wouldn't exist without these scripts:

    https://stackoverflow.com/questions/36762098/how-to-decrypt-password-from-javascript-cryptojs-aes-encryptpassword-passphras
    https://github.com/koenidv/sph-planner/blob/main/app/src/main/java/de/koenidv/sph/networking/Cryption.kt

    Schulportal Hessens encryption isn't really secure because it uses CBC encryption,
    so this whole process of encrypting and decrypting is actually useless.
    """

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def _bytes_to_key(self, data: bytes, salt: bytes, output=48) -> bytes:
        # extended from https://gist.github.com/gsakkis/4546068
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]

    def _pad(self, data: bytes) -> bytes:
        length = 16 - (len(data) % 16) # Block size = 16
        return data + (chr(length)*length).encode()

    def _unpad(self, data: bytes) -> str:
        return data[:-(data[-1] if isinstance(data[-1], int) else ord(data[-1]))].decode()

    def _random_letter(self) -> str:
        timestamp = time.time()

        seed(timestamp)
        random_value = round((timestamp + random() * 16) % 16)

        return f"{random_value:x}"

    def encrypt(self, data: str, secret: str) -> str:
        data = data.encode()
        secret = secret.encode()
        salt = Random.new().read(8)
        key_iv = self._bytes_to_key(secret, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(self._pad(data))).decode()

    def decrypt(self, data: str, secret: str) -> str:
        data = data.encode()
        secret = secret.encode()
        encrypted = base64.b64decode(data)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = self._bytes_to_key(secret, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return self._unpad(aes.decrypt(encrypted[16:]))

    def encrypt_key(self, secret: str, public_key: str) -> str:
        rsa = PKCS1_v1_5.new(RSA.import_key(public_key))

        return base64.b64encode(rsa.encrypt(secret.encode())).decode()

    def generate_key(self) -> str:
        pattern = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx-xxxxxx3xx"

        key = re.sub(pattern=r"[xy]",string=pattern,repl=self._random_letter())

        return self.encrypt(key, key)

    def handshake(self, encrypted_key: str) -> str:
        url = "https://start.schulportal.hessen.de/ajax.php?f=rsaHandshake&s=665"

        response = self.client.post(url,
                                    params=
                                    {"f": "rsaHandshake",
                                     "s": str(randint(0,2000))},
                                    data={"key": encrypted_key}
                                    )

        return str(response.json()["challenge"])

    def challenge(self, challenge: str, secret: str) -> bool:
        return self.decrypt(challenge, secret) == secret

    def get_public_key(self) -> str:
        url = "https://start.schulportal.hessen.de/ajax.php?f=rsaPublicKey"

        response = self.client.get(url)

        return response.json()["publickey"]
