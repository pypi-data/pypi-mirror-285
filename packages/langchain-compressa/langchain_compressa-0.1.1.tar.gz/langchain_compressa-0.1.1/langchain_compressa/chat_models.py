"""Чат модели Compressa"""

from typing import Any, List, Optional, Dict, Iterator
import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_core.pydantic_v1 import Field, SecretStr
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_openai import ChatOpenAI

COMPRESSA_API_BASE = "https://compressa-api.mil-team.ru/v1"

class ChatCompressa(BaseChatModel):
    """Интеграция чат моделей.

    Установка:
        Установите пакет``langchain_compressa`` и переменную окружения ``COMPRESSA_API_KEY``.

        .. code-block:: bash

            pip install git+https://github.com/insight-stream/langchain_compressa.git
            export COMPRESSA_API_KEY="ваш-ключ-здесь"

    Ключевые аргументы инициализации — параметры для комплишн:
        model: str
            Имя модели Compressa для использования.
        temperature: float
            Температура выборки.

    Ключевые аргументы инициализации — параметры клиента
        api_key: Optional[str]
            Ключ Compressa API. Если не передан то будет читаться из переменной окружения COMPRESSA_API_KEY.

    Полный список поддерживаемых аргументов инициализации и их описания см. в разделе параметров.

    Создание экземпляра:
        .. code-block:: python

            from langchain_compressa import ChatCompressa

            llm = ChatCompressa(
                model="...",
                temperature=0,
                # api_key="...",
            )

    Вызов:
        .. code-block:: python

            messages = [
                ("system", "Ты полезный переводчик. Переведи предложение пользователя на французский."),
                ("human", "Я люблю программирование."),
            ]
            llm.invoke(messages)

    Стриминг:
        .. code-block:: python

            for chunk in llm.stream(messages):
                print(chunk)

            stream = llm.stream(messages)
            full = next(stream)
            for chunk in stream:
                full += chunk
            full
   
    """ 
    
    model_name: str = Field(default="/app/resources/models/models/compressa-ai_Llama-3-8B-Instruct", alias="model")
    """Имя чат модели для использования."""
    temperature: float = 0.7
    """Температура для использования."""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Содержит любые параметры модели, действительные для вызова create, которые не указаны явно."""
    compressa_api_key: Optional[SecretStr] = Field(default=None, alias="api_key")
    """Автоматически берётся из переменной окружения `COMPRESSA_API_KEY` если не предоставлен."""
    streaming: bool = False
    """Выполнять стриминг результатов или нет"""
    client: Any = Field(default=None, exclude=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        compressa_api_key = self.compressa_api_key or SecretStr(os.getenv("COMPRESSA_API_KEY"))
        
        if compressa_api_key is None:
            raise Exception("status_code: None, body: The client must be instantiated be either passing in api_key or setting COMPRESSA_API_KEY")
            
        self.client = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            base_url=COMPRESSA_API_BASE,
            api_key=compressa_api_key
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        return self.client._generate(messages, stop, run_manager, **kwargs)
        

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
    
        return self.client._stream(messages, stop, run_manager, **kwargs)


    @property
    def _llm_type(self) -> str:
        """Возвращает тип чат модели."""
        return "chat-compressa"
        
    @property
    def _default_params(self) -> Dict[str, Any]:
        """Получить параметры по умолчанию для вызова Compressa API."""
        params = {
            "model": self.model_name,
            "stream": self.streaming,
            "temperature": self.temperature,
            **self.model_kwargs,
        }
        return params
        
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Получить идентифицирующие параметры."""
        return {"model_name": self.model_name, **self._default_params}
