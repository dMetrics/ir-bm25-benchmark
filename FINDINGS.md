Results of evaluations:
---

We are looking to compare all the different strategies we used for indexing and search using the metric `NDCG@10`.
This is metric reported by the BEIR paper and can be accessed [here](https://docs.google.com/spreadsheets/d/1L8aACyPaXrL8iEelJLGqlMqXKPX2oSP_R10pZoy77Ns/edit?usp=sharing) for these two datasets and others.
Other metrics printed below are simply for sanity checks.

Comments:
1. Comparing to the results for `NDCG@10` reported by BEIR against ES:
   1. These numbers should match exactly, but they are actually better in reality. 
   2. The reported benchmark had a bug concerning reproducibility. More details [here](https://github.com/UKPLab/beir/issues/58).
2. Comparing to the results for `NDCG@10` achieved with ES:
   1. Perform very poorly for the trec-covid dataset - `0.29494` compared to the `0.68803` for ES.
   2. Perform slightly poor for the nfcorpus dataset - `0.28791` compared to the `0.34281` for ES.
3. Comparing to the results for `NDCG@10` achieved with MS using ES-like settings:
   1. For the trec-covid dataset: `NDCG@10` jumps to `0.59764`, but we still fall short of the best of `0.68803` reported with ES.
   2. For the nfcorpus dataset: `NDCG@10` jumps to `0.31715`, but we still fall short of the best of `0.34281` reported with ES.

Results for trec-covid`:

|    dataset | settings              | NDCG@10 |
|-----------:|:----------------------|--------:|
| trec-covid | MS (default)          | 0.29494 |
| trec-covid | MS (es-like)          | 0.59764 |
| trec-covid | ES                    | 0.68803 |
| trec-covid | ES (reported in BEIR) |   0.616 |

Results for nfcorpus

|    dataset | settings              | NDCG@10 |
|-----------:|:----------------------|--------:|
|   nfcorpus | MS (default)          | 0.28791 |
|   nfcorpus | MS (es-like)          | 0.31715 |
|   nfcorpus | ES                    | 0.34281 |
|   nfcorpus | ES (reported in BEIR) |   0.297 |


Results with all metrics:

1. For MS:

a. Default settings:

```shell
python -m benchmark.manticore.evaluate data/trec-covid test trec_covid
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.29    | 0.28226 | 0.29505 | 0.29494 |
|  1 | MAP      | 0.00083 | 0.00143 | 0.00275 | 0.00478 |
|  2 | Recall   | 0.00083 | 0.00164 | 0.00394 | 0.00773 |
|  3 | P        | 0.36    | 0.34    | 0.36    | 0.352   |
|  4 | MRR      | 0.36    | 0.44    | 0.51    | 0.51872 |
|  5 | R_cap    | 0.36    | 0.34    | 0.36    | 0.352   |
|  6 | Hole     | 0.04    | 0.05    | 0.072   | 0.114   |
|  7 | Accuracy | 0.36    | 0.52    | 0.78    | 0.86    |


```shell
python -m benchmark.manticore.evaluate data/nfcorpus test nfcorpus
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.41176 | 0.36619 | 0.31409 | 0.28791 |
|  1 | MAP      | 0.05493 | 0.07349 | 0.0934  | 0.10805 |
|  2 | Recall   | 0.05493 | 0.07689 | 0.10895 | 0.14141 |
|  3 | P        | 0.42105 | 0.34985 | 0.25759 | 0.20402 |
|  4 | MRR      | 0.42724 | 0.4613  | 0.49138 | 0.49786 |
|  5 | R_cap    | 0.42724 | 0.36223 | 0.29551 | 0.26369 |
|  6 | Hole     | 0.05573 | 0.06502 | 0.07988 | 0.09226 |
|  7 | Accuracy | 0.42724 | 0.49536 | 0.60681 | 0.65635 |


b. ES-like settings:

```shell
python -m benchmark.manticore.evaluate data/trec-covid test trec_covid_es_like
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.72    | 0.69292 | 0.64028 | 0.59764 |
|  1 | MAP      | 0.00206 | 0.00401 | 0.00837 | 0.01405 |
|  2 | Recall   | 0.00206 | 0.00425 | 0.00916 | 0.01664 |
|  3 | P        | 0.78    | 0.78    | 0.7     | 0.652   |
|  4 | MRR      | 0.78    | 0.86    | 0.86667 | 0.87333 |
|  5 | R_cap    | 0.78    | 0.78    | 0.7     | 0.652   |
|  6 | Hole     | 0.02    | 0.01    | 0.04    | 0.048   |
|  7 | Accuracy | 0.78    | 0.94    | 0.96    | 1       |


```shell
python -m benchmark.manticore.evaluate data/nfcorpus test nfcorpus_es_like
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.4257  | 0.39989 | 0.35145 | 0.31715 |
|  1 | MAP      | 0.05581 | 0.07796 | 0.10248 | 0.11704 |
|  2 | Recall   | 0.05581 | 0.0823  | 0.12377 | 0.14913 |
|  3 | P        | 0.43963 | 0.39474 | 0.29969 | 0.22941 |
|  4 | MRR      | 0.44582 | 0.4969  | 0.52183 | 0.5269  |
|  5 | R_cap    | 0.44582 | 0.40402 | 0.3371  | 0.29062 |
|  6 | Hole     | 0.06811 | 0.06502 | 0.07616 | 0.08421 |
|  7 | Accuracy | 0.44582 | 0.54799 | 0.63777 | 0.67802 |


3. For ES:

```shell
python -m benchmark.es.evaluate_bm25 data/trec-covid test trec_covid
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.82    | 0.79679 | 0.72491 | 0.68803 |
|  1 | MAP      | 0.00234 | 0.0044  | 0.00961 | 0.01698 |
|  2 | Recall   | 0.00234 | 0.00443 | 0.01027 | 0.01907 |
|  3 | P        | 0.88    | 0.84    | 0.768   | 0.734   |
|  4 | MRR      | 0.88    | 0.9     | 0.92167 | 0.92167 |
|  5 | R_cap    | 0.88    | 0.83    | 0.768   | 0.734   |
|  6 | Hole     | 0.02    | 0.03    | 0.052   | 0.054   |
|  7 | Accuracy | 0.88    | 0.92    | 1       | 1       |

```shell
python -m benchmark.es.evaluate_bm25 data/nfcorpus test nfcorpus
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.44968 | 0.4197  | 0.37705 | 0.34281 |
|  1 | MAP      | 0.05936 | 0.08833 | 0.11329 | 0.12969 |
|  2 | Recall   | 0.05936 | 0.09328 | 0.13313 | 0.16603 |
|  3 | P        | 0.46753 | 0.41396 | 0.32273 | 0.24708 |
|  4 | MRR      | 0.44892 | 0.49536 | 0.52023 | 0.52954 |
|  5 | R_cap    | 0.44892 | 0.40712 | 0.34711 | 0.30188 |
|  6 | Hole     | 0.06192 | 0.07276 | 0.07802 | 0.08359 |
|  7 | Accuracy | 0.44892 | 0.5418  | 0.62848 | 0.70279 |

