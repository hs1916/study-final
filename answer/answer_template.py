from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain

# 최종 요약 Template
prompt = PromptTemplate(
    input_variables=["main", "question"],
    template="""
        Text: {main} \n 위 텍스트에 기반을 둔 체
        {question} 에 대해 대답해줘
    """,
)


def answer_using_template(query_result: str, query: str, api_key: str) -> str:
    chat = ChatOpenAI(temperature=0, openai_api_key=api_key)
    chain = LLMChain(llm=chat, prompt=prompt)
    return chain.run(main=str, question=query)
