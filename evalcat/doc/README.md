# How to use evalcat

This goes through a trivialized scenario using the features of evalcat.
We want to compare the performance of two systems, named `"old system"` and `"new system"`,
given a query set containing one query, "fruit".

## Loading search results

The search results is given as a dictionary which maps system names to an 
inner dictionary which contains a mapping from queries to their search results.

The search results should be a list of items, each represented as a dictionary.
```
search_results = {
    "old system": {
        "fruit": [{'id': '53', 'name': 'Orange', 'price': 1.00, 'category': 'fruit'},
                  {'id': '813', 'name': 'Fruitcake', 'price': 3.15, 'category': 'cake'}]
    },
    "new system": {
        "fruit": [{'id': '53', 'name': 'Orange', 'price': 1.00, 'category': 'fruit'},
                  {'id': '17', 'name': 'Apple', 'price': 0.80, 'category': 'fruit'}]
    },
}
```

## Using ResultList and Fields

Let's say we want to study the behaviour of the `price` and `category` fields. 
The subclasses of `Field` implement methods for the computation of metrics.
For example, `NumericalField` is used for fields with decimal values and include percentile metrics, 
while `CategoricalField` is used for fields with discrete values. 

```
>>> result_list = ResultList(search_results,
                             fields=[NumericalField('price'), CategoricalField('category')])
```

## Viewing the results

The three main comparison methods are `get_query_metric_df()`, `get_system_metric_df()` and `get_system_query_df()`.

We can use `get_query_metric_df(field_name, system)` to see how a system performs across queries.
```
>>> result_list.get_query_metric_df('price', system='new system')

|     |1-percentile|25-percentile| ... |total|mean|
|-----|------------|-------------| ... |-----|----|
|fruit|    0.802   |     0.998   | ... | 1.8 | 0.9|
```
Or we can use `get_system_metric_df(field_name, query)` to compare the performance
 of the systems for a certain query.
```
>>> result_list.get_system_metric_df('price', query='fruit')

|          |1-percentile|25-percentile| ... |total| mean|
|----------|------------|-------------| ... |-----|-----|
|old system|   1.0215   |    1.5375   | ... | 4.15|2.075|
|new system|   0.8020   |    0.8500   | ... | 1.80|0.900|
```
Finally we can use `get_system_query_df(field_name, metric)` which compares 
systems against queries for a single metric.
```
>>> result_list.get_system_query_df('price', metric='mean')
|          | fruit|
|----------|------|
|new system| 0.900|
|old system| 2.075|
```

### Other methods

Other methods that are useful in the comparison between systems include rank-biased overlap
(RBO).
```
>>> result_list.rank_biased_overlap(identifier='id',
                                    systems=['old system', 'new system'])
|     | rbo_min | rbo_res | rbo_ext |
|-----|---------|---------|---------|
|fruit| 0.255843| 0.699157|    0.55 |
```
