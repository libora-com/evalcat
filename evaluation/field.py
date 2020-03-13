import abc


class Field(abc.ABC):
    """Abstract base class for all fields.

    The Field class is akin to the field in Elasticsearch or a column in a relational database.

    Params
    ------
    name : str
        Name of the field must be the same as the field in the search results.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    @abc.abstractmethod
    def at_k(self, results, k=None):
        """Computes statistics for the top K hits returned by the system.

        Should be overridden by the subclass to provide computation of the desired statistics.

        Parameters
        ----------
        results
            Search results defined in the README. TODO: Should give the ES results its own class for simplicity [1].
        k : int, default=None
            Only use the top K results to calculate of statistics.

        Returns
        -------
        dict
            Contains computed statistics. TODO: Should give the results its own class as well [2].
        """
