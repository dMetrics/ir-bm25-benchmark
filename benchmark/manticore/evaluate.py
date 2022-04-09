from typing import List
import json
import manticoresearch
import typer
from beir.datasets.data_loader import GenericDataLoader
from manticoresearch.rest import ApiException
from tqdm import tqdm
from wasabi import msg

from benchmark.utils.eval import evaluate_all


def evaluate(data_path: str,
             split: str,
             index_name: str,
             k_values: List[int] = [1, 2, 5, 10],
             host: str = "http://127.0.0.1:9308"):
    corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split=split)

    # Defining the host is optional and defaults to http://127.0.0.1:9308
    # See configuration.py for a list of all supported configuration parameters.
    configuration = manticoresearch.Configuration(
        host=host
    )

    max_k = max(k_values)
    results = dict()
    # Enter a context with an instance of the API client
    for query_id, query in tqdm(queries.items()):
        with manticoresearch.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = manticoresearch.UtilsApi(api_client)
            # rankers: 'bm25'; 'proximity_bm25'; 'sph04'; ranker=expr('sum(atc*1000)'), idf='plain,tfidf_unnormalized'
            # ranker=expr('1000 * bm25a(1.2,0.75)')
            # ranker=expr('1000 * bm25f(1.2,0.75,{{title=1,content=1}})')
            body = "SELECT *, WEIGHT(), PACKEDFACTORS({}) FROM {} WHERE MATCH('@(title,content){}') OPTION ranker=expr('10000 * bm25f(1.2,0.75,{{title=1,content=1}})'), idf='plain,tfidf_unnormalized', max_matches={}" \
                .format("{json=1}",
                        index_name,
                        '"{}"/1'.format(query.replace('\'', '')),
                        max_k)
            # Set raw_response=False to provide a compatibility the with Manticore dev version
            raw_response = False
            try:
                # Performs a search
                # msg.fail(query)
                import re
                body_request = re.sub(r'[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]', u'', body)
                # body_request = re.sub(r'\'', r'', body)
                # body_request = body.encode("utf-8").__str__()[2:-1]
                api_response = api_instance.sql(body_request, raw_response=raw_response)
                results[query_id] = {
                    doc["_source"]["_id"]: doc["_source"]["weight()"] for doc in api_response[0]['hits']['hits']
                }
                # Filter out queries with empty results as Elastic does
                results = {k:v for k,v in results.items() if v}
            except ApiException as e:
                msg.fail("Exception when calling SearchApi->search: %s\n" % e)

    evaluate_all(qrels, results, k_values)


if __name__ == "__main__":
    typer.run(evaluate)
