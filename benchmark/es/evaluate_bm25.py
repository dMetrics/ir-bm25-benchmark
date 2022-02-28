from typing import List

import typer
from beir.datasets.data_loader import GenericDataLoader
from beir.retrieval.search.lexical.bm25_search import BM25Search as BM25

from benchmark.utils.eval import evaluate_all


def evaluate(data_path: str,
             split: str,
             index_name: str,
             initialize: bool = True,
             num_shards="default",
             host_name: str = "http://0.0.0.0:9200",
             k_values: List[int] = [1, 2, 5, 10], ):
    corpus, queries, qrels = GenericDataLoader(data_path).load(split=split)
    model = BM25(index_name=index_name, hostname=host_name, initialize=initialize, number_of_shards=num_shards)

    #### Retrieve dense results (format of results is identical to qrels)
    results = model.search(corpus, queries, max(k_values), sleep_for=10)

    #### Evaluate your retrieval using NDCG@k, MAP@K ...
    evaluate_all(qrels, results, k_values)


if __name__ == "__main__":
    typer.run(evaluate)
