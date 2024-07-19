import random
import string
from faker import Faker
class RandomGenerator:
    fake = Faker(locale="en_US")
    suffix = "@gmailiil.com"
    @classmethod
    def generate_random_name(cls):
        name = cls.fake.name().replace(" ", "").lower()
        return name

    @classmethod
    def generate_first_name(cls):
        name = cls.fake.name()
        return name.split(' ')[0]

    @classmethod
    def generate_random_email(cls, length):
        username = ''.join(random.choices(string.ascii_lowercase, k=length))
        email = f'{username}{cls.suffix}'
        return email

    @classmethod
    def generate_random_str(cls, length):
        return ''.join(random.choices(string.ascii_lowercase, k=length))





# # 使用示例
# random_name = RandomGenerator.generate_random_name()
# print(random_name)
# random_email = RandomGenerator.generate_random_email(10)
# print(random_email)
# print()
# 提供的值和类型
# value = '0x9f0e54337d515a9daa2e9cc05580b1993ebb18e2ebc465cf3ee6e777df369e2b'
#
# # 去除前缀 '0x' 并将其解码为bytes类型
# bytes32_value = bytes.fromhex(value[2:])
#
# # 打印结果
# print(bytes32_value)
# print(RandomGenerator.generate_random_name())