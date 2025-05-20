from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
from chromadb import AsyncHttpClient

chroma = AsyncHttpClient(host="localhost", port=5010)

openai_ef = OpenAIEmbeddingFunction(
    model_name="text-embedding-3-large",
    api_key=os.getenv("OPENAI_API_KEY"),
)