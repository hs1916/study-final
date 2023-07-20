import os
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

api_key = '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'


def embedding_cook_chroma():
  print("======= 시작 ========")
  loader = DirectoryLoader('../csv/cook', glob="**/*.csv", loader_cls=CSVLoader,  loader_kwargs = {'encoding':'UTF-8',  'csv_args' : {'delimiter': ','}}, use_multithreading=True)
  documents = loader.load()
  embeddings  = OpenAIEmbeddings(openai_api_key=api_key)
  print(documents);

  # load it into Chroma
  persist_directory="../chroma/cook"
  vectordb = Chroma.from_documents(documents, embeddings , persist_directory=persist_directory)  
  vectordb.persist()

  print("======= 끝 ========")
