from komo import printing
from komo.types import ClientException


def handle_errors(fn):
    def inner(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except ClientException as e:
            printing.error(e.msg)
            exit(1)

    return inner
