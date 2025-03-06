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

def chat_qna(llm, db, query):
    db = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 5}
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                

                Context: {context}
                """,
            ),
            ("human", "Question: {question}"),
        ]
    )

    chain = {
                "context": db | RunnableLambda(format_docs),
                "question": RunnablePassthrough()
            } | prompt | llm | StrOutputParser()

    response = chain.invoke(query)
    return response

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

###################################################################
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2
from sklearn.cluster import KMeans


# Mediapipe 얼굴 랜드마크 탐지 설정 함수
def initialize_face_detector(model_path='../data/face_landmarker_v2_with_blendshapes.task'):
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1
    )
    return vision.FaceLandmarker.create_from_options(options)


# 이미지를 Mediapipe Image 형식으로 변환 및 수동 화이트 밸런스 조정
def load_and_prepare_image_with_manual_white_balance(img_path):
    rgb_image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if rgb_image.shape[2] == 4:  # 알파 채널(투명도) 제거
        rgb_image = rgb_image[:, :, :3]

    # 각 채널의 평균 계산
    avg_r = np.mean(rgb_image[:, :, 0])
    avg_g = np.mean(rgb_image[:, :, 1])
    avg_b = np.mean(rgb_image[:, :, 2])

    # 목표 평균을 각 채널의 평균의 중간값으로 설정
    avg_gray = (avg_r + avg_g + avg_b) / 3
    scale_r = avg_gray / avg_r
    scale_g = avg_gray / avg_g
    scale_b = avg_gray / avg_b

    # 각 채널에 스케일 적용
    balanced_image = rgb_image.copy()
    balanced_image[:, :, 0] = np.clip(balanced_image[:, :, 0] * scale_r, 0, 255)
    balanced_image[:, :, 1] = np.clip(balanced_image[:, :, 1] * scale_g, 0, 255)
    balanced_image[:, :, 2] = np.clip(balanced_image[:, :, 2] * scale_b, 0, 255)

    return balanced_image.astype(np.uint8)


# 얼굴 랜드마크에서 각 부위별 픽셀 추출 (기존 함수 재사용)
def extract_all_pixels(rgb_image, face_landmarks):
    landmarks_dict = {
        'left_iris': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LEFT_IRIS],
        'right_iris': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_RIGHT_IRIS],
        'lips': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LIPS],
        'left_eyebrow': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LEFT_EYEBROW],
        'right_eyebrow': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_RIGHT_EYEBROW],
        'face_skin': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_FACE_OVAL]
    }

    all_pixels = []

    for body, landmarks in landmarks_dict.items():
        points = np.array([
            (int(landmark.x * rgb_image.shape[1]), int(landmark.y * rgb_image.shape[0])) for landmark in landmarks
        ], np.int32)

        mask = np.zeros(rgb_image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [points], 255)

        if body == 'face_skin':
            exclude_regions = ['left_iris', 'right_iris', 'lips', 'left_eyebrow', 'right_eyebrow']
            for region in exclude_regions:
                exclude_points = np.array([
                    (int(face_landmarks[idx[0]].x * rgb_image.shape[1]),
                     int(face_landmarks[idx[0]].y * rgb_image.shape[0]))
                    for idx in getattr(mp.solutions.face_mesh, 'FACEMESH_' + region.upper())
                ], np.int32)
                cv2.fillPoly(mask, [exclude_points], 0)

        mask_rgb = cv2.merge([mask] * 3).astype(rgb_image.dtype)
        extracted_pixels = cv2.bitwise_and(rgb_image, mask_rgb)

        pixels_list = []
        for y in range(extracted_pixels.shape[0]):
            for x in range(extracted_pixels.shape[1]):
                if mask[y, x] == 255:
                    pixel_value = extracted_pixels[y, x]
                    pixels_list.append(pixel_value[::-1].tolist())

        all_pixels.append({'region': body, 'pixels': pixels_list})

    return all_pixels


# 좌우 부위의 주요 색상을 찾기 위한 KMeans 함수
def find_combined_optimal_clusters(left_pixels, right_pixels, max_clusters=10):
    combined_pixels = left_pixels + right_pixels
    rgb_array = np.array(combined_pixels)

    inertias = []
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(rgb_array)
        inertias.append(kmeans.inertia_)

    optimal_clusters = inertias.index(min(inertias)) + 1
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    kmeans.fit(rgb_array)

    dominant_cluster_index = np.argmax(np.bincount(kmeans.labels_))
    return kmeans.cluster_centers_[dominant_cluster_index].astype(int)


# 개별 부위의 주요 색상을 찾기 위한 KMeans 함수
def find_optimal_cluster(rgb_values, max_clusters=10):
    rgb_array = np.array(rgb_values)

    inertias = []
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(rgb_array)
        inertias.append(kmeans.inertia_)

    optimal_clusters = inertias.index(min(inertias)) + 1
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    kmeans.fit(rgb_array)

    dominant_cluster_index = np.argmax(np.bincount(kmeans.labels_))
    return kmeans.cluster_centers_[dominant_cluster_index].astype(int)


# 얼굴 주요 색상 분석 함수
def analyze_face_colors_with_white_balance(img_path):
    rgb_image = load_and_prepare_image_with_manual_white_balance(img_path)
    detector = initialize_face_detector()

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    detection_result = detector.detect(mp_image)

    if not detection_result.face_landmarks:
        print("No face landmarks detected.")
        return

    face_landmarks = detection_result.face_landmarks[0]
    all_pixels = extract_all_pixels(rgb_image, face_landmarks)

    # 좌우 눈동자 색상
    left_iris_pixels = next(item['pixels'] for item in all_pixels if item['region'] == 'left_iris')
    right_iris_pixels = next(item['pixels'] for item in all_pixels if item['region'] == 'right_iris')
    combined_iris_color = find_combined_optimal_clusters(left_iris_pixels, right_iris_pixels)
    print("Combined iris dominant color:", combined_iris_color)

    # 좌우 눈썹 색상
    left_eyebrow_pixels = next(item['pixels'] for item in all_pixels if item['region'] == 'left_eyebrow')
    right_eyebrow_pixels = next(item['pixels'] for item in all_pixels if item['region'] == 'right_eyebrow')
    combined_eyebrow_color = find_combined_optimal_clusters(left_eyebrow_pixels, right_eyebrow_pixels)
    print("Combined eyebrow dominant color:", combined_eyebrow_color)

    # 입술 색상
    lips_pixels = next(item['pixels'] for item in all_pixels if item['region'] == 'lips')
    lips_color = find_optimal_cluster(lips_pixels)
    print("Lips dominant color:", lips_color)

    # 얼굴 피부 색상
    face_skin_pixels = next(item['pixels'] for item in all_pixels if item['region'] == 'face_skin')
    face_skin_color = find_optimal_cluster(face_skin_pixels)
    print("Face skin dominant color:", face_skin_color)

    return combined_iris_color, combined_eyebrow_color, lips_color, face_skin_color

def result_qna(llm, query):
    syste_prompt = """당신은 퍼스널 컬러 전문가입니다. 친절하고 쉬운 언어로 표현하세요. 여러분이라고 하지 마세요."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", syste_prompt),
            ("human", "Question: {question}"),
        ]
    )

    chain = {
                "question": RunnablePassthrough()
            } | prompt | llm | StrOutputParser()

    response = chain.invoke(query)
    return response

def process_image(image):
    from PIL import Image
    # Gradio에서 제공하는 비디오 데이터를 처리
    format_image = Image.fromarray(image)

    image_path = "../data/test.png"
    format_image.save(image_path)

    iris, eyebrow, lip, face_skin = analyze_face_colors_with_white_balance(image_path)

    system_input = (f"당신은 퍼스널 컬러 전문가입니다. "
                    f"눈동자: {iris}, 눈썹: {eyebrow}, 입술: {lip}, 피부: {face_skin} 색 정보를 바탕으로 퍼스널 컬러를 진단하고, 그에 대한 상세하고 유익한 조언을 제공하는 역할을 맡습니다. "
                    f"사용자가 퍼스널 컬러를 잘 모를 수도 있으니, 반드시 친절하고 쉬운 언어로 설명하세요. 여러분이라고 하지 마세요."
                    f"진단 과정에서 색상을 설명할 때 RGB 값 등 기술적인 용어를 사용하지 말고, 색감과 이미지를 떠올릴 수 있는 친근한 언어로 표현하세요."
                    f"어려운 용어가 등장하면 반드시 풀어서 설명하고, 답변은 항상 진단의 느낌을 유지하며 전문가다운 신뢰감을 줄 수 있도록 작성하세요."
                    f"다음은 사용자의 퍼스널 컬러 진단에서 포함해야 할 주요 항목입니다: 1. 퍼스널 컬러 유형과 특징 2. 추천 색상과 피해야 할 색상 3. 스타일링 가이드 4. 머리색 추천 5. 추천 액세서리"
                    f"답변은 사용자에게 꼭 맞는 맞춤형 진단으로 작성하고, 따뜻하고 격려하는 태도를 유지하세요. 사용자가 자신의 매력을 더 잘 이해하고, 이를 활용할 수 있도록 돕는 것을 목표로 하세요."
                    f"퍼스널 컬러 종류는 봄 웜 라이트, 봄 웜 브라이트, 여름 쿨 뮤트, 여름 쿨 라이트, 가을 웜 뮤트, 가을 웜 다크, 겨울 쿨 뮤트, 겨울 쿨 다크 중에서 하나로 출력해주세요.")

    # 채팅에 사용할 거대언어모델(LLM) 선택
    llm = chat_llm()

    response = result_qna(llm, system_input)

    text_path = "../data/test"

    try:
        with open(text_path, 'w', encoding='utf-8') as file:
            file.write(response)
        print(response)
        print(f"텍스트가 {text_path}에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 에러가 발생했습니다: {e}")

    return image


# 기존 Chroma 데이터베이스 디렉토리
save_directory = "./chroma_db"

# 임베딩 모델 생성
model = embedding_model()

# 기존 Chroma 데이터베이스 로드 또는 새로 생성
if os.path.exists(save_directory):
    db = load_existing_chroma(save_directory, model)
else:
    # 문서 업로드
    loader = docs_load("../data/RGB_results.pdf")

    # 문서 분할
    chunk = rc_text_split(loader)
    print(chunk)

    # 문서 임베딩
    db = document_embedding(chunk, model, save_directory)

# 채팅에 사용할 거대언어모델(LLM) 선택
llm = chat_llm()

# Gradio 앱 설정
with gr.Blocks() as demo:
    gr.Markdown("# 문서 기반 QA 시스템")

    # 웹캠 섹션
    gr.Markdown("## 웹캠으로 이미지를 캡처하세요!")
    webcam = gr.Interface(process_image, gr.Image(), "image")

# 앱 실행
if __name__ == "__main__":
    demo.launch(share=False)
