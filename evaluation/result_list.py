class ResultList:
    """
    ResultList provides methods for evaluation of search systems over queries and metrics.

    Parameters
    ----------
    results
        Search results defined in the README. TODO: Should give the ES results its own class for simplicity [1].
    fields : list of Field
        Contains the fields to be evaluated

    Methods
    -------
    get_query_metric_matrix(system)
        Returns a DataFrame comparing queries against metrics for a single system.
    get_system_metric_matrix(query)
        Returns a DataFrame comparing systems against metrics for a single query.
    get_system_query_matrix(metric)
        Returns a DataFrame comparing systems against queries for a single metric.
    """
    def __init__(self, results, fields):
        self.results = results
        self.fields = fields

    def _get_results(self, system=None, query=None, metric=None):
        if system and not query and not metric:
            return
        elif query and not system and not metric:
            return
        elif metric and not system and not metric:
            return
        else:
            raise ValueError()

    def get_query_metric_matrix(self, system):
        """Returns a DataFrame comparing queries against metrics for a single system.

        Parameters
        ----------
        system : str
            The name of the system.

        Returns
        -------
        DataFrame
            DataFrame with index queries and column metrics.
        """
        return self._get_results(system=system)

    def get_system_metric_matrix(self, query):
        """Returns a DataFrame comparing systems against metrics for a single query.

        Parameters
        ----------
        query : str
            The query string.

        Returns
        -------
        DataFrame
            DataFrame with index systems and column metrics.
        """
        return self._get_results(query=query)

    def get_system_query_matrix(self, metric):
        """Returns a DataFrame comparing systems against queries for a single metric.

        Parameters
        ----------
        metric : str
            The name of the metric.

        Returns
        -------
        DataFrame
            DataFrame with index systems and column queries.
        """
        return self._get_results(metric=metric)
