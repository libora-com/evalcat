class BaseResult(dict):
    """
    BaseResult stores the search results and handles reading from other data stores.

    Parameters
    ----------
    results : dict
        Nested python dictionary of search results. The structure should be
        ```
        {
            "system A": {
                "query 1": [Item1, Item2],
                "query 2": [Item1, Item2, Item3],
            },
            "system B": {
                "query 1": [Item1, Item2],
                "query 2": [Item1],
            },
        }
        ```
    queries : list of str, default=None
        A list of queries. Used in a call to `_check_queries` to check that all systems have the same query set.

    Attributes
    ----------
    systems : list
        Stores the list of system names.
    queries : list
        Stores the list of queries.
    """

    def __init__(self, results, queries=None):
        super().__init__(results)
        self.systems = list(results.keys()) if results else []
        self.queries = _check_queries(results, queries) if results else []


def _check_queries(results, queries=None):
    """Check that all systems have the same query set and returns a list of queries.

    Parameters
    ----------
    results : dict
        Contains the full search results.
    queries : list of str, default=None
        A list of queries. If not provided, the query set will be generated from the first system's queries.

    Returns
    -------
    queries : list of str
        A list of queries.

    Raises
    ------
    ValueError
        If not all systems have the same query set.
    """

    if not queries:
        queries = list(next(iter(results.values())).keys())

    if not all(set(queries) == set(query_res.keys()) for query_res in results.values()):
        raise ValueError('Not all query sets match the input queries.')
    return queries
