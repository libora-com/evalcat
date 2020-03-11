class ResultList:
    def __init__(self, results):
        self.results = results

    def _get_results(self, field, system=None, query=None, metric=None):
        if system and not query and not metric:
            return
        elif query and not system and not metric:
            return
        elif metric and not system and not metric:
            return
        else:
            raise ValueError()

    def get_query_metric_matrix(self, field, system):
        return self._get_results(field, system=system)

    def get_system_metric_matrix(self, field, query):
        return self._get_results(field, query=query)

    def get_system_query_matrix(self, field, metric):
        return self._get_results(field, metric=metric)
