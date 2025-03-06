from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2
import matplotlib.pyplot as plt

# 이미지 파일 경로 설정
img_path = 'data/test.png'
# 알파 채널을 포함하여 이미지를 불러옴
rgb_image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

# 알파 채널이 존재하는 경우 제거
if rgb_image.shape[2] == 4:
    rgb_image = rgb_image[:, :, :3]

# Mediapipe 얼굴 랜드마크 탐지 설정
base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# 이미지를 Mediapipe Image 형식으로 변환하고 랜드마크 탐지 실행
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
detection_result = detector.detect(mp_image)

# 영역의 픽셀을 추출하는 함수 정의
def extract_iris_pixels(rgb_image, face_landmarks):
    # 왼쪽 및 오른쪽 홍채(iris) 주변 좌표를 정의
    iris_landmarks = {
        'left_iris': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LEFT_IRIS],
        'right_iris': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_RIGHT_IRIS],
        'lips': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LIPS],
        'left_eyebrow': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LEFT_EYEBROW],
        'right_eyebrow': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_RIGHT_EYEBROW]
    }
    iris_pixels = {}

    for iris, landmarks in iris_landmarks.items():
        # 랜드마크 좌표를 이용해 눈썹 영역 좌표 배열 생성
        points = np.array([
            (int(landmark.x * rgb_image.shape[1]), int(landmark.y * rgb_image.shape[0])) for landmark in landmarks
        ], np.int32)

        # 마스크 생성
        mask = np.zeros(rgb_image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [points], 255)

        # 마스크를 RGB 이미지에 적용
        mask_rgb = cv2.merge([mask] * 3).astype(rgb_image.dtype)
        extracted_pixels = cv2.bitwise_and(rgb_image, mask_rgb)
        iris_pixels[iris] = extracted_pixels

    return iris_pixels

# 눈썹 픽셀을 추출하고 화면에 출력
if detection_result.face_landmarks:
    face_landmarks = detection_result.face_landmarks[0]
    iris_pixels = extract_iris_pixels(rgb_image, face_landmarks)

    for iris, pixels in iris_pixels.items():
        print(f"{iris} pixels (non-zero):", np.count_nonzero(pixels))
        plt.imshow(cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB))
        plt.title(f"{iris} iris pixels")
        plt.show()
else:
    print("No face landmarks detected.")
    