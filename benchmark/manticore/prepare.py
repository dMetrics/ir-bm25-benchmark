import json
import sys
import time
from functools import partial
from itertools import islice

import manticoresearch
import typer
from manticoresearch.rest import ApiException
from wasabi import msg


def take(n, iterable):
    return list(islice(iterable, n))


def read_data(data_file: str):
    with open(data_file) as corpus_file:
        corpus = corpus_file.readlines()
        for example in corpus:
            data = json.loads(example)
            yield data


def prepare(data_file: str,
            index_name: str,
            stop_words: str = 'en',
            index_es_like: bool = False,
            index_exists: bool = False,
            insert_batch_size: int = 1000,
            host: str = "http://127.0.0.1:9308"):
    configuration = manticoresearch.Configuration(host=host)
    with manticoresearch.ApiClient(configuration) as api_client:
        if not index_exists:
            # Create an instance of the API class
            api_instance = manticoresearch.UtilsApi(api_client)
            if index_es_like:
                body = "CREATE TABLE {}(_id string, title text, content text, url string) " \
                       "stopwords='{}' " \
                       "stopwords_unstemmed='1' " \
                       "morphology='stem_en' " \
                       "html_strip = '1' " \
                       "index_exact_words = '1' " \
                       "index_field_lengths = '1'" \
                    .format(index_name, stop_words)
            else:
                body = "CREATE TABLE {}(_id string, title text, content text, url string) ".format(index_name)
            raw_response = True

            try:
                # Perform SQL requests
                api_response = api_instance.sql(body, raw_response=raw_response)
                msg.info(api_response)
            except ApiException as e:
                msg.fail("Exception when calling UtilsApi->sql: %s\n" % e)
                sys.exit(1)

        # Create an instance of the API class
        api_instance = manticoresearch.IndexApi(api_client)
        batches = iter(partial(take, insert_batch_size, iter(read_data(data_file))), [])
        start_time = time.time()
        for batch_index, docs in enumerate(batches):
            try:
                prepped_docs = [{
                    "insert": {
                        "index": index_name,
                        "id": doc["_id"],
                        "doc": {
                            "_id": doc["_id"],
                            "title": doc["title"],
                            "content": doc["text"],
                            "url": doc["metadata"]["url"]
                        }
                    }
                } for doc in docs]
                msg.info("Batch {} with {} docs! ".format(batch_index, len(prepped_docs)))
                api_response = api_instance.bulk('\n'.join(map(json.dumps, prepped_docs)))
                # msg.info(api_response)
            except ApiException as e:
                msg.fail("Exception when calling IndexApi->insert: %s\n" % e)

        # Optimize index to prevent possible IDF miscalculation
        api_instance = manticoresearch.UtilsApi(api_client)
        body = "FLUSH RAMCHUNK {}".format(index_name)
        api_instance.sql(body, raw_response=raw_response)
        # Give time to Manticore for flush completing
        time.sleep(5)
        body = "OPTIMIZE INDEX {} OPTION cutoff=1, sync=1".format(index_name)
        api_instance.sql(body, raw_response=raw_response)

        msg.info("Documents inserted in {}s".format(time.time() - start_time))


if __name__ == "__main__":
    typer.run(prepare)
