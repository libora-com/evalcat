from evaluation.base_result import BaseResult
from evaluation.fields.base import Field


class ResultList:
    """
    ResultList provides methods for evaluation of search systems over queries and metrics.

    Parameters
    ----------
    results : dict, or BaseResult
        Dict should be structured as follows
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
    fields : list of Field
        Contains the fields to be evaluated. List items should be instances of Field subclasses.

    Attributes
    ----------
    base_result : BaseResult
        Stores the search results.
    fields : list of Field
        Contains a list of Field subclass instances.
    summary : pd.DataFrame
        DataFrame with MultiIndex (system, query) and column metric.
        Contains the computed metrics for the search results.

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
            summary[field.name] = field.compute_metrics(self.base_result, k)
        return summary

    def _get_field_from_summary(self, field_name):
        if isinstance(field_name, str):
            if field_name not in self.summary:
                raise ValueError("Field is not in result_list.")
            else:
                return self.summary[field_name]
        else:
            raise TypeError("`field_name` must be a string.")

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
        if system not in self.base_result.systems:
            raise ValueError("System not in result_list.")
        return self._get_field_from_summary(field_name).loc[system]

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
        if query not in self.base_result.queries:
            raise ValueError("Query not in result_list.")
        return self._get_field_from_summary(field_name).xs(query, level=1)

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
        summary_field = self._get_field_from_summary(field_name)
        if metric not in summary_field.columns.values:
            raise ValueError("Metric not calculated for this field.")
        return summary_field.loc[:, metric].unstack(1)
