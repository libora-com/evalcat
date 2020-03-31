import math


from evaluation.fields.base import Field


class NumericalField(Field):
    """
    NumericalField provides methods for the computation of metrics for fields with numerical (continuous) values.

    Parameters
    ----------
    name : str
        The name of the field indexed in each search item.
    percentiles : list of int or float, optional
        Contains the percentiles to compute. If not provided, will default to [1, 25, 50, 75, 99].
    ignore_none : bool, default=True
        If set to True, will ignore field values that are 'None'.
        Else if set to False, will convert all 'None' values to 0.
    """
    def __init__(self, name, percentiles=None, ignore_none=True):
        super().__init__(name)
        if percentiles:
            self.percentiles = percentiles
        else:
            self.percentiles = [1, 25, 50, 75, 99]
        self.ignore_none = ignore_none

    def at_k(self, result_list, k=None):
        if not k:
            k = len(result_list)

        field_values = []
        total = 0
        for item in result_list[:k]:
            val = item[self.name]
            if val is not None:
                total += val
                field_values.append(val)
            elif not self.ignore_none:
                field_values.append(0)

        if not field_values:  # No field values can be retrieved.
            metrics = {f'{n}-percentile': None for n in self.percentiles}
            metrics['total'] = None
            metrics['mean'] = None
            return metrics

        percents = percentile(field_values, self.percentiles)
        metrics = {
            f'{n}-percentile': percents[idx] for idx, n in enumerate(self.percentiles)
        }
        metrics['total'] = total
        metrics['mean'] = total / len(field_values)

        return metrics


def percentile(arr, percentiles):
    """Computes the percentile values in an array.

    Parameters
    ----------
    arr : list of int or float
        Input array.
    percentiles : list of int or float
        List of percentile values to compute, must be between 0 and 100 inclusive.

    Returns
    ------
    output : list
        Output array of the same length as `percentiles`.
    """
    if not arr:
        return []
    arr = list(sorted(arr))
    output = [0] * len(percentiles)
    for idx, p in enumerate(percentiles):
        x = (len(arr) - 1) * (p / 100)
        f = math.floor(x)
        c = math.ceil(x)
        if f == c:
            output[idx] = arr[int(x)]
        else:
            output[idx] = (c - x) * arr[int(f)] + (x - f) * arr[int(c)]
    return output
