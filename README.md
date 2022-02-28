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
tar -xvzg trec-covid.zip
cd ..
```

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
Look at the findings [here](./FINDINGS.md)


Questions:
---
1. What options are we missing on our MS index for us to get competitive results - similar to ES?
2. We've observed the best results for MS with the default `en` stop words although that list is much larger than the list for English stop words in ES. How can we explain this behavior?
