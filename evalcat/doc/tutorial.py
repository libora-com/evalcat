from evalcat import ResultList
from evalcat.fields import NumericalField, CategoricalField


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

result_list = ResultList(search_results,
                         fields=[NumericalField('price'), CategoricalField('category')])


print(result_list.get_query_metric_df('price', system='new system'))
"""
       1-percentile  25-percentile  50-percentile  ...  99-percentile  total  mean
fruit         0.802           0.85            0.9  ...          0.998    1.8   0.9
"""

print(result_list.get_system_metric_df('price', query='fruit'))
"""
            1-percentile  25-percentile  ...  total  mean
old system         1.000           1.00  ...    1.0   1.0
new system         0.802           0.85  ...    1.8   0.9
"""

print(result_list.get_system_query_df('price', metric='mean'))
"""
            fruit
new system    0.9
old system    1.0
"""

print(result_list.rank_biased_overlap(identifier='id',
                                      systems=['old system', 'new system']))
"""
        rbo_min   rbo_res  rbo_ext
fruit  0.255843  0.699157     0.55
"""
