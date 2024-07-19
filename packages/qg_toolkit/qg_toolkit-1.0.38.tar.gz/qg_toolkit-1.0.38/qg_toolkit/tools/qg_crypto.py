import hashlib


class QGCrypto:
    @staticmethod
    def md5_hash(text):
        md5_hasher = hashlib.md5()
        md5_hasher.update(text.encode('utf-8'))
        return md5_hasher.hexdigest()

    @staticmethod
    def sha256_hash(text):
        sha256_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return sha256_hash

    @staticmethod
    def google_author(secret_key):
        import pyotp
        import time
        # 替换为您的谷歌身份验证器密钥
        # secret_key = f"{self.phone}"
        # 创建一个TOTP对象
        totp = pyotp.TOTP(secret_key)
        # 获取当前时间戳
        current_time = int(time.time())
        # 获取谷歌验证码
        otp = totp.at(current_time)
        # 获取谷歌验证码的有效期剩余秒数
        remaining_seconds = totp.interval - (current_time % totp.interval)
        print(f"谷歌验证码:{otp}", f"有效期剩余秒数:{remaining_seconds}")
