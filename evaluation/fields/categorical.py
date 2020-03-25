from evaluation.fields.base import Field


class CategoricalField(Field):
    """
    CategoricalField provides methods for the computation of metrics for fields with categorical (discrete) values.

    Parameters
    ----------
    name : str
        The name of the field indexed in each search item.
    labels : list of int or float, optional
        List containing all labels of the field, across all systems and queries.
        If not provided, `_get_labels` will be called to retrieve label values.
    ignore_none : bool, default=True
        If set to True, will ignore items with None or "" labels, or if `labels` are provided, will ignore
        labels not in that list. Else if set to False, all the aforementioned labels will be mapped to None.
    """

    def __init__(self, name, labels=None, ignore_none=True):
        super().__init__(name)
        if labels:
            self.labels = set(labels)
        else:
            self.labels = None
        self.ignore_none = ignore_none

    def process_base_result(self, base_result):
        if not self.labels:
            self.labels = self._get_labels(base_result)

    def _get_labels(self, base_result):
        """Returns a set containing all unique labels from the corresponding Field in BaseResult.

        Iterates over all systems, queries and items, returning all unique labels in the Field.
        If `self.ignore_none` is True, ignores labels that are empty strings or None.

        Returns
        -------
        labels : set
            Contains all labels in BaseResult.

        Notes
        -----
        Since this function will iterate over all systems, queries and items, it might take a long time for large
        result lists. An alternative would be to pass a list of labels to the constructor to skip this step.
        """
        labels = set()
        for system_row in base_result.values():
            for query_row in system_row.values():
                for item in query_row:
                    if item[self.name]:
                        labels.add(item[self.name])
                    elif not self.ignore_none:
                        labels.add(None)
        return labels

    def at_k(self, result_list, k=None):
        if not result_list:
            metrics = {label: None for label in self.labels}
            metrics['unique_count'] = None
            return metrics
        if not k:
            k = len(result_list)

        metrics = {label: 0 for label in self.labels}
        unique_labels = set()
        total_count = 0

        for item in result_list[:k]:
            label = item[self.name]
            if label in self.labels:
                metrics[label] += 1
                total_count += 1
                unique_labels.add(label)
            elif not self.ignore_none:  # Catches other labels
                metrics[None] += 1
                unique_labels.add(None)
                total_count += 1

        if len(result_list[:k]) > 0:
            metrics = {key: v / total_count for key, v in metrics.items()}
        metrics['unique_count'] = len(unique_labels)

        return metrics
