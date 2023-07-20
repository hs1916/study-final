import webbrowser
import chromadb
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings


def process_llm_response(search_string, api_key):
    # client = chromadb.Client(
    #     Settings(
    #         chroma_api_impl="rest",
    #         chroma_server_host="15.164.29.82",
    #         chroma_server_http_port="8000",
    #     )
    # )
    
    client = chromadb.HttpClient(
        host="15.164.29.82",
        port="8000",
        settings=Settings(
            chroma_api_impl="rest"
        )
    )
    
    embedding = OpenAIEmbeddings(model="text-embedding-ada-002", chunk_size=1, openai_api_key=api_key)
    vectordb2 = Chroma(
        client=client, collection_name="parenting", embedding_function=embedding
    )
    retriever = vectordb2.as_retriever(search_kwargs={"k": 10})
    turbo_llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=api_key)
    qa_chain = RetrievalQA.from_chain_type(
        llm=turbo_llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    llm_response = qa_chain({"query": search_string})
    video_id = llm_response["source_documents"][0].metadata["video_id"]
    start_time = llm_response["source_documents"][0].metadata["start"]
    start_string = f"{int(start_time/60)}m{int(start_time%60)}s"
    youtube_url = f"https://www.youtube.com/watch?v={video_id}&t={start_string}"
    print(llm_response["query"])
    
    
    print('make another window for showing related youtube [s]')
    webbrowser.open(youtube_url, new=2)
    print('make another window for showing related youtube [e]')
    return llm_response["query"], llm_response["result"]
