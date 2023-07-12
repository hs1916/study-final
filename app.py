import streamlit as st
import openai
from googleapiclient.discovery import build
from langchain.document_loaders import YoutubeLoader
from langchain.llms import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.text_splitter import CharacterTextSplitter

openai.api_key = st.secrets["api_key"]


chat = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.9, openai_api_key=openai.api_key)
sys = SystemMessage(content='당신은 한글로 대답해주는 육아전문 AI 입니다')



PAGES = [
    '육아',
    '요리',
    '의학'
]

print(st.secrets["youtube_api_key"])

# YouTube Data API 클라이언트 빌드
youtube = build('youtube', 'v3', developerKey=st.secrets["youtube_api_key"])

st.set_page_config(
    page_title="Youtube Transcript Prototype",
    page_icon=":smiley:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": None
    }
)

def search_videos(query, max_results=10):
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_results
    ).execute()

    # 검색 결과 파싱
    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append({
                'title': search_result['snippet']['title'],
                'video_id': search_result['id']['videoId']
            })

    return videos


def query_UI():
    st.title('Youtube Transcript Prototype')
    st.text("육아 정보에 대해 물어보세요")
    
    with st.form("form"):
        user_input = st.text_input("Prompt")
        submit = st.form_submit_button("Submit")
    
    if user_input and submit:
        
        results = search_videos(user_input)
        pick = results[0]
        loader = YoutubeLoader.from_youtube_url(
                youtube_url='https://youtu.be/'+ pick['video_id'],
                language='ko',
                add_video_info=True
            )
        document = loader.load()
        outmsg = f"Found video from {document[0].metadata['author']} that is {document[0].metadata['length']} seconds long"
        text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=100)
        docs = text_splitter.split_documents(document)
        chain = load_summarize_chain(llm=chat, chain_type='map_reduce', verbose=True)
        result = chain.run(docs)
        
        msg = HumanMessage(content=result)
        aimsg = chat([sys, msg])
        
        st.write(aimsg.content)
        st.write('연관 영상: '+ 'https://youtu.be/'+ pick['video_id'])
        
        # st.write(user_input)
    
    
def run_UI():
    # st.title('Youtube Transcript Prototype')
    # st.text("생활 정보에 대해 물어보세요")

    st.sidebar.title('관심사항')
    
    if st.session_state.page:
        page = st.sidebar.radio('Navigation', PAGES, index=st.session_state.page)
    else:
        page = st.sidebar.radio('Navigation', PAGES, index=1)
        
    
    if page == '육아':
        st.sidebar.write("""
                         ## About
                            유투브 상의 육아에 대한 질문을 해주세요 
                         """)
        query_UI()
        
    elif page == '요리':
        st.sidebar.write("""
                         ## About
                            유투브 상의 요리에 대한 질문을 해주세요 
                         """)
    elif page == '의학':
        st.sidebar.write("""
                        ## About
                        유투브 상의 의학에 대한 질문을 해주세요 
                        """)    

    
    
if __name__ == '__main__':
    print(PAGES.index('육아'))
    st.session_state.page = PAGES.index('육아')
    run_UI()
