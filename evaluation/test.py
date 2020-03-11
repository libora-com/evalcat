import collections
import unittest

import pandas as pd

from result_list import ResultList
from field import Field


# Mock functions for testing ResultList.

# Defines a result in our collection.
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


class MockField(Field):
    def __init__(self):
        super().__init__('mock')

    def at_k(self, res, k=10):
        return {
            system: {
                query: {
                    metric.__name__: metric(results[:k]) for metric in [metric_sum, metric_product]
                } for query, results in query_res.items()
            } for system, query_res in res.items()
        }


class TestResultList(unittest.TestCase):
    def setUp(self):
        self.result_list = ResultList(MOCK_RESULTS)
        self.mock_field = MockField()

    def test_get_query_metric_matrix(self):
        for system in ['system A', 'system B']:
            test_result = pd.DataFrame({
               metric: [
                   val[metric] for val in TEST_RESULTS[system].values()
               ] for metric in ['metric_sum', 'metric_product']
            }, index=TEST_RESULTS[system].keys())

            print(test_result)

            result_df = self.result_list.get_query_metric_matrix(self.mock_field, system)
            pd.testing.assert_frame_equal(result_df, test_result)

    def test_get_system_metric_matrix(self):
        for query in ['query 1', 'query 2', 'query 3']:
            test_result = pd.DataFrame({
                metric: [
                    val[query][metric] for val in TEST_RESULTS.values()
                ] for metric in ['metric_sum', 'metric_product']
            }, index=TEST_RESULTS.keys())

            print(test_result)

            result_df = self.result_list.get_system_metric_matrix(self.mock_field, query)
            pd.testing.assert_frame_equal(result_df, test_result)

    def test_get_system_query_matrix(self):
        for metric in ['metric_sum', 'metric_product']:
            test_result = pd.DataFrame({
                query: [
                    val[query][metric] for val in TEST_RESULTS.values()
                ] for query in ['query 1', 'query 2', 'query 3']
            }, index=TEST_RESULTS.keys())

            print(test_result)

            result_df = self.result_list.get_system_query_matrix(self.mock_field, metric)
            pd.testing.assert_frame_equal(result_df, test_result)


if __name__ == '__main__':
    unittest.main()
