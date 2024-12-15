import random
import string


def generate_random_code(length=4):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))
