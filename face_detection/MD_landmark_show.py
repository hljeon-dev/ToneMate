from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import matplotlib.pyplot as plt
import cv2

# 화이트 밸런스 조정 함수
def load_and_prepare_image_with_manual_white_balance(img):
    # 각 채널의 평균 계산
    avg_r = np.mean(img[:, :, 0])
    avg_g = np.mean(img[:, :, 1])
    avg_b = np.mean(img[:, :, 2])

    # 목표 평균을 각 채널 평균의 중간값으로 설정
    avg_gray = 128
    scale_r = avg_gray / avg_r
    scale_g = avg_gray / avg_g
    scale_b = avg_gray / avg_b

    # 각 채널에 스케일 적용
    balanced_image = img.copy()
    balanced_image[:, :, 0] = np.clip(balanced_image[:, :, 0] * scale_r, 0, 255)
    balanced_image[:, :, 1] = np.clip(balanced_image[:, :, 1] * scale_g, 0, 255)
    balanced_image[:, :, 2] = np.clip(balanced_image[:, :, 2] * scale_b, 0, 255)

    return balanced_image.astype(np.uint8)

# 랜드마크를 이미지에 그리는 함수
def draw_landmarks_on_image(rgb_image, detection_result):
    face_landmarks_list = detection_result.face_landmarks
    annotated_image = np.copy(rgb_image)

    for idx in range(len(face_landmarks_list)):
        face_landmarks = face_landmarks_list[idx]
        
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        face_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
        ])

        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())
        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_contours_style())
        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_iris_connections_style())

    return annotated_image

# 이미지 로드 및 화이트 밸런스 적용
img_path = 'data/test.png'  # 이미지 경로를 사용자 이미지 경로로 변경하세요.
img = cv2.imread(img_path)

if img is not None:
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    balanced_image = load_and_prepare_image_with_manual_white_balance(rgb_image)

    # Mediapipe FaceLandmarker 설정
    base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
    options = vision.FaceLandmarkerOptions(base_options=base_options,
                                           output_face_blendshapes=True,
                                           output_facial_transformation_matrixes=True,
                                           num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)

    # Mediapipe 이미지 생성 및 처리
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=balanced_image)
    detection_result = detector.detect(mp_image)
    annotated_image = draw_landmarks_on_image(balanced_image, detection_result)

    # 결과 이미지 표시
    plt.imshow(balanced_image)
    plt.axis('off')
    plt.show()
else:
    print("Error: Image not found. Please check the path.")
