import base64
import re
import time
from functools import wraps
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
    """

    def __init__(self, client: httpx.Client) -> None:
        self.client: httpx.Client = client
        self.secret: str
        self.authenticated = False

    def _bytes_to_key(self, data: bytes, salt: bytes, output=48) -> bytes:
        """Transform bytes to keys.

        Parameters
        ----------
        data : bytes
            Byte data.
        salt : bytes
            Salt byte.
        output : int, optional
            Output, by default 48

        Returns
        -------
        bytes
            Key.

        Note
        ----
        I REALLY don't know what this does but it does work.
        """
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
        """Pad plain data.

        Parameters
        ----------
        data : bytes
            The plain data.

        Returns
        -------
        bytes
            The Padded plain data.

        Note
        ----
        I don't know what this does but it does work.
        """
        length = 16 - (len(data) % 16) # Block size = 16
        return data + (chr(length)*length).encode()

    def _unpad(self, data: bytes) -> str:
        """Unpad decrypted data.

        Parameters
        ----------
        data : bytes
            Decrypted data.

        Returns
        -------
        str
            The unpadded decrypted data.

        Note
        ----
        I don't know what this does but it does work.
        """
        return data[:-(data[-1] if isinstance(data[-1], int) else ord(data[-1]))].decode()

    def _random_letter(self, letter: str) -> str:
        """Return a pseudo-random letter.

        Returns
        -------
        str
            The letter.
        """
        timestamp = time.time()

        seed(timestamp)
        random_value = round((timestamp + random() * 16) % 16)

        return f"{random_value:x}"

    def _generate_key(self) -> str:
        """Generate a pseudorandom AES key for encrypting and decrypting.

        Returns
        -------
        str
            The key.

        Note
        ----
        UUIDs aren't meant to be random.
        Lanis pls fix.
        """
        pattern = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx-xxxxxx3xx"

        key = re.sub(pattern=r"[xy]",string=pattern,repl=self._random_letter)

        return self._encrypt(key, key)

    def _handshake(self, encrypted_key: str) -> str:
        """Tell Lanis how to encrypt data.

        Parameters
        ----------
        encrypted_key : str
            The encrypted key by `_encrypt_key`.

        Returns
        -------
        str
            Encrypted secret with our secret.
            It's used to check if both parties are encrypting equally.
        """
        url = "https://start.schulportal.hessen.de/ajax.php?f=rsaHandshake&s=665"

        response = self.client.post(url,
                                    params=
                                    {"f": "rsaHandshake",
                                     "s": str(randint(0,2000))},
                                    data={"key": encrypted_key}
                                    )

        return str(response.json()["challenge"])

    def _challenge(self, challenge: str) -> bool:
        """Check if Lanis and LanisAPI are encrypting equally.

        Parameters
        ----------
        challenge : str
            The encrypted secret from Lanis.

        Returns
        -------
        bool
            If False it failed, if True it isn't False.
        """
        return self.decrypt(challenge) == self.secret

    def _get_public_key(self) -> str:
        """Get Schulportal Hessens public rsa key.

        Returns
        -------
        str
            The rsa key.
        """
        url = "https://start.schulportal.hessen.de/ajax.php?f=rsaPublicKey"

        response = self.client.get(url)

        return response.json()["publickey"]

    def _encrypt_key(self, public_key: str) -> str:
        """Encrypts the secret with the public key.

        Parameters
        ----------
        public_key : str
            The public key from Schulportal Hessen.

        Returns
        -------
        str
            The encrypted key.
        """
        rsa = PKCS1_v1_5.new(RSA.import_key(public_key))

        return base64.b64encode(rsa.encrypt(self.secret.encode())).decode()

    def _encrypt(self, plain: str, secret: str = None) -> str:
        """Encrypts a given text with CBC.

        Parameters
        ----------
        plain : str
            The text to encrypt.
        secret : str, optional
            If given use this secret not the generated key, by default None

        Returns
        -------
        str
            The encrypted text.

        Note
        ----
        CBC encryption isn't the best there are better solutions.
        """
        plain = plain.encode()
        salt = Random.new().read(8)
        secret = secret.encode() if secret else self.secret.encode()
        key_iv = self._bytes_to_key(secret, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(self._pad(plain))).decode()

    def requires_auth(self) -> any:
        @wraps(self)
        def decorated(*args, **kwargs):
            if not args[0].authenticated:
                return
            return self(*args, **kwargs)
        return decorated

    @requires_auth
    def decrypt(self, encrypted: str) -> str:
        """Decrypts a given encrypted data.

        Parameters
        ----------
        encrypted : str
            The encrypted data.

        Returns
        -------
        str
            The decrypted data.
        """
        encrypted = base64.b64decode(encrypted.encode())
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = self._bytes_to_key(self.secret.encode(), salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return self._unpad(aes.decrypt(encrypted[16:]))

    def authenticate(self) -> bool:
        """Authenticate with a generated key so Lanis knows how to encrypt data.

        Returns
        -------
        bool
            If False the handshake failed, if True it isn't False.
        """
        self.secret = self._generate_key()

        encrypted_key = self._encrypt_key(self._get_public_key())

        challenge = self._handshake(encrypted_key)

        self.authenticated = True

        if self._challenge(challenge):
            return True

        self.authenticated = False

        return False
