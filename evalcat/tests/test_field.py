import unittest

import pandas as pd

from evalcat.base_result import BaseResult
from evalcat.fields.categorical import CategoricalField
from evalcat.fields.numerical import NumericalField


"""Mock functions for testing ResultList."""


# Defines a document (search result item) in our collection.
class Result(dict):
    def __init__(self, categorical_value, numerical_value):
        super().__init__(categorical_field=categorical_value, numerical_field=numerical_value)


# Input results.
MOCK_RESULTS = {
    'system A': {
        'query 1': [Result('a', 5), Result('b', 2), Result('c', 1)],
        'query 2': [Result('a', 1), Result('a', 3)],
        'query 3': [Result('a', 5), Result('c', 2)],
    }, 'system B': {
        # System B contains empty result lists, some results have None in either fields.
        'query 1': [],
        'query 2': [Result(None, 4), Result('a', 1)],
        'query 3': [Result('b', 4), Result(None, None), Result('a', 2), Result('c', None)],
    }
}

# Mock result (Output DataFrame will be made from this).
CATEGORICAL_RESULTS_1 = {
    'system A': {
        'query 1': {'unique_count': 3, 'a': 1/3, 'b': 1/3, 'c': 1/3},
        'query 2': {'unique_count': 1, 'a': 1, 'b': 0.0, 'c': 0.0},
        'query 3': {'unique_count': 2, 'a': 1/2, 'b': 0.0, 'c': 1/2},
    },
    'system B': {
        'query 1': {'unique_count': None, 'a': None, 'b': None, 'c': None},
        'query 2': {'unique_count': 1, 'a': 1, 'b': 0.0, 'c': 0.0},
        'query 3': {'unique_count': 3, 'a': 1/3, 'b': 1/3, 'c': 1/3},
    }
}

CATEGORICAL_RESULTS_2 = {
    'system A': {
        'query 1': {'unique_count': 3, 'a': 1/3, 'b': 1/3, 'c': 1/3, None: 0.0},
        'query 2': {'unique_count': 1, 'a': 1, 'b': 0.0, 'c': 0.0, None: 0.0},
        'query 3': {'unique_count': 2, 'a': 1/2, 'b': 0.0, 'c': 1/2, None: 0.0},
    },
    'system B': {
        'query 1': {'unique_count': None, 'a': None, 'b': None, 'c': None, None: None},
        'query 2': {'unique_count': 2, 'a': 1/2, 'b': 0.0, 'c': 0.0, None: 1/2},
        'query 3': {'unique_count': 4, 'a': 1/4, 'b': 1/4, 'c': 1/4, None: 1/4},
    }
}

NUMERICAL_RESULTS_1 = {
    'system A': {
        'query 1': {'25-percentile': 1.5, '50-percentile': 2.0, '75-percentile': 3.5, 'total': 8, 'mean': 8/3},
        'query 2': {'25-percentile': 1.5, '50-percentile': 2.0, '75-percentile': 2.5, 'total': 4, 'mean': 2.0},
        'query 3': {'25-percentile': 2.75, '50-percentile': 3.5, '75-percentile': 4.25, 'total': 7, 'mean': 3.5},
    },
    'system B': {
        'query 1': {'25-percentile': None, '50-percentile': None, '75-percentile': None, 'total': None, 'mean': None},
        'query 2': {'25-percentile': 1.75, '50-percentile': 2.5, '75-percentile': 3.25, 'total': 5, 'mean': 2.5},
        'query 3': {'25-percentile': 2.5, '50-percentile': 3.0, '75-percentile': 3.5, 'total': 6, 'mean': 3.0},
    }
}

NUMERICAL_RESULTS_2 = {
    'system A': {
        'query 1': {'25-percentile': 1.5, '50-percentile': 2.0, '75-percentile': 3.5, 'total': 8, 'mean': 8/3},
        'query 2': {'25-percentile': 1.5, '50-percentile': 2.0, '75-percentile': 2.5, 'total': 4, 'mean': 2.0},
        'query 3': {'25-percentile': 2.75, '50-percentile': 3.5, '75-percentile': 4.25, 'total': 7, 'mean': 3.5},
    },
    'system B': {
        'query 1': {'25-percentile': None, '50-percentile': None, '75-percentile': None, 'total': None, 'mean': None},
        'query 2': {'25-percentile': 1.75, '50-percentile': 2.5, '75-percentile': 3.25, 'total': 5, 'mean': 2.5},
        'query 3': {'25-percentile': 0.0, '50-percentile': 1.0, '75-percentile': 2.5, 'total': 6, 'mean': 1.5},
    }
}


"""Test Classes"""


class TestCategoricalField(unittest.TestCase):
    def test_get_labels(self):
        field = CategoricalField('categorical_field')

        mock_labels = field._get_labels(BaseResult(MOCK_RESULTS))
        self.assertEqual(mock_labels, {'a', 'b', 'c'})

        mock_labels2 = field._get_labels(BaseResult({'system A': {
                'query 1': [Result('a', 5), Result('c', 1)],
            }, 'system B': {
                'query 1': [Result('b', 8), Result('b', 3)],
            }
        }))
        self.assertEqual(mock_labels2, {'a', 'b', 'c'})

    def test_at_k(self):
        field_ab = CategoricalField('categorical_field', labels=['a', 'b'])
        field_abc = CategoricalField('categorical_field', labels=['a', 'b', 'c'])
        field_abn = CategoricalField('categorical_field', labels=['a', 'b', None], ignore_none=False)

        result_abb = [Result('a', 5), Result('b', 2), Result('b', 1)]
        result_abc = [Result('a', 5), Result('b', 2), Result('c', 1)]
        result_abn = [Result('a', 5), Result('b', 2), Result(None, 1)]

        # Labels match results exactly.
        self.assertEqual(field_ab.at_k(result_abb, k=10), {
            'unique_count': 2, 'a': 1/3, 'b': 2/3,
        })
        # Results are a subset of labels.
        self.assertEqual(field_abc.at_k(result_abb, k=10), {
            'unique_count': 2, 'a': 1/3, 'b': 2/3, 'c': 0.0
        })
        # Results are a subset of labels, k smaller than results length.
        self.assertEqual(field_abc.at_k(result_abc, k=1), {
            'unique_count': 1, 'a': 1, 'b': 0.0, 'c': 0.0
        })
        # Labels are a subset of results.
        self.assertEqual(field_ab.at_k(result_abc, k=10), {
            'unique_count': 2, 'a': 0.5, 'b': 0.5,
        })
        # None in results but `ignore_none=True`.
        self.assertEqual(field_ab.at_k(result_abn, k=10), {
            'unique_count': 2, 'a': 0.5, 'b': 0.5,
        })
        # None in results and `ignore_none=False`.
        self.assertEqual(field_abn.at_k(result_abn, k=10), {
            'unique_count': 3, 'a': 1/3, 'b': 1/3, None: 1/3
        })
        # Labels are a subset of results and `ignore_none=False`.
        self.assertEqual(field_abn.at_k(result_abc, k=10), {
            'unique_count': 3, 'a': 1/3, 'b': 1/3, None: 1/3
        })
        # Empty results.
        self.assertEqual(field_abn.at_k([], k=10), {
            'unique_count': None, 'a': None, 'b': None, None: None
        })

    def test_compute_metrics(self):
        columns = ['unique_count', 'a', 'b', 'c']
        index = pd.MultiIndex.from_product([['system A', 'system B'], ['query 1', 'query 2', 'query 3']])

        field = CategoricalField('categorical_field')
        pd.testing.assert_frame_equal(
            field.compute_metrics(BaseResult(MOCK_RESULTS), k=10).reindex(columns, axis=1),
            pd.DataFrame(
                [(i['unique_count'], i['a'], i['b'], i['c'])
                 for results in CATEGORICAL_RESULTS_1.values() for i in results.values()],
                index=index,
                columns=columns
            )
        )
        # Empty results.
        pd.testing.assert_frame_equal(
            field.compute_metrics(BaseResult({}), k=10),
            pd.DataFrame(
                [],
                index=pd.MultiIndex.from_product([[], []]),
                columns=[]
            )
        )
        field2 = CategoricalField('categorical_field', ignore_none=False)
        pd.testing.assert_frame_equal(
            field2.compute_metrics(BaseResult(MOCK_RESULTS), k=10).reindex(columns, axis=1),
            pd.DataFrame(
                [(i['unique_count'], i['a'], i['b'], i['c'])
                 for results in CATEGORICAL_RESULTS_2.values() for i in results.values()],
                index=index,
                columns=columns
            )
        )


class TestNumericalField(unittest.TestCase):
    def test_at_k(self):
        field_a = NumericalField('numerical_field')
        field_b = NumericalField('numerical_field', percentiles=[25, 50, 75])
        field_c = NumericalField('numerical_field', percentiles=[25, 50, 75], ignore_none=False)

        result_a = [Result('a', 5), Result('b', 2), Result('b', 1)]
        result_b = [Result('a', 4), Result('b', 2), Result(None, None)]

        # Default percentiles [1, 25, 50, 75, 99].
        self.assertEqual(field_a.at_k(result_a, k=10), {
            '1-percentile': 1.02, '25-percentile': 1.5, '50-percentile': 2.0, '75-percentile': 3.5,
            '99-percentile': 4.94, 'total': 8, 'mean': 8/3
        })
        # Percentiles [25, 50, 75].
        self.assertEqual(field_b.at_k(result_a, k=10), {
            '25-percentile': 1.5, '50-percentile': 2.0, '75-percentile': 3.5, 'total': 8, 'mean': 8/3
        })
        # Percentiles [25, 50, 75], k smaller than results length.
        self.assertEqual(field_b.at_k(result_a, k=1), {
            '25-percentile': 5, '50-percentile': 5, '75-percentile': 5, 'total': 5, 'mean': 5.0
        })
        # Percentiles [25, 50, 75], None in results, but `ignore_none=True`.
        self.assertEqual(field_b.at_k(result_b, k=10), {
            '25-percentile': 2.5, '50-percentile': 3.0, '75-percentile': 3.5, 'total': 6, 'mean': 3.0
        })
        # Percentiles [25, 50, 75], None in results, and `ignore_none=False`.
        self.assertEqual(field_c.at_k(result_b, k=10), {
            '25-percentile': 1.0, '50-percentile': 2.0, '75-percentile': 3.0, 'total': 6, 'mean': 2.0
        })
        # Empty results
        self.assertEqual(field_b.at_k([], k=10), {
            '25-percentile': None, '50-percentile': None, '75-percentile': None, 'total': None, 'mean': None
        })

    def test_compute_metrics(self):
        index = pd.MultiIndex.from_product([['system A', 'system B'], ['query 1', 'query 2', 'query 3']])

        field = NumericalField('numerical_field', percentiles=[25, 50, 75])
        pd.testing.assert_frame_equal(
            field.compute_metrics(BaseResult(MOCK_RESULTS), k=10).sort_index(axis=1),
            pd.DataFrame(
                [(i['25-percentile'], i['50-percentile'], i['75-percentile'], i['total'], i['mean'])
                 for results in NUMERICAL_RESULTS_1.values() for i in results.values()],
                index=index,
                columns=['25-percentile', '50-percentile', '75-percentile', 'total', 'mean']
            ).sort_index(axis=1)
        )
        # Empty results.
        pd.testing.assert_frame_equal(
            field.compute_metrics(BaseResult({}), k=10),
            pd.DataFrame(
                [],
                index=pd.MultiIndex.from_product([[], []]),
                columns=[]
            )
        )
        field2 = NumericalField('numerical_field', percentiles=[25, 50, 75], ignore_none=False)
        pd.testing.assert_frame_equal(
            field2.compute_metrics(BaseResult(MOCK_RESULTS), k=10).sort_index(axis=1),
            pd.DataFrame(
                [(i['25-percentile'], i['50-percentile'], i['75-percentile'], i['total'], i['mean'])
                 for results in NUMERICAL_RESULTS_2.values() for i in results.values()],
                index=index,
                columns=['25-percentile', '50-percentile', '75-percentile', 'total', 'mean']
            ).sort_index(axis=1)
        )
