import json
import time
from functools import partial
from itertools import islice

import typer
from manticoresearch.rest import ApiException
from vespa.io import VespaResponse
from vespa.package import (
    ApplicationPackage,
    Field,
    Schema,
    Document,
    RankProfile,
    FieldSet,
    Function,
)
from wasabi import msg


def take(n, iterable):
    return list(islice(iterable, n))


def callback(response: VespaResponse, id):
    if response.status_code != 200:
        #print(f"Response for id {id}: {response.status_code}")
        error_message = response.json.get('Exception', 'Unknown Error')  # Safely get the error message
        raise Exception(
            f"Error for ID {id}: Status code {response.status_code}, Exception: {error_message}")
    print(response.json)


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
            insert_batch_size: int = 10000,
            host: str = "http://127.0.0.1:9308"):
    if not index_exists:
        package = ApplicationPackage(
            name=index_name,
            schema=[
                Schema(
                    name=index_name,
                    document=Document(
                        fields=[
                            Field(name="doc_id", type="string", indexing=["index", "summary"]),
                            Field(
                                name="title",
                                type="string",
                                indexing=["index", "summary"],
                                index="enable-bm25",
                            ),
                            Field(
                                name="content",
                                type="string",
                                indexing=["index", "summary"],
                                index="enable-bm25",
                                bolding=True,
                            ),
                            Field(name="url", type="string", indexing=["summary"]),
                        ]
                    ),
                    fieldsets=[FieldSet(name="default", fields=["title", "content"])],
                    rank_profiles=[
                        RankProfile(
                            name="bm25",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                Function(name="bm25sum", expression="bm25(title) + bm25(content)")
                            ],
                            first_phase="bm25sum",
                        )
                    ],
                )
            ]
        )

        from vespa.deployment import VespaDocker

        vespa_docker = VespaDocker()
        app = vespa_docker.deploy(application_package=package)

    batches = iter(partial(take, insert_batch_size, iter(read_data(data_file))), [])
    start_time = time.time()
    for batch_index, docs in enumerate(batches):
        try:
            prepped_docs = []
            for doc in docs:
                document = {
                    "doc_id": doc["_id"],
                    "title": doc["title"],
                    "content": doc["text"],
                    "url": doc["metadata"]["url"]
                }
                prepped_docs.append({"id": doc["_id"], "fields": document})

            app.feed_iterable(prepped_docs, schema=index_name, callback=callback)

            msg.info("Batch {} with {} docs! ".format(batch_index, len(prepped_docs)))
        except ApiException as e:
            msg.fail("Exception when calling IndexApi->insert: %s\n" % e)

    msg.info("Documents inserted in {}s".format(time.time() - start_time))


if __name__ == "__main__":
    typer.run(prepare)
