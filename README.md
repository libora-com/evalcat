# evalcat
​
This module aims to assist evaluating and comparing the ranked results of search systems
by providing methods to parse and compute metrics from search engine results.
​
## Installation

Evalcat can be install using pip.
```
$ pip install evalcat
``` 

Alternatively, we can manually install by cloning this repository.
```
$ git clone ...
$ cd evalcat
$ python3 setup.py install
```

## Usage

The main class in this module is `ResultList`. 
It is used in conjunction with the `Field` class to define methods to compute metrics.
​
### ResultList
This class can be constructed by passing a dictionary of search results of the following format, as well as a list of `Field` subclasses.

Note that each system is evaluated with the same query set.
```
>>> result_list = ResultList({
        "system A": {
            "query 1": [Item1, Item2],
            "query 2": [Item1, Item2, Item3],
        },
        "system B": {
            "query 1": [Item1, Item2],
            "query 2": [Item1],
        },
    }, [FieldClass('field_name')])
```

The three main comparison methods are `get_query_metric_df()`, `get_system_metric_df()` and `get_system_query_df()`.

`get_query_metric_df(field_name, system)` compares queries against metrics for a single system.
```
>>> result_list.get_query_metric_df('field_name', system='system A')
|       |metric 1|metric 2|
|-------|--------|--------|
|query 1|  0.12  |  0.45  |
|query 2|  0.32  |  0.65  |
```
`get_system_metric_df(field_name, query)` compares systems against metrics for a single query.
```
>>> result_list.get_system_metric_df('field_name', query='query 1')
|        |metric 1|metric 2|
|--------|--------|--------|
|system 1|  0.12  |  0.45  |
|system 2|  0.34  |  0.56  |
```
`get_system_query_df(field_name, metric)` compares systems against queries for a single metric.
```
>>> result_list.get_system_query_df('field_name', metric='metric 1')
|        |query 1|query 2|
|--------|-------|-------|
|system 1|  0.12 |  0.32 |
|system 2|  0.34 |  0.76 |
```

### Field

The `Field` abstract base class corresponds to a field in a document.
This class is designed to be subclassed so that each field will have its own implementation of the required metrics.

The abstract method designed to be overridden is the `at_k(result_list, k)` method, 
which should contain the implementation of metrics for the top `k` items in a ranked result list.

A simple implementation example would be the mean price of the top `k` items.
```
def at_k(result_list, k):
    return {
        "mean_price": sum(item.price for item in result_list[:k]) / len(result_list[:k])
    }
```

## Testing

To run the tests in this module, run the following command.
```
>>> python3 -c 'from evalcat.tests import test; test()'
```

## Dependencies

- numpy
- pandas >= 1.0.1