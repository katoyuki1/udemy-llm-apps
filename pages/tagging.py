"""
poetry add llama-index@0.10.27 pypdf@4.1.0
"""

import streamlit as st
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json


class Attribute(BaseModel):
    language: str = Field(enum=["ja", "en"])
    tags: list[str] = Field(examples=[["Python", "Streamlit"]])


st.title("タグ付け")

text = st.text_area(label="タグ付けするテキスト")

if text:
    with st.spinner(text="タグ付け中..."):
        llm = ChatOpenAI(model_name="gpt-3.5-turbo")

        template = """
        以下のテキストに適切なタグを付けてください。タグは、言語とタグのリストを有効なJSON形式で返してください。
        JSON形式の文字列を``` で囲まないでください。

        言語: ja または en
        タグ: テキストの内容に関連するタグを複数付けてください。

        テキスト:
        {text}

        JSON形式:
        {{
            "language": "ja",
            "tags": ["タグ1", "タグ2", ...]
        }}
        """

        prompt = PromptTemplate(template=template, input_variables=["text"])

        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.invoke(text)

        st.write("デバッグ出力:")
        st.write(result)

        try:
            json_data = json.loads(result["text"])
            attr = Attribute.parse_obj(json_data)
            st.write(attr.dict())
        except (KeyError, json.JSONDecodeError, ValidationError) as e:
            st.error(f"エラーが発生しました: {str(e)}")
