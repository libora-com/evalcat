import abc


import pandas as pd


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

    def compute_metrics(self, base_result, k):
        """Returns a DataFrame with MultiIndex (system, query) and column metric.

        Should be called directly by ResultList to generate a summary DataFrame for this field.

        Parameters
        ----------
        base_result : BaseResult
            Contains the full search results.
        k : int, default=None
            Only use the top K results to calculate of statistics.

        Returns
        -------
        pd.DataFrame
            DataFrame with MultiIndex (system, query) and column metric.
            Contains the computed metrics for the search results.

        Notes
        -----
        Iterates over system and query, applying `at_k` to each search result list.
        """
        metrics = []
        metric_labels = []
        for system in base_result.systems:
            for query in base_result.queries:
                computed_metric = self.at_k(base_result[system][query], k=k)
                if not metric_labels:
                    metric_labels = computed_metric.keys()
                metrics.append(computed_metric.values())
        return pd.DataFrame(metrics,
                            index=pd.MultiIndex.from_product([base_result.systems, base_result.queries]),
                            columns=metric_labels)

    @abc.abstractmethod
    def at_k(self, result_list, k):
        """Computes statistics for the top K hits in a single list of search results.

        Should be overridden by the subclass to provide computation of the desired statistics.

        Parameters
        ----------
        result_list : list
            List of ranked search items for a single system and query.
        k : int
            Only use the top K results to calculate of statistics.

        Returns
        -------
        dict
            Maps the metric name to the computed metric.

        Examples
        --------
        If the two metrics implemented are `total_sum` and `mean`.

        >>> field_subclass_instance.at_k([1, 2, 3])
        {
            'total_sum': 6,
            'mean': 2
        }
        """
