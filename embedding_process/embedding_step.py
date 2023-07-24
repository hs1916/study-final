from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS
from typing import List
from langchain.docstore.document import Document
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from search.youtube_video import youtube_caption_load
import chromadb


def embedding_vectorstores(docs: List[Document], api_key: str):
    
    print('-------------')
    print(docs)
    print('-------------')
    for doc in docs:
        print(doc.metadata)
        if doc.metadata['description'] is None:
            print(doc.metadata['description'])
            doc.metadata['description'] = 'No description'
            
    chroma_client = chromadb.HttpClient(host="3.38.132.139", port=8000)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    # Chroma.from_documents(
    #     client=chroma_client, documents=docs, embedding=embeddings
    # )
    
    # vectorstore = FAISS.from_documents(
    #     documents=docs, embedding=OpenAIEmbeddings(openai_api_key=api_key)
    # )
    

    
    vectorstore = Chroma(
        client=chroma_client,
        collection_name="langchain",
        embedding_function=embeddings,
    )


    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo-16k", openai_api_key=api_key),
        retriever=vectorstore.as_retriever(),
    )
    return qa


def video_document_list(videos: List, text_splitter: any) -> List:
    total_document_list = []
    total_docuemnt_length = 0

    for v in videos:
        docs = youtube_caption_load(v["videoId"])
        d = text_splitter.split_documents(docs)
        total_document_list.extend(d)
        total_docuemnt_length += len(d)

    return total_document_list
