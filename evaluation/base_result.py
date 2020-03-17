class BaseResult:
    def __init__(self, result, queries=None):
        self.result = result
        self.systems = list(result.keys())
        self.queries = _check_queries(result, queries)


def _check_queries(result, queries=None):
    if not queries:
        queries = list(next(iter(result.values())).keys())

    if not all(set(queries) == set(query_res.keys()) for query_res in result.values()):
        raise ValueError('Not all query sets match the input queries.')
    return queries
