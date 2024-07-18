from vectara_client.util import CountDownLatch
from vectara_client.api import CorporaApi, IndexApi
from vectara_client.models import CreateCorpusRequest, CreateDocumentRequest, Corpus
from typing import List, Union
from threading import Thread
import logging

class SubIndexer:
    """
        Class designed to be used inside a thread to run multiple indexing requests and track completions.
    """

    def __init__(self, index_api: IndexApi, corpus_key: str, latch: CountDownLatch, thread_index: int):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.index_api = index_api
        self.corpus_key = corpus_key
        self.latch = latch
        self.thread_index = thread_index

        self.docs = []
        self.results = []

    def add_doc(self, doc):
        self.docs.append(doc)

    def index_docs(self):
        # TODO Handle success and failure into results array
        self.logger.info(f"Worker [{self.thread_index}] Starting our [{len(self.docs)}] indexer requests")

        for doc in self.docs:
            try:
                result = self.index_api.create_corpus_document(self.corpus_key, doc)

            except Exception as e:
                # Ignore for lab
                self.logger.error("Error: {e}")
        self.logger.info(f"Worker [{self.thread_index}] Finished our indexer requests")
        self.latch.count_down()

class CorpusManager:
    """
    Provides a layer of intelligence over the operations regarding corpus lifecycle.
    """

    corpora_api: CorporaApi

    def __init__(self, corpora_api: CorporaApi, index_api: IndexApi):
        self.logger = logging.getLogger(__class__.__name__)
        self.corpora_api = corpora_api
        self.index_api = index_api

    def find_corpora_by_name(self, name: str) -> List[int]:
        corpora = self.corpora_api.list_corpora(filter=name).corpora

        found: List[int] = []

        if not corpora:
            return found

        for potential in corpora:
            self.logger.info(f"Checking corpus with name [{potential.name}]")
            if potential.name == name:
                found.append(potential.id)

        self.logger.info(f"We found the following corpora with name [{name}]: {found}")
        return found


    def find_corpus_by_name(self, name: str, fail_if_not_exist=True) -> int | None:
        corpora = self.corpora_api.list_corpora(filter=name).corpora

        found = None
        if corpora:
            for potential in corpora:
                self.logger.info(f"Checking corpus with name [{potential.name}]")
                if potential.name == name:
                    if found:
                        raise Exception(f"We found multiple matching corpus with name [{name}]")
                    else:
                        found = potential

        if not found:
            if fail_if_not_exist:
                raise Exception(f"We did not find a corpus matching [{name}]")
            else:
                self.logger.info("No corpus with name [" + name + "] can be found")
                return None
        else:
            corpus_id = found.id

        self.logger.info(f"Our corpus id is [{corpus_id}]")
        return corpus_id

    def delete_corpus_by_name(self, name: str) -> bool:
        self.logger.info(f"Deleting existing corpus named [{name}]")

        # The filter below will match any corpus with "verified-corpus" anywhere in the name, so we need a
        # client side check to validate equivalence.
        existing_corpora = self.corpora_api.list_corpora(filter=name).corpora
        self.logger.info(f"We found [{len(existing_corpora)}] potential matches")
        found = False
        for existing_corpus in existing_corpora:
            if existing_corpus.name == name:
                # The following code will delete the corpus
                self.logger.info(f"Deleting existing corpus with id [{existing_corpus.key}]")
                self.corpora_api.delete_corpus(existing_corpus.key)
                found = True
            else:
                self.logger.info(
                    f"Ignoring corpus with id [{existing_corpus.key}] as it doesn't match our target name exactly")
        return found

    def create_corpus(self, corpus:CreateCorpusRequest, delete_existing=False, unique=True) -> Corpus:
        """
        Creates a new corpus with sensible defaults. Look at CorpusBuilder for a simplified notation
        to create a corpus.

        :param corpus: the new corpus to create.
        :param delete_existing: whether we delete an existing corpus with the same name.
        :param unique: whether we fail if there is an existing corpus of the same name.
        :return: the id of the new corpus.

        """
        self.logger.info(f"Performing account checks before corpus creation for name [{corpus.name}]")
        existing_ids = self.find_corpora_by_name(corpus.name)
        has_existing = len(existing_ids) > 0
        if has_existing:
            self.logger.info(f"We found existing corpus with name [{corpus.name}]")
            if delete_existing:
                self.delete_corpus_by_name(corpus.name)
            elif unique:
                raise Exception(f"Unable to create a corpus with the name [{corpus.name}] as there were existing ones"
                                f" and the flag \"delete_existing\" is \"False\".")
            else:
                self.logger.warning(f"There is a potential for confusion as there is already a corpus with name "
                                    f"[{corpus.name}]")
        self.logger.info("Account checks complete, creating the new corpus")

        return self.corpora_api.create_corpus(corpus)



    def batch_index(self, corpus_key:str, documents: List[Union[dict, CreateDocumentRequest]], threads:int=10) -> List[any]:
        self.logger.info(f"Performing parallel [{threads}] document indexing requests")

        # Convert the Incoming dicts to typed classes.
        typed_docs = []
        for doc in documents:
            if isinstance(doc, dict):
                typed_docs.append(CreateDocumentRequest.from_dict(doc))
            else:
                typed_docs.append(doc)


        # Create our countdown latch
        latch = CountDownLatch(threads)

        # Create sub-indexers for each thread
        sub_indexers = [ SubIndexer(self.index_api, corpus_key, latch, thread_index) for thread_index in range(threads)]

        for index, doc in enumerate(documents):
            thread_index = index % threads
            sub_indexers[thread_index].add_doc(doc)

        for sub_indexer in sub_indexers:
            thread = Thread(target=sub_indexer.index_docs)
            thread.start()

        # Wait for completion.
        latch.sweat_it_out()

        # TODO Extract results from each sub-indexer into a final result array and return it.


