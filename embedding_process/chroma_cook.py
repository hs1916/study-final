import os
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import chromadb


def embedding_cook_chroma(api_key: str):
  print("======= 시작 ========")
    
  loader = DirectoryLoader('../csv/cook', glob="**/*.csv", loader_cls=CSVLoader,  loader_kwargs = {'encoding':'UTF-8',  'csv_args' : {'delimiter': ','}}, use_multithreading=True)
  documents = loader.load()
  embeddings  = OpenAIEmbeddings(openai_api_key=api_key)
  print(documents);

  # load it into Chroma
  persist_directory="../chroma/cook"
  client = chromadb.PersistentClient(path=persist_directory)
  vectordb = Chroma(
    client=client,
    collection_name='cook',
    embedding_function=embeddings
  )
  
  # vectordb = Chroma.from_documents(documents, embeddings , persist_directory=persist_directory)  
  # vectordb.persist()

  print("======= 끝 ========")
