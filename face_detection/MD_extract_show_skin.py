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

# 얼굴 전체 영역을 추출하는 함수 정의
def extract_face_pixels(rgb_image, face_landmarks):
    # 얼굴 외곽을 정의하는 좌표 (FACE_OVAL)
    face_oval_landmarks = [
        face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_FACE_OVAL
    ]

    # 제외할 부위 (눈, 입술 등)
    exclude_landmarks_dict = {
        'left_eye': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LEFT_EYE],
        'right_eye': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_RIGHT_EYE],
        'left_iris': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LEFT_IRIS],
        'right_iris': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_RIGHT_IRIS],
        'lips': [face_landmarks[idx[0]] for idx in mp.solutions.face_mesh.FACEMESH_LIPS]
    }

    # 얼굴 외곽 마스크 생성
    face_oval_points = np.array([
        (int(landmark.x * rgb_image.shape[1]), int(landmark.y * rgb_image.shape[0]))
        for landmark in face_oval_landmarks
    ], np.int32)
    face_mask = np.zeros(rgb_image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(face_mask, [face_oval_points], 255)

    # 제외할 영역을 마스크에서 제거
    for region, landmarks in exclude_landmarks_dict.items():
        points = np.array([
            (int(landmark.x * rgb_image.shape[1]), int(landmark.y * rgb_image.shape[0]))
            for landmark in landmarks
        ], np.int32)
        cv2.fillPoly(face_mask, [points], 0)  # 해당 영역을 0으로 설정하여 제외

    # 얼굴 외곽 마스크를 적용하여 얼굴 영역만 추출
    mask_rgb = cv2.merge([face_mask] * 3).astype(rgb_image.dtype)
    face_pixels = cv2.bitwise_and(rgb_image, mask_rgb)

    return face_pixels

# 얼굴 영역을 추출하고 화면에 출력
if detection_result.face_landmarks:
    face_landmarks = detection_result.face_landmarks[0]
    face_pixels = extract_face_pixels(rgb_image, face_landmarks)

    plt.imshow(cv2.cvtColor(face_pixels, cv2.COLOR_BGR2RGB))
    plt.title("Extracted Face Region")
    plt.show()
else:
    print("No face landmarks detected.")
