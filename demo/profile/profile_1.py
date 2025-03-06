import os
import gradio as gr
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
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
    load_dotenv("../.env")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.56,
    )
    return llm

def define_colortype(gender):
    content = read_text_file(file_path="../data/test")

    if ("봄 웜 브라이트" in content) and (gender == "male"):
        color_type = "저는 봄 웜 브라이트 타입의 남성입니다."
        return color_type
    elif ("봄 웜 브라이트" in content) and (gender == "female"):
        color_type = "저는 봄 웜 브라이트 타입의 여성입니다."
        return color_type
    elif ("봄 웜 라이트" in content) and (gender == "male"):
        color_type = "저는 봄 웜 라이트 타입의 남성입니다."
        return color_type
    elif ("봄 웜 라이트" in content) and (gender == "female"):
        color_type = "저는 봄 웜 라이트 타입의 여성입니다."
        return color_type
    elif ("여름 쿨 라이트" in content) and (gender == "male"):
        color_type = "저는 여름 쿨 라이트 타입의 남성입니다."
        return color_type
    elif ("여름 쿨 라이트" in content) and (gender == "female"):
        color_type = "저는 여름 쿨 라이트 타입의 여성입니다."
        return color_type
    elif ("여름 쿨 뮤트" in content) and (gender == "male"):
        color_type = "저는 여름 쿨 뮤트 타입의 남성입니다."
        return color_type
    elif ("여름 쿨 뮤트" in content) and (gender == "female"):
        color_type = "저는 여름 쿨 뮤트 타입의 여성입니다."
        return color_type
    elif ("가을 웜 뮤트" in content) and (gender == "male"):
        color_type = "저는 가을 웜 뮤트 타입의 남성입니다."
        return color_type
    elif ("가을 웜 뮤트" in content) and (gender == "female"):
        color_type = "저는 가을 웜 뮤트 타입의 여성입니다."
        return color_type
    elif ("가을 웜 다크" in content) and (gender == "male"):
        color_type = "저는 가을 웜 다크 타입의 남성입니다."
        return color_type
    elif ("가을 웜 다크" in content) and (gender == "female"):
        color_type = "저는 가을 웜 다크 타입의 여성입니다."
        return color_type
    elif ("겨울 쿨 브라이트" in content) and (gender == "male"):
        color_type = "저는 겨울 쿨 브라이트 타입의 남성입니다."
        return color_type
    elif ("겨울 쿨 브라이트" in content) and (gender == "female"):
        color_type = "저는 겨울 쿨 브라이트 타입의 여성입니다."
        return color_type
    elif ("겨울 쿨 다크" in content) and (gender == "male"):
        color_type = "저는 겨울 쿨 다크 타입의 남성입니다."
        return color_type
    elif ("겨울 쿨 다크" in content) and (gender == "female"):
        color_type = "저는 겨울 쿨 다크 타입의 여성입니다."
        return color_type
    else:
        return 0


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
            ("system",system_prompt),
            ("human", human_prompt),
        ]
    )

    chain = {
                "context": db | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
                "content": RunnablePassthrough()
            } | prompt | llm | StrOutputParser()

    response = chain.invoke(query)
    return response

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

def read_text_file(file_path="../data/test"):
    """
    로컬에 저장된 텍스트 파일의 내용을 읽어 반환하는 함수
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        return content
    except FileNotFoundError:
        return f"파일 '{file_path}'을(를) 찾을 수 없습니다."
    except Exception as e:
        return f"파일 읽기 중 에러가 발생했습니다: {e}"


# 기존 Chroma 데이터베이스 디렉토리
save_directory = "./chroma_db"

# 임베딩 모델 생성
model = embedding_model()

# 기존 Chroma 데이터베이스 로드 또는 새로 생성
if os.path.exists(save_directory):
    db = load_existing_chroma(save_directory, model)
else:
    # 문서 업로드
    loader = docs_load("../data/QA_set.pdf")

    # 문서 분할
    chunk = rc_text_split(loader)
    print(chunk)

    # 문서 임베딩
    db = document_embedding(chunk, model, save_directory)

# 채팅에 사용할 거대언어모델(LLM) 선택
llm = chat_llm()

# Gradio 앱 설정
with gr.Blocks() as demo:
    read_button = gr.Button("진단하기")
    output_text = gr.Textbox(label="퍼스널 컬러 진단 내용", lines=10)

    # 버튼 클릭 시 파일 내용을 출력
    read_button.click(read_text_file, inputs=[], outputs=output_text)

    # 챗봇 섹션
    chatbot_display = gr.Chatbot(label="퍼스널 컬러 상담", type="messages")
    user_input = gr.Textbox(label="질문을 입력하세요", placeholder="질문을 입력하고 버튼을 눌러주세요.")
    submit_button = gr.Button("질문하기")

    # 상태 저장
    state = gr.State([])

    # 질문 처리 함수
    def handle_qa(state, user_input):
        if isinstance(state, str):
            state = []

        content = read_text_file(file_path="../data/test")
        color_type = define_colortype("female")  # male or female (데모버전이라서 수동으로 설정)
        response = chat_qna(llm, db, user_input, content, color_type)

        profile_1 = 'https://lh3.googleusercontent.com/fife/ALs6j_EqXIVckhgZ2o5OHlF28pORP2VOCi-2dsX5CN5heWmQgbCx-z9Na0IV3BJJbWmk1RkYKdrzyya_f0L1WG0g5DQJp_pEeyMLVyZy_KtfYLDQN9RWhiY9i9cgyC6bNEBLT3Xohjj0KK4DFNCjyDVB_iF_8QaUaHqgXihwSi3O7MfDptLeMVKPERXRxgSpSXQI6cNlf0R6WQ8ef0u1OE7Xi2V6FUlyLAepjOtO7Yrh1om9VNfvadWRYwok44m97o8Nik-3snQjmePP2e0Z1Wbsi5fW6l-_oovb0dSBmfqKuuPY1QeiDia3upd7CI6W-IoyuMs1K8RJ5N_3mfUBHHd-mrceS1iA0ULdxtpyv2X1eK1sgFbpnLC3zQonV3KqVyabNcNifxM5ADj1SZE7O_b5gsYo1l9bDmtvDM3AME9o2wlT_vG6Ws9W7sO7gpPpWjaIq52yYPZ_5W3Lu1-ubFWaw4Vr-T9VFdrK4yryGhKaNqtHdIAv0VG-QUZXAqJRdYRei-kZYzZ_sa614zjxR3Bvs61WaP88G--T528YrPjp8zOPCvKgThYrlZWZ7Y-wLsFjZ4kp2KqXr133LDJ48ic6HWQoZXUpLfrOKedxZQcXQ1T_meT7FIrpE_5VtAKdh6wInBuXn9Rt2q6_-zx9fKix87IuHQvjOoKCBjw_NvEm6ZUA0RtCvG3Smp2cjcyu6xJ9W8xa1EMJEHiPBx0ITjdRQciqOepIbMcvkJAgH6d7NcPG9b8DaUOQUyyeuHkBImq9CAOAsKhTviCz-yTadumgb3XJc_nSbwgeJcSV6a9SRL8tt_rkaINtW_oMAYU1ilX6Z16xnWZAfd0HlWj2v7HG0y705ihQmW7aF1DwnxrajGrMn9WJJkolHdkwSJQ9JjNcrKzQ4EViQcCMDpNyHQRdtgxLh5o-ux1A4td_JdrVHm2VeFPIjncc94Br2rCwxwKMplmxgWPhzjvhTkQ3gl5qRoLEmX0cv3p7e8CiK8oE9lxYpJBK9A3uJKoISBA96aoMXdHxD0sUdx4K5Pki83RPb61Wf8JeRUpEgqIX0327In4cisvkjxsB_uO2RUn9nSAE9TVZC25O6YDyIzodCQRnLA7yvxLksd3OIq7s6KPENBw-DosehZpf4pcfwJiA-8AwTfX2Ul5pQAW8LA1gb9QuC1b0Btcq69ynENLGRi7E7wlqHEpGF8RWHY3h1ECWwYeQ6kpTRfHIZ2bnrxWP-0tb7J-Z-ijiRtEaxDOib2oPhXIDqBmZ6RtW2kYOLjiLYte7vpqV4bCZP11d9zfdRGEdR2gYN7FkXSdKzgE70YQxaLItpX4XwIz4XfbOlWg_iYu0DdfeIXwaLclDyrbaVuCp5GQBvnXfaREoNO_qDze4KWVWCqEtqcpXrJa89swAMgTQv4SE_3bfI-6ncDI-36_6VKaKm_1wQ3tpRmeHJcmyUlwq8JzOn_uI8i0qUzBmEf2zoqXtjWSkKnQqji1PRIhVB1Wf7X8nUhiVN-8SnPBVj4YvYiZNeMyOqLr2A5YxLiBxcI7Osu5m9N6IrQsVY2qCCMBwu2pIiqvNjL35pJbYIzPYIW1Q4ucStGlSGuIwg3rrjDxnmAB4OTKHEPMNR2hoRpm99vzrcgyK8FWbFasz_rGWOIBVbWBDPAgLDOzRvhxF6H-Pn_BUkj56zmTlEkbqluo7B5e8WYD2_Yu7EjnZHxI26V_RPu6g_6vAJ27JiHuxeam0xQjTsB1KI1uvyFb1pPgU04buO1VnwxwDmdA=w2926-h1646'
        profile_2 = 'https://lh3.googleusercontent.com/fife/ALs6j_E0N5wkhA8EqJ8dtn7PopmNd66RqeD0cXooF2ggSDZq0kRMd0OnMl-t_uzjpKSeHxeNO3ZwjMgrceKauzeKB8cBNWl6jvB3d6qm-77o-sAUX07b0H3_jB2-mly8yUV7EUE4sQHjx2QBLnQLxRJOZoW3CDjL-z46l3XRL0PC5Wl9Y_OVXqd2fVBlaCO-7fFDGDLQKvRiLrqMF9UocmLjEKSsrABTamFGKQbavj4nrveqstBw3856xjnCZGZ5-Z7fUNySLD39XiX1qIrCL8WlEyOWV5wyP7920GyVbNsW5sOmGtxZVAT_LUz7Ot22eDVm2CscJMPWXu316TBCecLvizjUpawTCyqgv6u0PTz4AM-Z7nwqc68jGnS6BsTV7g-mmFXHkOtnA6nTl6meuhpmLAmHcCMEqzXDgwvrQkS44N3urfKMj8ENL-PKOoYcYc-Xk3oLkS-Be_ZW6NnzYCT1IZG5RR1ak_g9Mg4fsEF_QFU6DLONhMSIU3GjT4draJjj1jC0bRVfKncBoUhGsGvaB7nS4ilKt82soMGR4fWvme6_yl-2wipK7a7YZU7TOFSOUsY9ShKwTIJ8V-hyMnC9HRAQDIDKTCcWkc9a6pVYU5BOhAw5FdFTXdGucZdeoJxtpDpKQ8NiJuxee182-MZton5s9wVQsXJ7iylvWjwi2smFwa3hY0O5xU0W4BpS4Aa4Bz0V4IhRgykcSOD5tCpusp6BgUpQWlN_MbedOmzJLyQ2uTcIsMnPNt--pyHc-nDymdP98kiL8HDa9L4sN6dPClZCjdzxXXm8ixE5V3QTza22Ou7tyEhxDDSLpy4HE7vaqJaQzporN46qfghcISd_Fdt359_YEIwfork3iyXb6C5-4QwQTNNaSqJbD7dZWcucePx_1aYNUPuwFmMWqfOanJpN9Vso_y8z9JqwNT3bEHlc6faaU1Lnr4KFrW9i4Nirh1AK4z-YTtrVDz29r1m6ZGd-CsqPMEG0E2sJOHSGOYGLL19du0PWbSDGJtozlzQKFrF5pZbKnaejV52zq0lb9Qi9F-b83Du398InAsdLtOypA8TZ3qoWO5lvPTE7mbRifQFf4Otv4qSUbi9M-WrkiIudUw5LyZ9K-bpDFv-7kPX3gpI-RwF3QHaNWOeWbcyP99d6ESErtWU1ycYJJE9Ium86DtnuugIVY-UvJYsg0uJc9l0su5sB5bSf-uCb6w16ofXJRn9B6UiKayEASiXSf3opCfaxZFylVuTClSFM7DgBZtXq9-2mYuuOQWujYtn4xpH2Uqk6i8ihQVxaavYMuOhglSO0e96Wkao-1WtKEKvzasRuzTbRqg1AMjsQcIRERz619rleTEKAi0wu12YzMlUmFoHvn23YGT10_BIY-osS0WpxpAtvBVy0BwB9PdIfb-_vdFXtbzkbMTj0IqF8j7Qdu_mChfZVgApPRMqUEL2IlvV7Tp9oy_4LMpMTBEfAtIE-7hj--paXkOtRtr4Ev5rHcUxfsS_F0rC-twmt9gzp38pPBxFZDNmHns3VBy9C7vMTQQ-iGbeqEXyUzsqe89TXKT4Z-yiqm9V5mgl0N-PBSeQftAxzkKbAbqf44w7K_-ijuekVfz61JTwbWzoAn2_i-lp9FBFW43QPBT850ALVkXxLSGJ7hqXCtGQD0dy1k8lYFggvym-vF6sMvH5kLBcZKyE-XcAChdqnuUKBy0-tl5DW_AMCdAVqhyy-dyhoa4ws3-ww3Camt43bIETj40yiavz5HbyBfHGSOw=w2926-h1646'
        profile_3 = 'https://lh3.googleusercontent.com/fife/ALs6j_FfZmkGAqf8UYsv6-9tkksg8w5eDFPlOOuzr2ilFmMktWXzE3kVgOn5l5Hhh8pvcnJbaKUDywxgj1XuI46WG7J9tk1f3FQMJc_lHPnpdD3ksN-JP-VhNMduGW6bH0IaY_nYp25uVANlWGsFUdPL5N5pZxjI5Z6zcuwhBbMXqRGR_4WQyjKZY5l4X_EyXV49Hf25NMJ-kMNFr_uJdbRv6Ccu2-h4ZnC69lxQsrrxuVcCKFy0xMNUiw2sR0Pk85qCdhnaxv4iIdwKCZ8fQDoRAT7lei_aB5OJYRPIOD7OviIBKkHgUn17CKF33z4qWuq1H5BPSYJrWuAWyZpnvQWu2vrn_oskFMp2cjNST_qKrik53rJLZNuZs4H7BlMhAnnrQwqpoGG1iRJbHjPtIQPyHNFXPtOoj7HeYFhHT4oQAJGdwD8vXpSMxm2wcLronxqapjyVQVGOkktqaep2BUSLUP0al9VP4hiScmxp559rbo1yfA_rDIqHR8UKTtGIYG1m7D3Rmsak8kimyUHxHTL_lU0Rnv-o0Lr1H8tA5VwgSXgUS5C-4CgVNzFMgRLC4wJDWqcNLhGYf0eDBzslFqg1w1iV3_quNTPzBffRoVbByxlqaXleN-kf-Yneenki9XZm3nHrz88ehVtKksl0VCwbHfCZJxhC3G1lOPgns5gkxvh9yfpAIv6cwat3hyjE6e_WoAXOXoDiXgMk38GI21FfvkfYUU9Cvg3ACO2V-MxgkZbVAbak-iWHIDEoQbwL4hUm6CggX3XBd4n6IH767Sj9B2eGXSlFXgXOAe3axzCQpfsDCCYmeFmaS6lVaBovernExf82z6bmUJJM5gshzirESfMrKDa5QjMPi141eTfNMxL1B_0MS6nrp_xdBCZpj1PQ_bHb0Hhl1fzVVJ44tG2VuwtqGdWVpYqhQ9oxt1yUSj8IClNyqaYm3n2h82cnrDDJTV6GhMTJ4n6M8KsHmHoqWkNhgbxJkYFk4Q8OvH7j8eLOFfcnTuuSuOcuYsruV4Y2IEPgDVQv6xjXPJECzhuTgQfXFxc_IsGMYGk_vI3ujy1ctG5ARL16z-7iHAmy48IKeqRRK8EOxUJ-bGnqefrL8YfQJe5h2s9hV__wKN-hXghyvO4G_yt9WxgDj2Qw3Xyq_h9xfW5ARDc1a6gdaYMqyE9sUJnlBcGdp9GkdOsiooystN_9-vrI-h1uGXV4Yllf4o7D-YeqB_cAHKnY04gSQLwRTQRm9PWWT6h97EC7EPQb4WWZqoTquVtwn0iFcKsygOu6pilu9JxSZoKn6u56Rz80mxYn2RNrBmNxHxrc6ERCY-GHLXBalJ1OjS2MZ4cFwWsofit5kY7lWku5sR9GWeWUQYqRwyOu0CljRPmMOo3ivIDgLK1FnXrzrxUeAMPNT8Gst1ECr0j5S26FiDcY1kY1kCg0IQ2hyAUmBq1BUebxfr-UgPIkdU0Y0OICtV0sg0CfAUhWdR6D64f86IRSP2_QWfNB0Rj26h2V4kT21-8rOnTAuyMh1rCqvz0osYdRUfnTZCnzf-HtxgKRHbzYUTxopQhyFQUXyH5em2-Ni4jFYpB4h4ewi0ikSUeljSoHc1i3seMu_Hzy_qoedDx7wXs-mqT1QwosRuo7dweq1ecRBYTOQpuOaV9YOQgwoNhsaaiEr17_ALHytoYZ5Sgyo1l24KOFUFhjI9w4poVzx7shkaeQ0NtWfWHgMmZlNv9Q1xPljh8xsUufJZXC6CXgEhl_Bd2xDfkI2kZNxlM=w2896-h1614'
        profile_html = f"<img src='{profile_1}' style='width:65px;height:65px;border-radius: 50%;margin-right: 10px;' />"
        state.append({"role": "user", "content": user_input})
        state.append({"role": "assistant", "content": profile_html + "\n\n" + response})
        return state, state

    submit_button.click(handle_qa, inputs=[state, user_input], outputs=[chatbot_display, state])

# 앱 실행
if __name__ == "__main__":
    demo.launch(share=False)
