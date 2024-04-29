#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from typing import Literal, Union, List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import settings
from modules import models


class Retriever:
    _map = {}

    def __init__(self, namespace: str):
        # todo 单例 共享连接
        self.path = settings.DATA_DIR / namespace / 'db'
        self.collection = namespace
        self.store = self.get_or_create_vst()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=0,
            separators=["\n\n", "\n", "。", "！", "？", "，"],
            length_function=len
        )

    @classmethod
    def get_instance(cls, namespace):
        if namespace not in cls._map:
            cls._map[namespace] = cls(namespace)
        return cls._map[namespace]

    def get_or_create_vst(self):
        from langchain.vectorstores.qdrant import Qdrant
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import VectorParams, Distance

        client = QdrantClient(path=self.path)
        collections = client._client.collections.keys()
        if not (self.collection in collections):
            client.create_collection(
                **{'collection_name': self.collection,
                   'vectors_config': VectorParams(
                       size=1536, distance=Distance.COSINE, hnsw_config=None, quantization_config=None, on_disk=True
                   )
               }
            )
        return Qdrant(client, self.collection, models.embeddings)

    def add_context(self, context: Document, need_spilt=True):
        if need_spilt:
            texts = self.text_splitter.split_text(context.content)
        else:
            texts = [context.content]
        metadata = context.metadata
        context.metadata['created'] = datetime.datetime.now()
        metadatas = [metadata] * len(texts)
        self.store.add_texts(texts, metadatas)

    def search_context(self, query, k: int = 8, order_by: Literal['time', 'similarity'] = 'time') -> List[Document]:
        docs = self.store.similarity_search(query, k=k)
        if order_by == 'time':
            contexts = sorted(docs, key=lambda x: x.additional_kwargs['created'])
        else:
            contexts = docs
        return contexts


retriever = Retriever()