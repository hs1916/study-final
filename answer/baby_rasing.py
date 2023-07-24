import webbrowser
import chromadb
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate

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

    # prompt_template = """
    # 마지막에 있는 Question 답하려면 다음 context를 사용하십시오.
    # 답을 모르면 그냥 모른다고 말하고 답을 지어내려고 하지 마세요.

    # {context}

    # Question: {question}
    # 메일로 쓸 수 있도록, 제목, 내용 형식으로 200자 이상 300자 이하로 만들어줘.
    # 단, 답변은 파싱해서 쓸 수 있도록 JSON 형식으로 반환해줘 
    # (단, '\t' 문자는 없게 해줘)
    # (개행문자는 '<br>' 로 대체해줘)
    # 예시는 아래와 같은 형태로 출력해줘
    # {{ 
    #     "title": 
    #         "육아 스트레스 해소 방법",
    #     "content": 
    #         "육아 스트레스를 해소하기 위해 카페에 혼자만의 시간을 가져가보세요.
    #          주변에 마음을 터놓고 얘기할 진이 있다면 힘든 상황과 마음을 나누어 보는 것이 좋아요.
    #          남편과 상의해서 집안일을 나누거나 가정의 경제 사정에 맞춰서 도움을 받는 것도 좋은 방법입니다.
    #          또한, 자신의 감정을 잘 컨트롤하고 아이에게 너무 많은 부담을 주지 않는 것이 중요합니다."
    # }}   
    # :
    # """
    
    prompt_template = """
    마지막에 있는 Question 답하려면 다음 context를 사용하십시오.
    답을 모르면 그냥 모른다고 말하고 답을 지어내려고 하지 마세요.

    {context}

    Question: {question}
    메일 답변에 쓸 수 있도록, 300자 이상 400자 이하로 만들어줘.
    또한, 메일 답변에 쓸 수 있도록 보기 좋게 개행문자 넣어서 형태를 갖춰서 출력해줘
    답변은 아래와 같은 형태로 출력해줘
    {{ 
             "육아 스트레스를 해소하기 위해 카페에 혼자만의 시간을 가져가보세요.
              주변에 마음을 터놓고 얘기할 진이 있다면 힘든 상황과 마음을 나누어 보는 것이 좋아요.
              남편과 상의해서 집안일을 나누거나 가정의 경제 사정에 맞춰서 도움을 받는 것도 좋은 방법입니다.
              또한, 자신의 감정을 잘 컨트롤하고 아이에게 너무 많은 부담을 주지 않는 것이 중요합니다."
    }}   
    :
    """
    
    
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    
    chain_type_kwargs = {"prompt": PROMPT}
    
    qa = RetrievalQA.from_chain_type(llm=turbo_llm
                                     ,chain_type="stuff" 
                                     ,retriever=retriever
                                     ,chain_type_kwargs=chain_type_kwargs
                                     ,return_source_documents=True
                                    )

    llm_response = qa({"query": search_string})
    video_id = llm_response["source_documents"][0].metadata["video_id"]
    start_time = llm_response["source_documents"][0].metadata["start"]
    start_string = f"{int(start_time/60)}m{int(start_time%60)}s"
    youtube_url = f"https://www.youtube.com/watch?v={video_id}&t={start_string}"
    print(llm_response["query"])
    print(llm_response["result"])
    
    print('make another window for showing related youtube [s]')
    webbrowser.open(youtube_url, new=2)
    print('make another window for showing related youtube [e]')
    return llm_response["query"], llm_response["result"]

def send_mail(gmail_user, gmail_password, to, subject, body):
    import json
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(gmail_user, gmail_password) 
        text = msg.as_string() 
        server.sendmail(gmail_user, to, text) 
        server.quit() 

    except Exception as e:
        print('Something went wrong...', e)

# 질문
# search_string = "육아할때 스트레스가 너무 심한데 어떻게 풀어야 하나요?"
# api_key = os.environ["OPENAI_API_KEY"]
# question, answer = process_llm_response(search_string, api_key)

# 메일 발송
gmail_user = 'hs1916@gmail.com'
gmail_password = 'kexlctgrckciqotr'
to = 'hs1916@gmail.com'

# send_mail(gmail_user, gmail_password, to, answer)