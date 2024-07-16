# This file is placed in the Public Domain.
# pylint: disable=R0903


"caching"


from .object import Object


class Broker:

    "Broker"

    def __init__(self):
        self.objs = Object()


def get(obj, orig):
    "return object by origin (repr)"
    return getattr(obj.objs, orig, None)


def register(obj, obj2):
    "add an object to the broker."
    ids = object.__repr__(obj2)
    setattr(obj.objs, ids, obj2)


def __dir__():
    return (
        'Broker',
        'get',
        'register'
    )
