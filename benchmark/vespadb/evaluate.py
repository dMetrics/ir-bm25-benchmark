from typing import List
import json
import manticoresearch
import typer
from beir.datasets.data_loader import GenericDataLoader
from manticoresearch.rest import ApiException
from tqdm import tqdm
from vespa.application import Vespa
from wasabi import msg

from benchmark.utils.eval import evaluate_all


def evaluate(data_path: str,
             split: str,
             index_name: str,
             k_values: List[int] = [1, 2, 5, 10],
             host: str = "http://127.0.0.1",
             port: int = 8080):
    corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split=split)


    max_k = max(k_values)
    results = dict()
    # Enter a context with an instance of the API client
    for query_id, query in tqdm(queries.items()):
        vespa = Vespa(url=host, port=port)
        query = {
            'yql': 'select * from sources * where userQuery()',
            'query': query.replace('\'', ''),
            'ranking': 'bm25',
            'hits': max_k
        }
        res = vespa.query(body=query)
        try:
            results[query_id] = {
                doc['fields']['doc_id']: doc["relevance"] for doc in res.hits
            }
            # Filter out queries with empty results as Elastic does
            results = {k: v for k, v in results.items() if v}
        except ApiException as e:
            msg.fail("Exception when calling SearchApi->search: %s\n" % e)

    evaluate_all(qrels, results, k_values)


if __name__ == "__main__":
    typer.run(evaluate)
