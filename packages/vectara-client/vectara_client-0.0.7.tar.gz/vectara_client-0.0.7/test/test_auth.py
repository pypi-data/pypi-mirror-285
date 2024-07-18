from unittest import TestCase
from vectara_client.core import Factory, Client
from vectara_client.models import QueryCorpusRequest, GenerationParameters


class RenderMarkdownTest(TestCase):

    def test_new_client_init(self):
        client = Factory().build()

        queries_api = client.queries_api

        request = QueryCorpusRequest(
            query='Which API should I use to ingest my data into Vectara?',
            search=None,
            generation=GenerationParameters(enable_factual_consistency_score=False)
        )

        response = queries_api.query_corpus(corpus_key="vectara-docs_314", query_corpus_request=request)
        print(response.summary)
