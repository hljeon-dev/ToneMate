import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# 초기화 함수들
def docs_load(pdf_path):
    loader = PyPDFLoader(pdf_path).load()
    return loader


def rc_text_split(corpus):
    rc_text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separators=["\n\n", "\n", " "],
        chunk_size=2000,
        chunk_overlap=500,
        encoding_name="o200k_base",
        model_name="gpt-4o",
    )
    text_documents = rc_text_splitter.split_documents(corpus)
    return text_documents


def embedding_model():
    model_name = "jhgan/ko-sroberta-multitask"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}
    model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    return model


def document_embedding(docs, model, save_directory):
    from langchain_chroma import Chroma
    import os
    import shutil

    # print("잠시만 기다려주세요.")

    if os.path.exists(save_directory):
        shutil.rmtree(save_directory)
        # print(f"디렉토리 {save_directory}가 삭제되었습니다.\n")

    # print("문서 벡터화를 시작합니다.")
    db = Chroma.from_documents(docs, model, persist_directory=save_directory)
    # print("새로운 Chroma 데이터베이스가 생성되었습니다.\n")

    return db


def load_existing_chroma(save_directory, embedding_model):
    """
    기존 Chroma 데이터베이스를 로드하는 함수
    """
    from langchain_chroma import Chroma

    # print(f"Chroma 데이터베이스를 '{save_directory}'에서 불러옵니다.")
    db = Chroma(persist_directory=save_directory, embedding_function=embedding_model)
    # print("기존 Chroma 데이터베이스를 성공적으로 로드했습니다.\n")

    return db


def chat_llm():
    load_dotenv(".env")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.56,
    )
    return llm

def result_qna(llm, query):
    syste_prompt = """당신은 퍼스널 컬러 전문가입니다. 친절하고 쉬운 언어로 표현하세요. 한 사람에게 알려주는 겁니다. '여러분'이라고 절대 하지 마세요. '당신'이라고 칭하세요."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", syste_prompt),
            ("human", "Question: {question}"),
        ]
    )

    chain = {
                "question": RunnablePassthrough()
            } | prompt | llm | StrOutputParser()

    result_response = chain.invoke(query)
    return result_response

def chat_qna(llm, db, query, content, color_type):
    db = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 5}
    )

    system_prompt = f"""
    당신은 퍼스널 컬러 전문가입니다. 
    사용자의 정보를 바탕으로 퍼스널 컬러와 관련된 질문에 대해 상냥하고 쉽게 설명해주세요. 
    퍼스널 컬러를 모르는 사람도 이해할 수 있도록 친절하고 자세히 답변하며, 어려운 전문 용어가 등장하면 반드시 풀어서 설명하세요.
    사용자의 정보를 바탕으로 해당 퍼스널 컬러 톤의 사람에게 적합한 색상, 스타일, 액세서리 등에 대해 조언하세요. 아래는 관련 정보를 기반으로 한 가이드입니다:
    {content}
    사용자가 자신의 톤에 대해 더 알고 싶거나, 스타일을 구체적으로 조정하고 싶다면, 꼭 이 정보를 바탕으로 맞춤형으로 조언을 제공하세요. 
    항상 긍정적이고 격려하는 태도로 응답하며, 사용자가 스스로의 매력을 더 잘 발견할 수 있도록 돕는 것을 목표로 하세요.
    최대 세 문장을 넘어가도록 하지 마세요.
    문장의 시작할 때, 퍼스널 컬러 유형에 대해서 언급하지 마세요.

    Context: {{context}}
    """

    human_prompt = f"""{color_type}Question: {{question}}"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
    )

    chain = {
                "context": db | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
                "content": RunnablePassthrough()
            } | prompt | llm | StrOutputParser()

    qna_response = chain.invoke(query)
    return qna_response

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)