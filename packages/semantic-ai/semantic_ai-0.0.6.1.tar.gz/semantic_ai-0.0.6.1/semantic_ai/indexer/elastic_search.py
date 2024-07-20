from elasticsearch import Elasticsearch
from langchain.embeddings.base import Embeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import ElasticsearchStore

from semantic_ai.indexer.base import BaseIndexer
from semantic_ai.utils import check_isfile, iter_to_aiter, sync_to_async


class ElasticsearchIndexer(BaseIndexer):

    def __init__(
            self,
            *,
            url: str,
            index_name: str,
            user: str | None = None,
            password: str | None = None,
            embedding: Embeddings | None = HuggingFaceEmbeddings(),
            verify_certs: bool = True,
            api_key: str | None = None,
            **kwargs
    ):
        self.url = url
        self.user = user
        self.password = password
        self.index_name = index_name
        self.embeddings = embedding
        self.verify_certs = verify_certs
        self.api_key = api_key
        self.kwargs = kwargs

        self._conn = Elasticsearch(
            self.url,
            basic_auth=(self.user, self.password),
            verify_certs=self.verify_certs,
            **kwargs
        )
        self._vector_store: ElasticsearchStore = ElasticsearchStore(
            embedding=self.embeddings,
            index_name=f"{self.index_name}",
            es_connection=self._conn,
            es_api_key=self.api_key,
            **self.kwargs
        )

    async def create(self) -> ElasticsearchStore:
        return ElasticsearchStore(
            embedding=self.embeddings,
            index_name=f"{self.index_name}",
            es_connection=self._conn,
            es_api_key=self.api_key,
            **self.kwargs
        )

    async def index(self, extracted_json_dir_or_file: str, recursive: bool = False):
        if extracted_json_dir_or_file:
            documents_data = self.from_documents(extracted_json_dir_or_file, recursive)
            documents = await documents_data.asend(None)
            if await check_isfile(extracted_json_dir_or_file):
                try:
                    if documents:
                        await ElasticsearchStore.afrom_documents(
                            documents=documents,
                            embedding=self.embeddings,
                            index_name=self.index_name,
                            es_connection=self._conn,
                            **self.kwargs
                        )
                except Exception as ex:
                    print(f"{ex}")
            else:
                try:
                    async for docs in iter_to_aiter(documents):
                        if docs:
                            await ElasticsearchStore.afrom_documents(
                                documents=docs,
                                embedding=self.embeddings,
                                index_name=self.index_name,
                                es_connection=self._conn,
                                **self.kwargs
                            )
                except Exception as ex:
                    print(f"{ex}")
        else:
            raise ValueError(f"Please give valid file or directory path.")

    async def exists(self, index_name: str) -> bool:
        exist_index = await sync_to_async(
            self._conn.indices.exists,
            index=index_name
        )
        return exist_index

    async def delete(self, index_name: str):
        if await self.exists(index_name):
            await sync_to_async(
                self._conn.indices.delete,
                index=index_name
            )
            return True
        else:
            return False
