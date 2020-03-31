import unittest

import pandas as pd

from evaluation.result_list import ResultList
from evaluation.fields.base import Field


"""Mock functions for testing ResultList."""


# Defines a document (search result item) in our collection.
class Result(dict):
    def __init__(self, value):
        super().__init__(value=value)


# Defines a mock metric 1: the sum of values from a list of results.
def metric_sum(results):
    return sum(item['value'] for item in results if item['value'] is not None)


# Defines a mock metric 2: the product of values from a list of results.
def metric_product(results):
    prod = 1
    for item in results:
        if item['value']:
            prod *= item['value']
    return prod


# Mock Field class using the metrics `metric_sum` and `metric_product`.
class MockField(Field):
    def __init__(self):
        super().__init__('mock')

    def at_k(self, res, k=10):
        return {metric.__name__: metric(res[:k]) for metric in [metric_sum, metric_product]}


# Input for ResultList is in this format.
MOCK_RESULTS = {
    'system A': {
        'query 1': [Result(5), Result(2), Result(1)],
        'query 2': [Result(1), Result(3)],
        'query 3': [Result(5), Result(2)],
    }, 'system B': {
        'query 1': [Result(8), Result(3)],
        'query 2': [Result(4), Result(1)],
        'query 3': [Result(4), Result(1), Result(3), Result(None)],
    }
}

# Mock result (Output DataFrame will be made from this).
TEST_RESULTS = {
    'system A': {
        'query 1': {'metric_sum': 8, 'metric_product': 10},
        'query 2': {'metric_sum': 4, 'metric_product': 3},
        'query 3': {'metric_sum': 7, 'metric_product': 10}
    },
    'system B': {
        'query 1': {'metric_sum': 11, 'metric_product': 24},
        'query 2': {'metric_sum': 5, 'metric_product': 4},
        'query 3': {'metric_sum': 8, 'metric_product': 12}
    }
}


"""Test Classes"""


class TestResultList(unittest.TestCase):
    def setUp(self):
        self.result_list = ResultList(MOCK_RESULTS, [MockField()])

    def test_get_field_from_summary(self):
        pd.testing.assert_frame_equal(
            self.result_list.summary['mock'],
            self.result_list._get_field_from_summary('mock')
        )
        with self.assertRaises(ValueError):
            self.result_list._get_field_from_summary('wrong_field')
        with self.assertRaises(TypeError):
            self.result_list._get_field_from_summary(12)

    def test_get_query_metric_matrix(self):
        # Testing good queries.
        for system in ['system A', 'system B']:
            test_result = pd.DataFrame({
               metric: [
                   val[metric] for val in TEST_RESULTS[system].values()
               ] for metric in ['metric_sum', 'metric_product']
            }, index=TEST_RESULTS[system].keys())
            """Example output for system A
            >>> test_result
            |        |metric_sum|metric_product|
            |-------|----------|--------------|
            |query 1|         8|            10|
            |query 2|         4|             3|
            |query 3|         7|            10|
            """

            result_df = self.result_list.get_query_metric_df(field_name='mock', system=system)
            pd.testing.assert_frame_equal(result_df, test_result)

        # Testing bad queries
        with self.assertRaises(ValueError):
            self.result_list.get_query_metric_df(field_name='mock', system='wrong_system')

    def test_get_system_metric_matrix(self):
        for query in ['query 1', 'query 2', 'query 3']:
            test_result = pd.DataFrame({
                metric: [
                    val[query][metric] for val in TEST_RESULTS.values()
                ] for metric in ['metric_sum', 'metric_product']
            }, index=TEST_RESULTS.keys())
            """Example output for query 1
            >>> test_result
            |        |metric_sum|metric_product|
            |--------|----------|--------------|
            |system A|         8|            10|
            |system B|        11|            24|
            """

            result_df = self.result_list.get_system_metric_df(field_name='mock', query=query)
            pd.testing.assert_frame_equal(result_df, test_result)

            # Testing bad queries
            with self.assertRaises(ValueError):
                self.result_list.get_system_metric_df(field_name='mock', query='wrong_query')

    def test_get_system_query_matrix(self):
        for metric in ['metric_sum', 'metric_product']:
            test_result = pd.DataFrame({
                query: [
                    val[query][metric] for val in TEST_RESULTS.values()
                ] for query in ['query 1', 'query 2', 'query 3']
            }, index=TEST_RESULTS.keys())
            """Example output for metric_sum
            >>> test_result
            |        |query 1|query 2|query 3|
            |--------|-------|-------|-------|
            |system A|      8|      4|      7|
            |system B|     11|      5|      8|
            """

            result_df = self.result_list.get_system_query_df(field_name='mock', metric=metric)
            pd.testing.assert_frame_equal(result_df, test_result)

            # Testing bad queries
            with self.assertRaises(ValueError):
                self.result_list.get_system_query_df(field_name='mock', metric='wrong_metric')

    def test_rank_bias_overlap(self):
        # Both systems returns identical result lists.
        reslist1 = ResultList({
            'system A': {
                'query 1': [Result(1), Result(2), Result(3)],
                'query 2': [Result(1), Result(2)]
            },
            'system B': {
                'query 1': [Result(1), Result(2), Result(3)],
                'query 2': [Result(1), Result(2)]
            }
        })
        pd.testing.assert_frame_equal(
            reslist1.rank_biased_overlap(identifier='value'),
            pd.DataFrame([[0.5225283643313484, 0.47747163566865164, 1.0],
                          [0.41168557622089896, 0.588314423779101, 1.0]],
                         index=['query 1', 'query 2'], columns=['rbo_min', 'rbo_res', 'rbo_ext']),
        )
        pd.testing.assert_frame_equal(
            reslist1.rank_biased_overlap(identifier='value', systems=['system A', 'system B']),
            pd.DataFrame([[0.5225283643313484, 0.47747163566865164, 1.0],
                          [0.41168557622089896, 0.588314423779101, 1.0]],
                         index=['query 1', 'query 2'], columns=['rbo_min', 'rbo_res', 'rbo_ext']),
        )
        # Both systems returns different result lists.
        reslist2 = ResultList({
            'system A': {
                'query 1': [Result(1), Result(2), Result(3)],  # Ordered differently.
                'query 2': [Result(1), Result(2), Result(3)],  # Uneven lengths.
                'query 3': [Result(1), Result(2), Result(3)],  # Different results.
                'query 4': [Result(1), Result(2), Result(3)],  # Different results.
                'query 5': [],  # No results
                'query 6': []  # No results
            },
            'system B': {
                'query 1': [Result(3), Result(2), Result(1)],
                'query 2': [Result(1), Result(2)],
                'query 3': [Result(4), Result(5)],
                'query 4': [Result(2), Result(5)],
                'query 5': [],
                'query 6': [Result(1), Result(2)]
            }
        })
        pd.testing.assert_frame_equal(
            reslist2.rank_biased_overlap(identifier='value'),
            pd.DataFrame([[0.3775283643313485, 0.47747163566865164, 0.8550000000000001],
                          [0.41168557622089896, 0.5883144237791011, 1.0],
                          [0.0, 0.7377750000000001, 0.0],
                          [0.15584278811044952, 0.6721572118895507, 0.45],
                          [None, None, None],
                          [None, None, None],
                          ],
                         index=[f'query {i}' for i in range(1, 7)], columns=['rbo_min', 'rbo_res', 'rbo_ext']),
        )
        # Malformed queries
        with self.assertRaises(KeyError):
            reslist2.rank_biased_overlap(identifier='id')
        with self.assertRaises(TypeError):
            reslist2.rank_biased_overlap(identifier='id', systems=3)
        with self.assertRaises(ValueError):
            reslist2.rank_biased_overlap(identifier='id', systems=['system A'])
        with self.assertRaises(ValueError):
            reslist2.rank_biased_overlap(identifier='id', systems=['system A', 'System C'])


if __name__ == '__main__':
    unittest.main()
