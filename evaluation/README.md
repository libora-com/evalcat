# Evaluation
​
This module for evaluating and comparing the ranked results of search systems.
This module is built to parse and compute metrics from search engine results.
​
## Usage
​
The main class for use is `ResultList`.
It can be constructed by passing a dictionary of search results of the following format, as well as a list of `Field` subclasses.

The `Field` abstract base class corresponds to a field in a document.
This class is designed to be subclassed so that each field will have its own implementation of the required metrics.


Note that each system is evaluated with the same query set.
```
>>> result_list = ResultList({
        'system A': {
            'query 1': [Result1, Result2, Result3],
            'query 2': [Result1],
            'query 3': [Result1, Result2],
        }, 'system B': {
            'query 1': [Result1, Result2],
            'query 2': [Result1, Result2],
            'query 3': [Result1, Result2],
        }
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

## Testing

To run the tests in this module, run the following command.
```
>>> python3 -m unittest discover evaluation.tests
```