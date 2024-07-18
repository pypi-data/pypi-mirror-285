import random
import string
from faker import Faker


class QGRandom:
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
