This repo has scripts and steps for evaluation of Manticore Search (MS) over example datasets for Information Retrieval (IR).

We try to evaluate how MS compares with Elasticsearch (ES) and how both compare for retrieval using BM25.

We try to mimic ES settings for BM25 search as described [here](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables).

The evaluation is done comparing various IR benchmarking metrics, implemented in [BEIR](https://github.com/UKPLab/beir).
BEIR is a python package for benchmarking models/algorithms for IR tasks.

Setup for data:
---
We evaluate on the datasets below.

1. TREC-COVID https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/trec-covid.zip
2. NF-CORPUS https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nfcorpus.zip

Run the below commands in the directory you clone the repo:
```shell
cd data
wget https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/trec-covid.zip
wget https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nfcorpus.zip
tar -xvzf nfcorpus.zip
tar -xvzf trec-covid.zip
cd ..
```

NOTES: 

Meta information about the datasets:
1. Each dataset has two fields with contents that needs be indexed, a `title` and `txt` field.
2. The trec-covid dataset has `171332` documents while nfcorpus has `3633` documents.
3. For IR evaluation, each dataset has a fixed set of queries and corresponding relevant documents. 
4. The trec-covid dataset has `50` queries while nfcorpus has `323` queries. 

Setup for code:
---

1. Create and activate conda env:
```shell
conda create --name ir-bm25-benchmark python=3.10
conda activate ir-bm25-benchmark
```

2. Install dependencies:
```shell
pip install -r requirements.txt
pip install --no-deps -r requirements_no_deps.txt
```

Evaluating Manticore Search:
---

1. For Pull docker image and start container 
```shell
docker pull manticoresearch/manticore
docker run -p 9306:9306 -p 9308:9308 manticoresearch/manticore
```

2. Create and populate indices:

a. Create indices with default settings:
```shell
python -m benchmark.manticore.prepare data/trec-covid/corpus.jsonl trec_covid
python -m benchmark.manticore.prepare data/nfcorpus/corpus.jsonl nfcorpus
```

b. Create indices with settings to mimic ES-like BM25 behavior for search:
```shell
python -m benchmark.manticore.prepare data/trec-covid/corpus.jsonl trec_covid_es_like --index-es-like
python -m benchmark.manticore.prepare data/nfcorpus/corpus.jsonl nfcorpus_es_like --index-es-like
```

**NOTE 1:** 

The following options are set on the indices for the ES-like BM25 behaviour:
```shell
stopwords='en'
stopwords_unstemmed='1'
morphology='stem_en'
html_strip = '1'
index_exact_words = '1'
index_field_lengths = '1'
```

**NOTE 2:**
The following MS ranking options are set for the evaluation of the ES-like BM25 behaviour:
```shell
ranker=expr('sum(10000 * bm25f(1.2,0.75,{{title=1,content=1}}))'), idf='plain,tfidf_unnormalized'
```

**NOTE 3:** 

Manticore's default english stops words is much longer than that for ElasticSearch.
For the `*es_like` indices you can set use the same stops words as ElasticSearch. 
But we've noticed that our evaluation performance is poor when we limit to ES only stop words.
For this, copy the file in `data/elasticsearch_en_stop_words` to your manticore docker container, say at location 
`/var/lib/manticore/data/`. 
You can then change your index preparation script to this:
```shell
python -m benchmark.manticore.prepare data/trec-covid/corpus.jsonl trec_covid_es_like --index-es-like --stop-words /var/lib/manticore/data/elasticsearch_en_stop_words
python -m benchmark.manticore.prepare data/nfcorpus/corpus.jsonl nfcorpus_es_like --index-es-like --stop-words /var/lib/manticore/data/elasticsearch_en_stop_words
```

Evaluate:

a. Evaluate retrieval for MS default settings:
```shell
python -m benchmark.manticore.evaluate data/nfcorpus test nfcorpus
python -m benchmark.manticore.evaluate data/trec-covid test trec_covid
```

b. Evaluate retrieval for MS with ES-like settings:
```shell
python -m benchmark.manticore.evaluate data/nfcorpus test nfcorpus_es_like
python -m benchmark.manticore.evaluate data/trec-covid test trec_covid_es_like
```

Evaluating Elasticsearch:
---

1. Run ElasticSearch in a docker container:
```shell
docker pull elasticsearch:7.17.0
docker-compose up
```

Wait for a couple of minutes for the docker container to be ready.

2. Evaluate: (This re-creates an index each time you evaluate)
```shell
python -m benchmark.es.evaluate_bm25 data/trec-covid test trec_covid
python -m benchmark.es.evaluate_bm25 data/nfcorpus test nfcorpus
```

Note: There is a sleep of 10 seconds between the creation of the index and the evaluation in the above script. 
This allows ES to finish the indexing before we run the evaluations.

Findings:
---

We are looking to compare all the different strategies we used for indexing and search using the metric `NDCG@10`.
This is metric reported by the BEIR paper and can be accessed [here](https://docs.google.com/spreadsheets/d/1L8aACyPaXrL8iEelJLGqlMqXKPX2oSP_R10pZoy77Ns/edit?usp=sharing) for these two datasets and others.
Other metrics printed below are simply for sanity checks.

Comments:
1. Comparing to the results for `NDCG@10` reported by BEIR against ES:
   1. These numbers should match exactly, but they are actually better in reality. 
   2. The reported benchmark had a bug concerning reproducibility. More details [here](https://github.com/UKPLab/beir/issues/58).
2. Comparing to the results for `NDCG@10` achieved with ES:
   1. MS performs very poorly for the trec-covid dataset - `0.29494` compared to the `0.68803` for ES.
   2. MS performs slightly poor for the nfcorpus dataset - `0.28791` compared to the `0.34281` for ES.
3. Comparing to the results for `NDCG@10` achieved with MS using ES-like settings:
   1. For the trec-covid dataset: `NDCG@10` jumps to `0.59764`, but we still fall short of the best of `0.68803` reported with ES.
   2. For the nfcorpus dataset: `NDCG@10` jumps to `0.31715`, but we still fall short of the best of `0.34281` reported with ES.

Results for trec-covid:

|    dataset | settings              | NDCG@10 |
|-----------:|:----------------------|--------:|
| trec-covid | MS (default)          | 0.29494 |
| trec-covid | MS (es-like)          | 0.59764 |
| trec-covid | ES                    | 0.68803 |
| trec-covid | ES (reported in BEIR) |   0.616 |

Results for nfcorpus:

|    dataset | settings              | NDCG@10 |
|-----------:|:----------------------|--------:|
|   nfcorpus | MS (default)          | 0.28791 |
|   nfcorpus | MS (es-like)          | 0.31715 |
|   nfcorpus | ES                    | 0.34281 |
|   nfcorpus | ES (reported in BEIR) |   0.297 |

All Results:
---
Look at all the results [here](./RESULTS.md).


Questions:
---
1. What options are we missing on our **MS index** for us to get competitive results - similar to ES?
2. What options are we missing on our **MS ranking options** for us to get competitive results - similar to ES?
3. We've observed the best results for MS with the default `en` stop words although that list is much larger than the list for English stop words in ES. How can we explain this behavior?


Versions:
---
Elasticsearch version: 7.17.0
Run using [this](https://hub.docker.com/layers/elasticsearch/library/elasticsearch/7.17.0/images/sha256-fa7141154a7e14df214e42f08c333702403eb88c02ba44e79322a1f42d733013?context=explore) docker image.

Manticore Search version: Manticore 4.2.0 15e927b28@211223 release
Run using [this](https://hub.docker.com/layers/manticoresearch/manticore/4.2.0/images/sha256-b49a09d569838908bd9759d99eaf2807a2f851aadfeff422cf754addbb4bc3ac?context=explore) docker image.
