# This file is placed in the Public Domain.
# pylint: disable=C0413,W0212,E0401


"daemon"


from .main import background


if __name__ == "__main__":
    background()
