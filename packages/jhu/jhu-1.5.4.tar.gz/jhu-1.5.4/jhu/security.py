"""
安全模块工具
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bcrypt import checkpw, gensalt, hashpw
from base64 import b64decode, b64encode
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from jose import jwt


class AESAPI:
    def __init__(self, key: str) -> None:
        # ECB模式,加密结果固定
        self._cipher = AES.new(key.encode(), AES.MODE_ECB)

    @property
    def cipher(self):
        return self._cipher

    def encrypt(self, plain_text: str) -> str:
        """加密:pad->encrypt->b64encode
        """

        # 对明文进行补全至块大小的填充
        padded_text = pad(plain_text.encode(), AES.block_size)

        # 加密
        ciphertext = self.cipher.encrypt(padded_text)

        # 返回Base64编码的密文
        return b64encode(ciphertext).decode()

    def decrypt(self, encrypted_value: str) -> str:
        """解密:b64decode->decrypt->unpad
        """

        # 将Base64编码的密文解码为字节
        ciphertext = b64decode(encrypted_value)

        # 解密
        decrypted_text = unpad(self.cipher.decrypt(ciphertext), AES.block_size)

        # 将解密后的字节串转换回字符串
        return decrypted_text.decode()


class HashAPI:
    def hash(self, plain_text: str) -> str:
        """明文哈希加密
        """
        return hashpw(plain_text.encode(), gensalt()).decode()

    def verify(self, plain_text: str, hash_text: str) -> bool:
        """验证明文和密文的内容是否一致
        """
        return checkpw(plain_text.encode(), hash_text.encode())


class JWTAPI:
    def __init__(self, key: str, expire_min: int, algorithm: str = "HS256") -> None:
        """JWT对象

        Args:
            key:str,密钥
            expire_min:int,token的有效期(分钟)
            algorithm:str,加密算法

        """
        self.__key = key
        self.__algorithm = algorithm
        self.expire = expire_min

    @property
    def key(self):
        return self.__key

    @property
    def algorithm(self):
        return self.__algorithm

    def encode(self, **kw) -> str:
        """编码JWT的token
        """
        # expire = datetime.utcnow() + timedelta(minutes=self.expire)
        expire = datetime.now(ZoneInfo("UTC")) + timedelta(minutes=self.expire)
        payload = dict(**kw, exp=expire)
        return jwt.encode(payload, key=self.key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        """解码JWT的token
        """
        return jwt.decode(token=token, key=self.key, algorithms=self.algorithm)


if __name__ == "__main__":
    ...
