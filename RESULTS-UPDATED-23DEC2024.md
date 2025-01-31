Below are results with:

Manticore 6.3.8 release

Results with all metrics:

1. For MS:

a. Default settings:

```shell
python -m benchmark.manticore.evaluate data/trec-covid test trec_covid
```

|    | metric   |   k=1 |   k=2 |     k=5 |    k=10 |
|---:|:---------|------:|------:|--------:|--------:|
|  0 | NDCG     |  0    |  0    | 0.00146 | 0.00095 |
|  1 | MAP      |  0    |  0    | 1e-05   | 1e-05   |
|  2 | Recall   |  0    |  0    | 2e-05   | 2e-05   |
|  3 | P        |  0    |  0    | 0.004   | 0.002   |
|  4 | MRR      |  0    |  0    | 0       | 0.002   |
|  5 | R_cap    |  0    |  0    | 0       | 0.002   |
|  6 | Hole     |  0.96 |  0.56 | 0.652   | 0.8     |
|  7 | Accuracy |  0    |  0    | 0       | 0.02    |


```shell
python -m benchmark.manticore.evaluate data/nfcorpus test nfcorpus
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.12752 | 0.12963 | 0.12311 | 0.11403 |
|  1 | MAP      | 0.02175 | 0.03538 | 0.04675 | 0.0517  |
|  2 | Recall   | 0.02175 | 0.0399  | 0.05719 | 0.06486 |
|  3 | P        | 0.12752 | 0.12584 | 0.1047  | 0.08054 |
|  4 | MRR      | 0.10836 | 0.12539 | 0.14123 | 0.14808 |
|  5 | R_cap    | 0.10836 | 0.10836 | 0.09835 | 0.10131 |
|  6 | Hole     | 0.17028 | 0.17957 | 0.1969  | 0.24923 |
|  7 | Accuracy | 0.10836 | 0.14241 | 0.19814 | 0.25077 |



b. ES-like settings (row-6 in sheet engine = columnar):

Schema:

```
CREATE TABLE trec_covid_es_like (
id bigint,
title text,
content text,
_id string attribute,
url string attribute
) index_exact_words='1' html_strip='1' engine='columnar' blend_chars='+,&,-' blend_mode='trim_all,trim_head, trim_tail' morphology='lemmatize_en_all,libstemmer_en' stopwords_unstemmed='1' stopwords='/var/lib/manticore/trec_covid_es_like/en' optimize_cutoff='1'
```

```shell
python -m benchmark.manticore.evaluate data/trec-covid test trec_covid_es_like
```
|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.68    | 0.66066 | 0.6149  | 0.56133 |
|  1 | MAP      | 0.00179 | 0.00333 | 0.00709 | 0.01193 |
|  2 | Recall   | 0.00179 | 0.0036  | 0.00838 | 0.01493 |
|  3 | P        | 0.74    | 0.72    | 0.664   | 0.604   |
|  4 | MRR      | 0.74    | 0.8     | 0.83967 | 0.83967 |
|  5 | R_cap    | 0.74    | 0.71    | 0.664   | 0.602   |
|  6 | Hole     | 0.04    | 0.02    | 0.024   | 0.05    |
|  7 | Accuracy | 0.74    | 0.86    | 1       | 1       |



Schema
```
CREATE TABLE nfcorpus_es_like (
id bigint,
title text,
content text,
_id string attribute,
url string attribute
) index_exact_words='1' html_strip='1' engine='columnar' blend_chars='+,&,-' blend_mode='trim_all,trim_head, trim_tail' morphology='lemmatize_en_all,libstemmer_en' stopwords_unstemmed='1' stopwords='/var/lib/manticore/nfcorpus_es_like/en' optimize_cutoff='1'
```

```shell
python -m benchmark.manticore.evaluate data/nfcorpus test nfcorpus_es_like
```


|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.46405 | 0.41222 | 0.36177 | 0.3246  |
|  1 | MAP      | 0.06067 | 0.08241 | 0.10618 | 0.12042 |
|  2 | Recall   | 0.06067 | 0.08666 | 0.12507 | 0.14913 |
|  3 | P        | 0.47712 | 0.40033 | 0.3085  | 0.23235 |
|  4 | MRR      | 0.45511 | 0.50155 | 0.52503 | 0.53009 |
|  5 | R_cap    | 0.45511 | 0.39319 | 0.33318 | 0.27592 |
|  6 | Hole     | 0.05263 | 0.06966 | 0.0774  | 0.08731 |
|  7 | Accuracy | 0.45511 | 0.54799 | 0.63467 | 0.67183 |



c. ES-like settings (row-7 in sheet using engine = rowwise):

Schema:

```
CREATE TABLE trec_covid_es_like1 (
id bigint,
title text,
content text,
_id string attribute,
url string attribute
) index_exact_words='1' html_strip='1' index_field_lengths='1' morphology='stem_en' stopwords_unstemmed='1' stopwords='en'
```

```shell
python -m benchmark.manticore.evaluate data/trec-covid test trec_covid_es_like1
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.83    | 0.81066 | 0.77408 | 0.71179 |
|  1 | MAP      | 0.00229 | 0.00439 | 0.01026 | 0.01846 |
|  2 | Recall   | 0.00229 | 0.00441 | 0.01101 | 0.02055 |
|  3 | P        | 0.88    | 0.85    | 0.824   | 0.758   |
|  4 | MRR      | 0.86    | 0.88    | 0.90833 | 0.90833 |
|  5 | R_cap    | 0.86    | 0.85    | 0.824   | 0.758   |
|  6 | Hole     | 0       | 0.01    | 0.02    | 0.026   |
|  7 | Accuracy | 0.86    | 0.9     | 1       | 1       |




Schema:

```
CREATE TABLE nfcorpus_es_like1 (
id bigint,
title text,
content text,
_id string attribute,
url string attribute
) index_exact_words='1' html_strip='1' index_field_lengths='1' morphology='stem_en' stopwords_unstemmed='1' stopwords='en'
```


```shell
python -m benchmark.manticore.evaluate data/nfcorpus test nfcorpus_es_like1
```

|    | metric   |     k=1 |     k=2 |     k=5 |    k=10 |
|---:|:---------|--------:|--------:|--------:|--------:|
|  0 | NDCG     | 0.45292 | 0.42067 | 0.38322 | 0.34537 |
|  1 | MAP      | 0.0592  | 0.08632 | 0.11326 | 0.12953 |
|  2 | Recall   | 0.0592  | 0.09091 | 0.13506 | 0.16388 |
|  3 | P        | 0.47078 | 0.41558 | 0.33182 | 0.2513  |
|  4 | MRR      | 0.4582  | 0.4969  | 0.52657 | 0.53319 |
|  5 | R_cap    | 0.4582  | 0.40867 | 0.35516 | 0.30366 |
|  6 | Hole     | 0.06192 | 0.07585 | 0.08111 | 0.08731 |
|  7 | Accuracy | 0.4582  | 0.5356  | 0.64087 | 0.6935  |
