"""Rerank модели Compressa"""

from __future__ import annotations

import os
import requests
from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Union

from langchain_core.callbacks.manager import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
from langchain_core.pydantic_v1 import Field, SecretStr


_RerankRequestDocumentsItem = Union[str, Dict]

class _CompressaClient:
    """
    Параметры:
    ----------
    base_url : typing.Optional[str]
        Базовый URL-адрес, который будет использоваться для запросов от клиента.

    compressa_api_key : typing.Optional[str]
        Ключ Compressa API.
    """

    def __init__(
        self,
        *,
        base_url: Optional[str] = os.getenv("COMPRESSA_BASE_URL", "https://compressa-api.mil-team.ru/v1"),
        compressa_api_key: Optional[SecretStr] = Field(default=None, alias="api_key")
    ):
        
        self.compressa_api_key = compressa_api_key
        self.base_url = base_url

    def _rerank(
        self,
        *,
        query: str,
        documents: Sequence[_RerankRequestDocumentsItem],
        model: Optional[str] = "Compressa-ReRank",
        top_n: Optional[int] = 5,
        return_documents: Optional[bool] = False
    ) -> any:  #TODO: обработать ответ RerankResponse 
        
        headers = {
            "Content-Type": "application/json",
            "X-Fern-Language": "Python",
            "Authorization": "Bearer " + self.compressa_api_key.get_secret_value()
        }
           
        jsonBody = {
            "model": model,
            "query": query,
            "documents": documents,
            "top_n": top_n,
            "return_documents": return_documents,
            }
	    
        _response = requests.post(f"{self.base_url}/rerank", headers=headers, json=jsonBody)

        if _response.status_code == 200:
            return _response.json() 
        else:
            raise Exception(f"status_code: {_response.status_code}, body: {_response.text}")


class CompressaRerank(BaseDocumentCompressor):
    """Компрессор документов который использует `Compressa Rerank API`."""

    top_n: Optional[int] = 3
    """Количество возвращаемых документов."""
    model: str = "Compressa-ReRank"
    """Модель Compressa, используемая для реранка"""
    compressa_api_key: Optional[SecretStr] = Field(default=None, alias="api_key")
    """Ключ Compressa API. Может быть определён непосредственно или путём установки переменной окружения COMPRESSA_API_KEY."""
    client: Any = Field(default=None, exclude=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        compressa_api_key = self.compressa_api_key or SecretStr(os.getenv("COMPRESSA_API_KEY"))
        
        if compressa_api_key is None:
            raise Exception("status_code: None, body: The client must be instantiated be either passing in api_key or setting COMPRESSA_API_KEY")
            
        self.client = _CompressaClient(compressa_api_key=compressa_api_key)

    def _rerank(
        self,
        documents: Sequence[Union[str, Document, dict]],
        query: str,
        *,
        model: Optional[str] = None,
        top_n: Optional[int] = -1,
    ) -> List[Dict[str, Any]]:
        """Возвращает список документов, упорядоченный по их релевантности предоставленному запросу.

        Args:
            query: Запрос, используемый для реранка.
            documents: Последовательность документов для реранка.
            model: Модель, используемая для реранкинга. По умолчанию self.model.
            top_n : Количество результатов для возвращения. Если None возвращаются все результаты.
                По умолчанию self.top_n.
        """
        if len(documents) == 0:  # чтобы избегать пустых вызовов API
            return []
        docs = [
            doc.page_content if isinstance(doc, Document) else doc for doc in documents
        ]
        model = model or self.model
        
        top_n = top_n if (top_n is None or top_n > 0) else self.top_n
        results = self.client._rerank(
            query=query,
            documents=docs,
            model=model,
            top_n=top_n,
        )
        result_dicts = []
        for res in results["results"]:
            result_dicts.append(
                {"index": res["index"], "relevance_score": res["relevance_score"]}
            )
        return result_dicts

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Сжатие (compress) документов с использованием Compressa rerank API.

        Args:
            documents: Последовательность документов для сжатия.
            query: Запрос, используемый для компрессии документов.
            callbacks: Обратные вызовы для запуска во время процесса сжатия.

        Returns:
            Последовательность сжатых документов.
        """
        compressed = []
        for res in self._rerank(documents, query):
            doc = documents[res["index"]]
            doc_copy = Document(doc.page_content, metadata=deepcopy(doc.metadata))
            doc_copy.metadata["relevance_score"] = res["relevance_score"]
            compressed.append(doc_copy)
        return compressed
