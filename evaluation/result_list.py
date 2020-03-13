import pandas as pd


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
    get_query_metric_matrix(field_name, system)
        Returns a DataFrame comparing queries against metrics for a single system and field.
    get_system_metric_matrix(field_name, query)
        Returns a DataFrame comparing systems against metrics for a single query and field.
    get_system_query_matrix(field_name, metric)
        Returns a DataFrame comparing systems against queries for a single metric and field.
    """
    def __init__(self, results, fields=None, k=10):
        self.results = results
        self.fields = fields
        self.summary = self._compute_summary(k)

    def _compute_summary(self, k=10):
        summary = {}
        for field in self.fields:
            summary[field.name] = field.at_k(self.results, k)
        return summary

    def get_query_metric_matrix(self, field_name, system):
        """Returns a DataFrame comparing queries against metrics for a single system.

        Parameters
        ----------
        system : str
            The name of the system.
        field_name : str
            The name of the field.

        Returns
        -------
        DataFrame
            DataFrame with index queries and column metrics.
        """
        return pd.DataFrame({
            metric: [
                val[metric] for val in self.summary[field_name][system].values()
            ] for metric in ['metric_sum', 'metric_product']
        }, index=self.summary[field_name][system].keys())

    def get_system_metric_matrix(self, field_name, query):
        """Returns a DataFrame comparing systems against metrics for a single query.

        Parameters
        ----------
        query : str
            The query string.
        field_name : str
            The name of the field.

        Returns
        -------
        DataFrame
            DataFrame with index systems and column metrics.
        """
        return pd.DataFrame({
            metric: [
                val[query][metric] for val in self.summary[field_name].values()
            ] for metric in ['metric_sum', 'metric_product']
        }, index=self.summary[field_name].keys())

    def get_system_query_matrix(self, field_name, metric):
        """Returns a DataFrame comparing systems against queries for a single metric.

        Parameters
        ----------
        metric : str
            The name of the metric.
        field_name : str
            The name of the field.

        Returns
        -------
        DataFrame
            DataFrame with index systems and column queries.
        """
        return pd.DataFrame({
            query: [
                val[query][metric] for val in self.summary[field_name].values()
            ] for query in ['query 1', 'query 2', 'query 3']
        }, index=self.summary[field_name].keys())
