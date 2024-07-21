from base64 import b64decode as _b64decode, b64encode as _b64encode
from cryptography.hazmat.primitives import hashes as _hashes, padding as _padding
from cryptography.hazmat.primitives.ciphers import Cipher as _Cipher, algorithms as _algorithms, modes as _modes

class OpenSSL_AES:
    __SALT_LENGTH = 8
    __IV_LENGTH = 16
    __KEY_LENGTH = 32

    def _DeriveKey(self, password:str, salt:bytes):
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        kdf = PBKDF2HMAC(
            algorithm=_hashes.SHA256(),
            length=self.__KEY_LENGTH + self.__IV_LENGTH,
            salt=salt,
            iterations=10000
        ).derive(password.encode())
        key = kdf[:self.__KEY_LENGTH]
        iv = kdf[self.__KEY_LENGTH:]
        return key, iv
    
    def EncryptFile(self, inputPath:str, password:str, outputPath:str=None):
        from simpleworkspace.io import file

        if(outputPath is None):
            outputPath = f'{inputPath}.oscc'

        file.Create(
            outputPath,
            self.EncryptBytes(
                file.Read(inputPath, type=bytes),
                password
            )
        )
        return outputPath
    
    def DecryptFile(self, inputPath:str, password:str, outputPath:str=None):
        from simpleworkspace.io import file

        if(outputPath is None):
            outputPath = inputPath.removesuffix('.oscc')

        file.Create(
            outputPath,
            self.DecryptBytes(
                file.Read(inputPath, type=bytes),
                password
            )
        )
        return outputPath

        
    def EncryptString(self, plainText:str, password:str):
        cipherBytes = self.EncryptBytes(plainText.encode(), password)
        return _b64encode(cipherBytes).decode()
    
    def DecryptString(self, cipherText:str, password:str):
        plainBytes = self.DecryptBytes(_b64decode(cipherText), password)
        return plainBytes.decode()

    def EncryptBytes(self, plainBytes:bytes, password:str):
        import os

        salt = os.urandom(self.__SALT_LENGTH)
        key, iv = self._DeriveKey(password, salt)
        cipher = _Cipher(_algorithms.AES(key), _modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = _padding.PKCS7(_algorithms.AES.block_size).padder()
        padded_data = padder.update(plainBytes) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return b'Salted__' + salt + encrypted_data

    def DecryptBytes(self, cipherBytes:bytes, password:str):
        salt = cipherBytes[8:16] #skip first 8 of header "__Salted"
        key, iv = self._DeriveKey(password, salt)

        encrypted_data = cipherBytes[16:] #skip first 8 "__Salted" and next 8 which is the salt itself
        cipher = _Cipher(_algorithms.AES(key), _modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = _padding.PKCS7(_algorithms.AES.block_size).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return unpadded_data
