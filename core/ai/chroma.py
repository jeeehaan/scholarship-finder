from chromadb import HttpClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
from dotenv import load_dotenv

load_dotenv()

chroma_client = HttpClient(host="localhost", port=5010)
openai_ef = OpenAIEmbeddingFunction(
    model_name="text-embedding-3-large",
    api_key=os.getenv("OPENAI_API_KEY"),
)