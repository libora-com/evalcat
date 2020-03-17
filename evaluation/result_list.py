import pandas as pd


from .base_result import BaseResult


class ResultList:
    """
    ResultList provides methods for evaluation of search systems over queries and metrics.

    Parameters
    ----------
    results
        BaseResult-like search results.
    fields : list of Field
        Contains the fields to be evaluated

    Methods
    -------
    get_query_metric_df(field_name, system)
        Returns a DataFrame comparing queries against metrics for a single system and field.
    get_system_metric_df(field_name, query)
        Returns a DataFrame comparing systems against metrics for a single query and field.
    get_system_query_df(field_name, metric)
        Returns a DataFrame comparing systems against queries for a single metric and field.
    """
    def __init__(self, results, fields=None, k=10, **kwargs):
        if isinstance(results, BaseResult):
            self.base_result = results
        else:
            self.base_result = BaseResult(results, **kwargs)
        self.fields = fields
        self.summary = self._compute_summary(k)

    def _compute_summary(self, k=10):
        summary = {}
        for field in self.fields:
            summary[field.name] = field.at_k(self.base_result.result, k)
        return summary

    def get_query_metric_df(self, field_name, system):
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
        }, index=self.base_result.queries)

    def get_system_metric_df(self, field_name, query):
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
        }, index=self.base_result.systems)

    def get_system_query_df(self, field_name, metric):
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
            ] for query in self.base_result.queries
        }, index=self.base_result.systems)
