import streamlit as st
import tempfile
from pathlib import Path
from langchain_openai import ChatOpenAI
from llama_index.core import VectorStoreIndex
from llama_index.readers.file import PDFReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
import logging

logging.basicConfig(level=logging.DEBUG)

st.title("PDFに関する質問")

index = st.session_state.get("index")


def on_change_file():
    if "index" in st.session_state:
        st.session_state.pop("index")


uploaded_file = st.file_uploader(
    label="質問対象のファイル", type="pdf", on_change=on_change_file
)


if uploaded_file and index is None:
    with st.spinner(text="準備中..."):
        with tempfile.NamedTemporaryFile() as f:
            f.write(uploaded_file.getbuffer())

            documents = PDFReader().load_data(file=Path(f.name))

            llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

            Settings.llm = OpenAI(model="gpt-3.5-turbo")
            Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
            Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
            Settings.num_output = 512
            Settings.context_window = 3900

            index = VectorStoreIndex.from_documents(documents)
            st.session_state["index"] = index

if index is not None:
    question = st.text_input(label="質問")

    if question:
        with st.spinner(text="考え中..."):
            query_engine = index.as_query_engine()
            answer = query_engine.query(question)
            st.write(answer.response)
            st.info(answer.source_nodes)
