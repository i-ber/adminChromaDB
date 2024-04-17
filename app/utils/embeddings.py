import os
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from yandex_chain import YandexEmbeddings

ya_auth = {
    "api_key": os.getenv("YA_API_KEY"),
    "folder_id": os.getenv("YA_FOLDER_ID")
}

def create_documents(content, meta):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=20,
            separators=[
                "\n\n",
            ]
        )
        texts = text_splitter.split_text(content)
        embedder = YandexEmbeddings(**ya_auth)
        embeddings = embedder.embed_documents(texts)
        return {
            "ids": [str(uuid.uuid4()) for _ in texts],
            "documents": texts,
            "metadatas": [meta for _ in texts],
            "embeddings": embeddings
        }
    except Exception as exception:
        raise Exception(f"Error while create documents: {str(exception)}")


def embed_query(text):
    try:
        embedder = YandexEmbeddings(**ya_auth)
        return embedder.embed_query(text)
    except Exception as exception:
        raise Exception(f"Error while embed query: {str(exception)}")
