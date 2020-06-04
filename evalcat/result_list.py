import pandas as pd


from evalcat.base_result import BaseResult
from evalcat.fields.base import Field
from evalcat.rbo import rbo


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
    k : int
        Depth of search results for metrics to be computed.

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
        self.fields = fields if fields else []
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

    def add_fields(self, fields, k=10, replace=False):
        """Adds new fields to the ResultList and computes metrics.

        Parameters
        ----------
        fields : list of Field, or Field
            Contains the fields to be evaluated. List items should be instances of Field subclasses.
        k : int
            Depth of search results for metrics to be computed.
        replace : bool, default=False
            If false, raises ValueError if there  is already a field with the same name as the new field.
            Else it will replace the old field.
        """
        if isinstance(fields, Field):
            fields = [fields]
        for f in fields:
            if f.name in self.summary and not replace:
                raise ValueError(f'Field {f} already exists. Pass `replace=True` to override.')
            self.fields.append(f)
            self.summary[f.name] = f.compute_metrics(self.base_result, k)

    def get_query_metric_df(self, field_name, system):
        """Returns a DataFrame comparing queries against metrics for a single system.

        Parameters
        ----------
        field_name : str
            The name of the field.
        system : str
            The name of the system.

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
        field_name : str
            The name of the field.
        query : str
            The query string.

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
        field_name : str
            The name of the field.
        metric : str
            The name of the metric.

        Returns
        -------
        DataFrame
            DataFrame with index systems and column queries.
        """
        summary_field = self._get_field_from_summary(field_name)
        if metric not in summary_field.columns.values:
            raise ValueError("Metric not calculated for this field.")
        return summary_field.loc[:, metric].unstack(1)

    def rank_biased_overlap(self, identifier='id', systems=None, p=0.9):
        """Computes the rank-biased overlap (RBO) of two systems across all queries.

        Parameters
        ----------
        identifier : str
            The name of a metric that can uniquely identify a search result item.
        systems : list of str, optional
            The names of the two systems to be compared. If not provided, will compare the first two systems.
        p : float, default=0.9
            A RBO parameter modelling the user's persistence, or the probability of continuing to the next search item.
        Returns
        -------
        DataFrame
            DataFrame with index queries and columns [rbo_min, rbo_res, rbo_ext].

        Notes
        -----
        For each query, will compute the triplet (RBO_min, RBO_res, RBO_ext) between the two systems as defined in [1]_.
        The implementation accounts for uneven lists but not ties.

        .. [1] William Webber, Alistair Moffat, and Justin Zobel. 2010. A similarity measure for indefinite rankings.
           ACM Trans. Inf. Syst. 28, 4, Article 20 (November 2010), 38 pages.
           DOI:https://doi.org/10.1145/1852102.1852106
        """
        if len(self.base_result.systems) < 2:
            raise RuntimeError('There are less than 2 systems in the results but RBO requires 2 systems.')
        if systems:
            try:
                if len(systems) != 2:
                    raise ValueError('RBO can only compare 2 systems.')
                res1 = self.base_result[systems[0]]
                res2 = self.base_result[systems[1]]
            except TypeError:
                raise TypeError('`systems` must be a list containing the names of 2 systems.')
            except ValueError as e:
                raise e
            except KeyError:
                raise ValueError('Systems provided are not in results.')
        else:
            res1 = self.base_result[self.base_result.systems[0]]
            res2 = self.base_result[self.base_result.systems[1]]

        rbos = []
        for query in self.base_result.queries:
            id1 = [item[identifier] for item in res1[query]]
            id2 = [item[identifier] for item in res2[query]]
            if not id1 or not id2:
                rbos.append((None, None, None))
            else:
                rbos.append(rbo(id1, id2, p))

        return pd.DataFrame(rbos, index=self.base_result.queries, columns=['rbo_min', 'rbo_res', 'rbo_ext'])
