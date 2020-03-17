import collections
import unittest

import pandas as pd

from ..result_list import ResultList
from ..field import Field


"""Mock functions for testing ResultList."""

# Defines a document (search result item) in our collection.
Result = collections.namedtuple('Result', ['value'])


# Defines a mock metric 1: the sum of values from a list of results.
def metric_sum(results):
    return sum(res.value for res in results)


# Defines a mock metric 2: the product of values from a list of results.
def metric_product(results):
    prod = 1
    for res in results:
        prod *= res.value
    return prod


# Input for ResultList is in this format.
MOCK_RESULTS = {
    'system A': {
        'query 1': [Result(5), Result(2), Result(1)],
        'query 2': [Result(1), Result(3)],
        'query 3': [Result(5), Result(2)],
    }, 'system B': {
        'query 1': [Result(8), Result(3)],
        'query 2': [Result(4), Result(1)],
        'query 3': [Result(4), Result(1), Result(3)],
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


# Mock Field class using the metrics `metric_sum` and `metric_product`.
class MockField(Field):
    def __init__(self):
        super().__init__('mock')

    def at_k(self, res, k=10):
        return {metric.__name__: metric(res[:k]) for metric in [metric_sum, metric_product]}


"""Test Classes"""


class TestResultList(unittest.TestCase):
    def setUp(self):
        self.result_list = ResultList(MOCK_RESULTS, [MockField()])

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
        with self.assertRaises(KeyError):
            self.result_list.get_query_metric_df(field_name='wrong_field', system='system A')
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
            with self.assertRaises(KeyError):
                self.result_list.get_system_metric_df(field_name='wrong_field', query='query 1')
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
            with self.assertRaises(KeyError):
                self.result_list.get_system_query_df(field_name='wrong_field', metric='metric_sum')
                self.result_list.get_system_query_df(field_name='mock', metric='wrong_metric')


if __name__ == '__main__':
    unittest.main()
