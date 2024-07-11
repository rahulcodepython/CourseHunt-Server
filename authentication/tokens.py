import random


def create_uid() -> int:
    return random.randint(1000, 9999)


def create_token() -> int:
    return random.randint(1000, 9999)