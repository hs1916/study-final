import streamlit as st
from streamlit import components
import openai
from googleapiclient.discovery import build
from langchain.llms import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores import FAISS
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from search.youtube_video import search_videos, youtube_caption_load
from embedding_process.embedding_step import embedding_vectorstores, video_document_list
from answer.answer_template import answer_using_template
from answer.baby_rasing import process_llm_response
from streamlit_chat import message

# 요리
from answer.chain_cook import answer_on_cook
from embedding_process.chroma_cook import embedding_cook_chroma
from search.youtube_cook import youtube_cook_video



openai.api_key = st.secrets["api_key"]


if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []

if "chat_answer_history" not in st.session_state:
    st.session_state["chat_answer_history"] = []

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


chat = ChatOpenAI(temperature=0, openai_api_key=openai.api_key)
sys = SystemMessage(content="당신은 한글로 친절하고 자세히 대답해주는 육아전문 AI 입니다")


PAGES = ["육아", "요리", "의학"]

# YouTube Data API 클라이언트 빌드
youtube = build("youtube", "v3", developerKey=st.secrets["youtube_api_key"])

st.set_page_config(
    page_title="Youtube Transcript Prototype",
    page_icon=":smiley:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": None},
)


def query_UI():
    st.title("의학")
    st.text("의학 정보에 대해 물어보세요")

    with st.form("form"):
        user_input = st.text_input("Prompt")
        submit = st.form_submit_button("Submit")

    if user_input and submit:
        # video 검색 및 caption load
        # embedding 및 쿼리
        results = search_videos(user_input, youtube)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=200
        )
        docs = video_document_list(results, text_splitter)
        qa = embedding_vectorstores(docs, openai.api_key)

        # 최종 Question 및 출력
        answer = qa({"query": user_input})
        template_answer = answer_using_template(answer, user_input, openai.api_key)
        print(template_answer)
        st.write(template_answer)
        # st.write(answer)
        video_url = "https://youtu.be/" + results[0]["videoId"]
        st.video(video_url)
        st.write("연관 영상: " + "https://youtu.be/" + results[0]["videoId"])


def run_UI():
    # st.title('Youtube Transcript Prototype')
    # st.text("생활 정보에 대해 물어보세요")

    st.sidebar.title("관심사항")

    if st.session_state.page:
        page = st.sidebar.radio("Navigation", PAGES, index=st.session_state.page)
    else:
        page = st.sidebar.radio("Navigation", PAGES, index=1)

    if page == "육아":
        st.sidebar.write(
            """
                         ## About
                            유투브 상의 육아에 대한 질문을 해주세요 
                         """
        )
        
        st.title("육아")
        st.text("육아 정보에 대해 물어보세요")

        with st.form("form"):
            user_input = st.text_input("Prompt")
            submit = st.form_submit_button("Submit")

        if user_input and submit:
            query, response = process_llm_response(user_input, openai.api_key)
            print('query: ' + query)
            print('response: ' + response)
            
            st.session_state["user_prompt_history"].append(user_input)
            st.session_state["chat_answer_history"].append(response)
            st.session_state["chat_history"].append((user_input,response))
            if st.session_state["chat_answer_history"]:
                for ans, query in zip(st.session_state["chat_answer_history"], st.session_state["user_prompt_history"]):
                    message(query, is_user=True)
                    message(ans)

    elif page == "요리":
        st.sidebar.write(
            """
                         ## About
                            유투브 상의 요리에 대한 질문을 해주세요 
                         """
        )
        st.title("요리")
        st.text("요리 정보에 대해 물어보세요")
        with st.form("form"):
            user_input = st.text_input("Prompt")
            submit = st.form_submit_button("Submit")
        if user_input and submit:
            youtube_cook_video(user_input, youtube)
            embedding_cook_chroma()
            answer = answer_on_cook(user_input)
            st.write(answer['answer'])

        
    elif page == "의학":
        st.sidebar.write(
            """
                        ## About
                        유투브 상의 의학에 대한 질문을 해주세요 
                        """
        )
        query_UI()


if __name__ == "__main__":
    print(PAGES.index("육아"))
    st.session_state.page = PAGES.index("육아")
    run_UI()
