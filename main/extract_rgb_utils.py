import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2
from sklearn.cluster import KMeans


# Mediapipe 얼굴 랜드마크 탐지 설정 함수
def initialize_face_detector(model_path='face_landmarker_v2_with_blendshapes.task'):
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

    # 각 채널(r,g,b)의 평균 계산
    avg_r = np.mean(rgb_image[:, :, 0])
    avg_g = np.mean(rgb_image[:, :, 1])
    avg_b = np.mean(rgb_image[:, :, 2])

    # 목표 평균을 각 채널의 평균의 평균 값으로 설정
    avg_gray = (avg_r + avg_g + avg_b) / 3
    scale_r = avg_gray / avg_r
    scale_g = avg_gray / avg_g
    scale_b = avg_gray / avg_b

    # 각 채널에 스케일 적용
    balanced_image = rgb_image.copy()
    balanced_image[:, :, 0] \
        = np.clip(balanced_image[:, :, 0] * scale_r, 0, 255)
    balanced_image[:, :, 1] \
        = np.clip(balanced_image[:, :, 1] * scale_g, 0, 255)
    balanced_image[:, :, 2] \
        = np.clip(balanced_image[:, :, 2] * scale_b, 0, 255)

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
