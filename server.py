import streamlit as st
import os
from utils.check_password import check_password
from utils.streamlit_chromadb_connection import ChromadbConnection

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


configuration = {
    "client": "HttpClient",
    "host": os.getenv("CHROMADB_HOST"),
    "port": os.getenv("CHROMADB_PORT"),
    "auth_token": os.getenv("CHROMA_AUTH_TOKEN")
}

conn = st.connection(name="http_connection",
                     type=ChromadbConnection,
                     **configuration)

collection_name = "botpress_collection"

collection_df = conn.get_collection_data(collection_name)
documents_collection_df = collection_df[["documents", "metadatas", "embeddings"]]
st.dataframe(documents_collection_df)
