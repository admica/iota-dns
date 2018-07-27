#!/usr/bin/env python

import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

class Cipher:

    def __init__(self, key):
        self.bs = 64
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)) 

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


if __name__ == '__main__':

    key = 'test'
    raw = '{"ip": "127.0.0.1", "name": "localhost.localdomain.com"}'

    print("Creating cipher...")
    cipher = Cipher(key)

    enc = cipher.encrypt(raw)
    print("Encrypted: {}".format(enc))

    raw = cipher.decrypt(enc)
    print("Raw: {}".format(raw))

