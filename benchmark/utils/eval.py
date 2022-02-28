from typing import Dict, Tuple, List

import pandas as pd
import pytrec_eval
from beir.retrieval.custom_metrics import mrr, recall_cap, hole, top_k_accuracy
from wasabi import msg


def get_metric_evaluation_row(metric_evaluation, metric_name, k_values):
    row = {"metric": metric_name}
    for k in k_values:
        row["k={}".format(k)] = metric_evaluation["{}@{}".format(row["metric"], k)]

    return row


def evaluate_standard(qrels: Dict[str, Dict[str, int]],
                      results: Dict[str, Dict[str, float]],
                      k_values: List[int]) -> Tuple[
    Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float]]:
    ndcg = {}
    _map = {}
    recall = {}
    precision = {}

    for k in k_values:
        ndcg[f"NDCG@{k}"] = 0.0
        _map[f"MAP@{k}"] = 0.0
        recall[f"Recall@{k}"] = 0.0
        precision[f"P@{k}"] = 0.0

    map_string = "map_cut." + ",".join([str(k) for k in k_values])
    ndcg_string = "ndcg_cut." + ",".join([str(k) for k in k_values])
    recall_string = "recall." + ",".join([str(k) for k in k_values])
    precision_string = "P." + ",".join([str(k) for k in k_values])
    evaluator = pytrec_eval.RelevanceEvaluator(qrels, {map_string, ndcg_string, recall_string, precision_string})
    scores = evaluator.evaluate(results)

    for query_id in scores.keys():
        for k in k_values:
            ndcg[f"NDCG@{k}"] += scores[query_id]["ndcg_cut_" + str(k)]
            _map[f"MAP@{k}"] += scores[query_id]["map_cut_" + str(k)]
            recall[f"Recall@{k}"] += scores[query_id]["recall_" + str(k)]
            precision[f"P@{k}"] += scores[query_id]["P_" + str(k)]

    for k in k_values:
        ndcg[f"NDCG@{k}"] = round(ndcg[f"NDCG@{k}"] / len(scores), 5)
        _map[f"MAP@{k}"] = round(_map[f"MAP@{k}"] / len(scores), 5)
        recall[f"Recall@{k}"] = round(recall[f"Recall@{k}"] / len(scores), 5)
        precision[f"P@{k}"] = round(precision[f"P@{k}"] / len(scores), 5)

    return ndcg, _map, recall, precision


def evaluate_custom(qrels: Dict[str, Dict[str, int]],
                    results: Dict[str, Dict[str, float]],
                    k_values: List[int], metric: str) -> Tuple[Dict[str, float]]:
    if metric.lower() in ["mrr", "mrr@k", "mrr_cut"]:
        return mrr(qrels, results, k_values)

    elif metric.lower() in ["recall_cap", "r_cap", "r_cap@k"]:
        return recall_cap(qrels, results, k_values)

    elif metric.lower() in ["hole", "hole@k"]:
        return hole(qrels, results, k_values)

    elif metric.lower() in ["acc", "top_k_acc", "accuracy", "accuracy@k", "top_k_accuracy"]:
        return top_k_accuracy(qrels, results, k_values)


def evaluate_all(qrels: Dict[str, Dict[str, int]],
                 results: Dict[str, Dict[str, float]],
                 k_values: List[int],
                 metrics: List[str] = ["mrr", "recall_cap", "hole", "accuracy"]) -> Tuple[Dict[str, float]]:
    ndcg, _map, recall, precision = evaluate_standard(qrels, results, k_values)
    metric_evaluations = list()
    metric_evaluations.append(get_metric_evaluation_row(ndcg, "NDCG", k_values))
    metric_evaluations.append(get_metric_evaluation_row(_map, "MAP", k_values))
    metric_evaluations.append(get_metric_evaluation_row(recall, "Recall", k_values))
    metric_evaluations.append(get_metric_evaluation_row(precision, "P", k_values))

    # TEMP WORKAROUND FOR https://github.com/UKPLab/beir/issues/70
    query_ids = set([query_id for query_id in qrels])
    result_query_ids = [query_id for query_id, doc_scores in results.items()]
    for query_id in query_ids:
        if query_id not in result_query_ids:
            results[query_id] = {}

    for metric in metrics:
        msg.info()
        metric_result = evaluate_custom(qrels, results, k_values, metric=metric)
        metric_name = None
        for k in metric_result.keys():
            metric_name = k.split("@")[0]
            break

        metric_evaluations.append(get_metric_evaluation_row(metric_result, metric_name, k_values))

    metrics_df = pd.DataFrame(data=metric_evaluations)
    print(metrics_df.to_markdown())
