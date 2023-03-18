import random
import string


def get_random():
    random_string = ''.join(random.choice(
                            string.ascii_letters + string.digits)
                            for _ in range(10)
                            )
    return random_string
