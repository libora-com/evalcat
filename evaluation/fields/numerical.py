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
    """
    def __init__(self, name, percentiles=None):
        super().__init__(name)
        if percentiles:
            self.percentiles = percentiles
        else:
            self.percentiles = [1, 25, 50, 75, 99]

    def at_k(self, result_list, k=10):
        total = sum(item[self.name] for item in result_list[:k])
        percents = percentile([item['price'] for item in result_list[:k]], self.percentiles)
        metrics = {
            f'{n}-percentile': percents[idx] for idx, n in self.percentiles
        }

        metrics['total'] = total
        metrics['average'] = total / len(result_list[:k])

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
        return None
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
