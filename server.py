import streamlit as st
import os
from utils.check_password import check_password
from utils.streamlit_chromadb_connection import ChromadbConnection
from utils.create_documents import create_documents

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

st.session_state["chroma_collections"] = conn.get_all_collection_names()
if "chroma_collections" in st.session_state:
    st.session_state["selected_collection"] = st.selectbox(
            label="Chroma collections",
            options=st.session_state["chroma_collections"]
        )
    if st.session_state["selected_collection"]:
        collection_df = conn.get_collection_data(collection_name=st.session_state["selected_collection"])
        with st.container():
            st.subheader("Embedding data")
            st.markdown("Dataframe:")
            dataframe_placeholder = st.empty()
            dataframe_placeholder.dataframe(collection_df)

        with st.container():
            st.subheader("Document Upload")
            hotel_name = st.text_input('Hotel name', 'predgorie')
            file_uploads = st.file_uploader('Only TXT(s)', type=['txt'], accept_multiple_files=True)

            if file_uploads:
                for file in file_uploads:
                    try:
                        content = file.read().decode("utf-8")
                        docs = create_documents(content=content, meta={"source": file.name, "hotel": hotel_name})
                        conn.upload_documents(collection_name=st.session_state["selected_collection"], **docs)
                        st.toast(body='New file uploaded!',
                                 icon='✅')
                    except Exception as ex:
                        st.toast(body=f"{str(ex)}", icon="⚠️")
                        st.toast(body='Failed to upload file!', icon='❌')

                dataframe_placeholder.empty()
                new_df = conn.get_collection_data(collection_name=st.session_state["selected_collection"])
                dataframe_placeholder.dataframe(new_df)
