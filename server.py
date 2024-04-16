import streamlit as st
import os
from utils.check_password import check_password
from utils.streamlit_chromadb_connection import ChromadbConnection
from utils.embeddings import create_documents, embed_query
import pandas as pd

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
    selected_collection_placeholder = st.empty()
    st.session_state["selected_collection"] = selected_collection_placeholder.selectbox(
            label="Chroma collections",
            options=st.session_state["chroma_collections"]
        )

    delete_button_placeholder = st.empty()

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

            document_query_placeholder = st.empty()
            with document_query_placeholder.container():
                st.subheader("Document Search")
                query_placeholder = st.empty()
                query = query_placeholder.text_input(label="Query")
                query_dataframe_placeholder = st.empty()

                if query:
                    embeddings = embed_query(query)
                    query_dict = conn.query(collection_name=st.session_state["selected_collection"], query=[embeddings])
                    query_dict0 ={}
                    for key, value in query_dict.items():
                        if value:
                            query_dict0[key] = value[0]
                    query_df = pd.DataFrame(data=query_dict0)[["ids", "documents", "metadatas", "embeddings"]]
                    query_dataframe_placeholder.dataframe(query_df)
            document_add_placeholder = st.empty()
            with document_add_placeholder.container():
                st.subheader("Document Add")
                pass
            document_remove_placeholder = st.empty()
            with document_remove_placeholder.container():
                st.subheader("Document remove by ids")
                pass
    if delete_button_placeholder.button(label="❗ Delete collection", type="primary"):
        st.cache_resource.clear()
        try:
            conn.delete_collection(st.session_state["selected_collection"])
            st.toast(body='Collection deleted!', icon='✅')
        except Exception as ex:
            st.toast(body=f"{str(ex)}", icon="⚠️")
            st.toast(body="Failed to delete connection", icon="😢")
        st.rerun()


with st.container():
    new_collection_name = st.sidebar.text_input(label='New collection name', placeholder='')
    if st.sidebar.button("Create"):
        try:
            conn.create_collection(collection_name=new_collection_name,
                                   embedding_function_name="DefaultEmbeddingFunction",
                                   embedding_config={})
            st.toast(body='New collection created!',
                     icon='✅')

            st.session_state["chroma_collections"] = conn.get_all_collection_names()
            selected_collection_placeholder.empty()
            st.session_state["selected_collection"] = selected_collection_placeholder.selectbox(
                label="Chroma collections",
                options=st.session_state["chroma_collections"],
                key="new_select_box"
            )
        except Exception as ex:
            st.toast(body=f"{str(ex)}",
                     icon="⚠️")
            st.toast(body="Failed to create new connection",
                     icon="😢")
        st.rerun()
