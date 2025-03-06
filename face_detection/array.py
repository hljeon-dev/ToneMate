import pandas as pd

# CSV 파일 로드
file_path = "./data/analyzed_results.csv"  # 파일 경로 수정
df = pd.read_csv(file_path)


# 'Analysis Result' 열 가공 함수
def process_analysis_result(result):
    # 바깥쪽 괄호 제거
    cleaned_result = result.strip("()")

    # "array" 기준으로 분리 후 각 RGB 값 추출
    components = cleaned_result.split("array")

    # 각 RGB 값 추출 및 클린업
    rgb_values = [comp.strip(" ,[]()") for comp in components if comp.strip()]

    # 필요한 값들만 추출 (순서대로 눈, 눈썹, 입술, 피부)
    return {
        "Eye RGB": rgb_values[0] if len(rgb_values) > 0 else None,
        "Eyebrow RGB": rgb_values[1] if len(rgb_values) > 1 else None,
        "Lip RGB": rgb_values[2] if len(rgb_values) > 2 else None,
        "Skin RGB": rgb_values[3] if len(rgb_values) > 3 else None,
    }


# 'Analysis Result' 열 가공
processed_results = df["Analysis Result"].apply(process_analysis_result)

# 가공된 데이터프레임 확장
processed_df = processed_results.apply(pd.Series)

# 기존 데이터프레임과 병합
final_df = pd.concat([df.drop(columns=["Analysis Result"]), processed_df], axis=1)

# 최종 데이터프레임 확인
print(final_df)

# 결과를 CSV로 저장
output_path = "data/processed_results.csv"  # 저장 경로
final_df.to_csv(output_path, index=False)
print(f"Processed results saved to {output_path}")
