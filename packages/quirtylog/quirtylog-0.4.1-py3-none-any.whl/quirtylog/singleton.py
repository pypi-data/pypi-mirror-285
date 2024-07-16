"""
------------
singleton.py
------------

A package for singleton creation
"""

__all__ = ["singleton"]


class _SingletonWrapper(object):
    """
    A singleton wrapper class. Its instances would be created
    for each decorated class.
    """

    def __init__(self, cls):
        """Initialize the class"""
        self.__wrapped__ = cls
        self._instance = None

    def __call__(self, *args, **kwargs):
        """Return a single instance of decorated class"""
        if self._instance is None:
            self._instance = self.__wrapped__(*args, **kwargs)
        return self._instance


def singleton(cls):
    """
    Create a singleton object.

    Returns a wrapper objects. A call on that object
    returns a single instance object of decorated class. Use the __wrapped__
    attribute to access decorated class directly in unit tests
    """
    return _SingletonWrapper(cls)


if __name__ == "__main__":
    pass
