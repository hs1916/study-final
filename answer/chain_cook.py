import os
import platform

import openai
import chromadb
import langchain
import tiktoken

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory


def answer_on_cook(query: str, api_key: str)->str:
  print("======= 시작 ========")

  embedding_function = OpenAIEmbeddings()
  vectordb = Chroma(persist_directory="../chroma/cook", embedding_function=embedding_function)

  model = ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo")
  
  memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
  chain = ConversationalRetrievalChain.from_llm(llm = model, retriever=vectordb.as_retriever(), memory=memory)

  return chain({"question": query})
