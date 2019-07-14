try:
    import secrets
except ImportError:
    import random as secrets
import string
import imp
import sys

DEFAULT_CHAR_STRING = string.ascii_lowercase + string.digits
DEFAULT_CHAR_INTS = string.digits
MAXIMUM_SLUG_LENGTH = 252

DEFAULT_SIZE = 8


def complete_digit(digit, length=2):
    """
    A function to complete the left side of a INTEGER with '0' to fill the length desired
    Returns a CHAR.
    """
    length = int(length)
    digit = int(digit)  # Convert To Int
    str_digit = "%s" % digit  # Convert To String in Order to have the Length
    digit_length = len(str_digit)

    if digit_length >= length:
        return str_digit
    else:
        i = 1
        while i <= (length - digit_length):
            str_digit = "0" + str_digit
            i = i + 1
        return str_digit


def generate_random_string(chars=DEFAULT_CHAR_STRING, size=6):
    return "".join(secrets.choice(chars) for _ in range(size))


def generate_random_ints(chars=DEFAULT_CHAR_INTS, size=6):
    return "".join(secrets.choice(chars) for _ in range(size))


def generate_url_token(size=None):
    if not size or not isinstance(size, int):
        size = DEFAULT_SIZE

    try:
        return secrets.token_urlsafe(size)
    except:
        return generate_random_string()
