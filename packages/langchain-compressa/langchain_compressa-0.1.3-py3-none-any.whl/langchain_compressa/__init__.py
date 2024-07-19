from importlib import metadata

from langchain_compressa.embeddings import CompressaEmbeddings
from langchain_compressa.chat_models import ChatCompressa
from langchain_compressa.reranks import CompressaRerank

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Случай, когда метаданные пакета недоступны.
    __version__ = ""
del metadata  # необязательно, позволяет избежать загрязнения результатов dir(__package__)

__all__ = [
    "CompressaEmbeddings",
    "ChatCompressa",
    "CompressaRerank",
    "__version__",
]
