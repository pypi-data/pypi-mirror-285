# langchain-compressa

Этот пакет содержит интеграцию LangChain и Compressa.

## Установка

```bash
pip install langchain-compressa
```

И вам следует настроить учетные данные, установив следующую переменную окружения:  
COMPRESSA_API_KEY

## Embeddings

`CompressaEmbeddings` класс предоставляет embeddings из Compressa.

```python
from langchain_compressa import CompressaEmbeddings

embeddings = CompressaEmbeddings()
embeddings.embed_query("В чем смысл жизни?")
```


## Chat model
` ChatCompressa` класс предоставляет чат модели из Compressa.

```python
from langchain_openai import ChatCompressa

llm = ChatCompressa(
    temperature=0,    
    # api_key="...",  # если вы предпочитаете передавать ключ непосредственно в конструктор вместо использования переменных окружения   
)

messages = [
    (
        "system",
        "Ты полезный помощник, который переводит с русского на болгарский. Переведи предложение пользователя.",
    ),
    ("human", "Я люблю программирование."),
]

ai_msg = llm.invoke(messages)
print(ai_msg)
print(ai_msg.content)

```

## CompressaRerank
` CompressaRerank` класс предоставляет реранк модели из Compressa.

```python
from langchain_core.documents import Document
from langchain_compressa.reranks import CompressaRerank

documents = [
    Document(
        page_content="""Карсон-Сити — столица американского штата Невада. 
        По данным переписи населения США 2010 года, население Карсон-Сити составляло 55 274 человека.""",
        metadata={"source": "https://пример.ru/1"}
    ),
    Document(
        page_content="""Содружество Северных Марианских островов — группа островов в Тихом океане, 
        которые являются политическим разделением, контролируемым Соединенными Штатами. 
        Столица — Сайпан.""",
        metadata={"source": "https://пример.ru/2"}
    ),
    Document(
        page_content="""Шарлотта-Амалия — столица и крупнейший город Виргинских островов США. 
        В нем проживает около 20 000 человек. Город находится на острове Сент-Томас.""",
        metadata={"source": "https://пример.ru/3"}
    ),
    Document(
        page_content="""Вашингтон, округ Колумбия (также известный как просто Вашингтон или 
        округ Колумбия, и официально как округ Колумбия) — столица Соединенных Штатов. 
        Это федеральный округ. На территории находятся резиденция президента США и многие 
        крупные государственные правительственные учреждения. Это делает его политическим центром 
        Соединенных Штатов Америки.""",
        metadata={"source": "https://пример.ru/4"}
    ), 
    Document(
        page_content="""Смертная казнь существовала в Соединенных Штатах еще до того, 
        как Соединенные Штаты стали страной. По состоянию на 2017 год смертная казнь разрешена 
        в 30 из 50 штатов. Федеральное правительство (включая вооруженные силы США) также 
        применяет смертную казнь.""",
        metadata={"source": "https://пример.ru/5"}
    )
]

query = "Какая столица у Соединенных Штатов Америки?"

reranker = CompressaRerank()
compress_res = reranker.compress_documents(query=query,  documents=documents)
```

## Пример RAG 

```python
import os
from langchain_compressa import CompressaEmbeddings, ChatCompressa, CompressaRerank
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma

COMPRESSA_API_KEY = os.getenv('COMPRESSA_API_KEY')

compressa_embedding = CompressaEmbeddings(api_key=COMPRESSA_API_KEY)
llm = ChatCompressa(api_key=COMPRESSA_API_KEY)

loader = WebBaseLoader("https://ru.wikipedia.org/wiki/Архитектура_фон_Неймана")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=100, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

vectorstore = Chroma.from_documents(documents=all_splits, embedding=compressa_embedding)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

compressor = CompressaRerank(api_key=COMPRESSA_API_KEY)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

system_template = f"""Ты помощник по вопросам-ответам. Используй следующую контекстную информацию, 
чтобы ответить на вопрос. Если в контексте нет ответа, ответь 'Не знаю ответа на вопрос'. 
Используй максимум три предложения и будь точным но кратким."""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", """Контекстная информация:

        {context}
        
        Вопрос: {input}		
    """),
])

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(compression_retriever, question_answer_chain)

answ = rag_chain.invoke({"input": "Какое узкое место у архитектуры фон Неймана?"})
print(answ["answer"])
```
