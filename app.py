import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from openai import OpenAI

# 1. 페이지 기본 설정
st.set_page_config(page_title="Flavor Map Free AI", layout="wide")
st.title("Flavor Map: 지능형 주류 & 푸드 큐레이션 시스템 (최신 Llama 3.1 탑재)")
st.write("오픈소스 LLM 클라우드 API를 활용하여 비용이 전혀 들지 않는 하이브리드 추천 엔진입니다.")

# 데이터 로드
df_whiskey = pd.read_csv("whiskey_db.csv")
df_food = pd.read_csv("food_db.csv")
categories = ['smoky', 'sweet', 'fruity', 'body']

# 2. 사이드바: 제어 패널 구성
st.sidebar.title("제어 패널")

# Groq API 키 입력창
groq_api_key = st.sidebar.text_input(
    "Groq API Key를 입력하세요:", 
    type="password", 
    help="Groq Cloud에서 발급받은 gsk_... 형태의 무료 키를 입력하세요."
)

mode = st.sidebar.radio(
    "분석 모드를 선택하세요:", 
    ["기존 위스키 기반 추천", "내 입맛 맞춤 커스텀 추천", "오늘의 안주 맞춤 추천 (New)"]
)

# 3. 모드별 유저 취향 벡터(Taste Vector) 생성
if mode == "기존 위스키 기반 추천":
    user_choice = st.sidebar.selectbox("좋아하는 위스키를 골라보세요:", df_whiskey['name'].tolist())
    target_data = df_whiskey[df_whiskey['name'] == user_choice].iloc[0]
    user_profile = [target_data['smoky'], target_data['sweet'], target_data['fruity'], target_data['body']]
    label_name = user_choice
    context_text = f"유저가 평소에 [{user_choice}] 위스키를 아주 좋아합니다."

elif mode == "내 입맛 맞춤 커스텀 추천":
    st.sidebar.subheader("당신의 선호도를 조절해보세요 (1~5점)")
    u_smoky = st.sidebar.slider("스모키함 (피트 향)", 1, 5, 3)
    u_sweet = st.sidebar.slider("달콤함 (바닐라/카라멜)", 1, 5, 3)
    u_fruity = st.sidebar.slider("과일향 (상큼함/시트러스)", 1, 5, 3)
    u_body = st.sidebar.slider("바디감 (무게감)", 1, 5, 3)
    user_profile = [u_smoky, u_sweet, u_fruity, u_body]
    label_name = "내 커스텀 취향"
    context_text = f"유저가 직접 선호도를 선택했습니다. (스모키:{u_smoky}, 단맛:{u_sweet}, 과일향:{u_fruity}, 바디감:{u_body})"

else:
    food_choice = st.sidebar.selectbox("오늘 함께 먹을 안주를 골라보세요:", df_food['food_name'].tolist())
    target_food = df_food[df_food['food_name'] == food_choice].iloc[0]
    user_profile = [target_food['ideal_smoky'], target_food['ideal_sweet'], target_food['ideal_fruity'], target_food['ideal_body']]
    label_name = f"{food_choice}의 이상적 매칭"
    context_text = f"유저가 오늘 안주로 [{food_choice}]를 먹으려고 합니다."

# 4. [추천 알고리즘] 유클리드 거리 연산
df_whiskey['distance'] = (
    (df_whiskey['smoky'] - user_profile[0])**2 +
    (df_whiskey['sweet'] - user_profile[1])**2 +
    (df_whiskey['fruity'] - user_profile[2])**2 +
    (df_whiskey['body'] - user_profile[3])**2
)**0.5

if mode == "기존 위스키 기반 추천":
    recommendations = df_whiskey[df_whiskey['name'] != user_choice].sort_values(by='distance')
else:
    recommendations = df_whiskey.sort_values(by='distance')

recommended_whiskey = recommendations.iloc[0]

# 5. 메인 대시보드 화면 구성 (시각화)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("취향 대조 분석 맵 (Flavor Overlay)")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=user_profile, theta=categories, fill='toself', name=label_name, line_color='#1f77b4'))
    fig.add_trace(go.Scatterpolar(
        r=[recommended_whiskey['smoky'], recommended_whiskey['sweet'], recommended_whiskey['fruity'], recommended_whiskey['body']],
        theta=categories, fill='toself', name=f"추천: {recommended_whiskey['name']}", line_color='#ff7f0e'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("매칭 엔진 분석 결과")
    st.metric(label="최적 매칭 모델", value=recommended_whiskey['name'])
    st.metric(label="맛 거리지수 (Taste Distance)", value=f"{recommendations.iloc[0]['distance']:.3f}")
    
    st.divider()
    st.markdown("### Llama 3.1 오픈소스 AI 소믈리에의 페어링 가이드")
    
    if groq_api_key:
        try:
            with st.spinner("최신 라마 3.1 모델이 초고속으로 답변을 생성 중입니다..."):
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=groq_api_key
                )
                
                prompt = f"""
                당신은 세계 최고 권위의 위스키 소믈리에이자 푸드 페어링 전문가입니다.
                알고리즘의 분석 결과, {context_text} 유저에게 최적의 위스키로 [{recommended_whiskey['name']}]이 추천되었습니다.
                
                이 추천 결과가 왜 좋은 조합인지, 유저의 상황과 엮어서 친절하고 고급스러운 어조로 설명해주세요.
                
                [조건]
                1. 철저히 친절한 전문가의 어조(해요체)로 작성할 것.
                2. 한글 기준 3문장 이내로 짧고 명쾌하게 작성할 것.
                3. 위스키의 맛 특징(스모키:{recommended_whiskey['smoky']}, 단맛:{recommended_whiskey['sweet']})을 자연스럽게 언급할 것.
                """
                
                # [수정된 부분] 지원이 종료된 구형 모델 대신 최신 'llama-3.1-8b-instant'를 사용합니다.
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                
                ai_note = response.choices[0].message.content
                st.info(ai_note)
                
        except Exception as e:
            st.error(f"AI 호출 중 오류가 발생했습니다. 키를 다시 확인해주세요. (에러내용: {e})")
    else:
        st.warning("왼쪽 제어 패널에 무료로 발급받은 'Groq API Key'를 입력하시면, 돈 한 푼 안 드는 오픈소스 Llama 3.1 소믈리에 가이드가 활성화됩니다!")