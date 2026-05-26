import pandas as pd

# 1. 위스키 데이터베이스 파일 읽어오기
df = pd.read_csv("whiskey_db.csv")

# 2. 유저가 좋아하는 위스키 선택 (이름을 바꾸면 추천도 바뀝니다!)
user_choice = "Lagavulin 16"

# 유저가 고른 위스키의 맛 데이터만 쏙 빼오기
target = df[df['name'] == user_choice].iloc[0]

# 3. [AI 핵심 로직] 모든 위스키와 내가 고른 위스키 사이의 맛 거리 구하기
# 맛 점수 차이를 제곱해서 모두 더한 뒤, 루트를 씌우는 수학 공식(유클리드 거리)입니다.
df['distance'] = (
    (df['smoky'] - target['smoky'])**2 +
    (df['sweet'] - target['sweet'])**2 +
    (df['fruity'] - target['fruity'])**2 +
    (df['body'] - target['body'])**2
)**0.5

# 4. 추천 결과 도출
# 거리가 0인 건 '자기 자신'이므로 제외하고, 거리가 가장 가까운(숫자가 작은) 순서대로 정렬합니다.
recommendations = df[df['name'] != user_choice].sort_values(by='distance')

# 5. 결과 화면 출력
print(f"\n[{user_choice}]를 좋아하는 당신을 위한 추천 알고리즘 가동 🔥")
print(f"-> 당신이 다음에 마셔봐야 할 가장 비슷한 위스키는 바로:")
print(f"{recommendations.iloc[0]['name']} ✨ (맛 거리 차이: {recommendations.iloc[0]['distance']:.2f})")