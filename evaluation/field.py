import abc


class Field(abc.ABC):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    @abc.abstractmethod
    def at_k(self, res, k=10):
        """Returns a dictionary containing statistics for the top K hits returned by the system.
        Should return an empty dictionary if not supported.
        """
