

import streamlit as st
from openai import OpenAI

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="AI Dessert Lab",
    page_icon="🍰",
    layout="wide"
)

# ==========================================
# 2. 디자인 CSS
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.stApp {
    background-color: #FFF9F7;
}

.main-title {
    text-align: center;
    font-family: 'Jua', sans-serif;
    font-size: 48px;
    color: #B76E79;
    padding-top: 15px;
}

.sub-title {
    text-align: center;
    color: #8D7777;
    font-size: 17px;
    margin-bottom: 30px;
}

.section-title {
    font-size: 23px;
    font-weight: 700;
    color: #9B6570;
    margin-top: 20px;
}

.result-card {
    background-color: #FFFFFF;
    border: 1px solid #F1D9D8;
    border-radius: 15px;
    padding: 22px;
    margin: 12px 0;
}

.result-name {
    color: #B76E79;
    font-size: 23px;
    font-weight: 700;
}

div.stButton > button {
    background-color: #D9949C;
    color: white;
    border-radius: 10px;
    border: none;
    height: 48px;
    font-weight: bold;
    width: 100%;
}

div.stButton > button:hover {
    background-color: #BD7882;
    color: white;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #F1D9D8;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. 제목
# ==========================================

st.markdown(
    '<div class="main-title">🍰 AI Dessert Lab</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'AI와 함께 세상에 하나뿐인 나만의 디저트를 개발해 보세요!'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 4. 재료 및 개발 조건 입력
# ==========================================

st.markdown(
    '<div class="section-title">🍓 01. 사용할 재료 선택</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

ingredients_list = [
    "딸기", "말차", "화이트초콜릿",
    "다크초콜릿", "밀크초콜릿", "바닐라",
    "레몬", "블루베리", "망고",
    "라즈베리", "생크림", "크림치즈",
    "그릭요거트", "우유", "캐러멜",
    "피스타치오", "흑임자", "고구마",
    "단호박", "바나나", "코코넛"
]

with col1:
    selected_ingredients = st.multiselect(
        "사용하고 싶은 재료를 선택하세요.",
        ingredients_list,
        default=["딸기", "말차", "화이트초콜릿"]
    )

with col2:
    extra_ingredients = st.text_input(
        "추가 재료 입력 (선택)",
        placeholder="예: 유자, 로즈마리, 얼그레이"
    )

st.markdown(
    '<div class="section-title">🧁 02. 디저트 종류 선택</div>',
    unsafe_allow_html=True
)

dessert_type = st.selectbox(
    "어떤 종류의 디저트를 개발할까요?",
    [
        "무스",
        "푸딩",
        "타르트",
        "케이크",
        "마카롱",
        "초콜릿 디저트",
        "젤리 및 판나코타",
        "아이스크림",
        "종류 상관없음"
    ]
)

st.markdown(
    '<div class="section-title">✨ 03. 개발 방향 선택</div>',
    unsafe_allow_html=True
)

development_style = st.selectbox(
    "어떤 콘셉트의 디저트를 만들까요?",
    [
        "독특하고 새로운 조합",
        "고급스럽고 세련된 디저트",
        "대중적으로 인기 있는 디저트",
        "계절 한정 디저트",
        "비주얼이 독창적인 디저트",
        "식감이 재미있는 디저트",
        "건강한 식재료를 활용한 디저트"
    ]
)

col3, col4 = st.columns(2)

with col3:
    sweetness = st.select_slider(
        "원하는 단맛 정도",
        options=["매우 약함", "약함", "보통", "강함", "매우 강함"],
        value="보통"
    )

with col4:
    difficulty = st.selectbox(
        "제조 난이도",
        ["쉬움", "보통", "어려움", "상관없음"]
    )


# ==========================================
# 5. AI 메뉴 개발 함수
# ==========================================

def generate_desserts(
    ingredients,
    dessert_type,
    style,
    sweetness,
    difficulty
):
    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    prompt = f"""
너는 전문 제과제빵사이자 디저트 메뉴 개발 전문가야.

사용자가 입력한 조건에 맞춰 독창적인 디저트 신메뉴
3가지를 개발해 줘.

[사용자 입력 조건]

사용 재료: {ingredients}
디저트 종류: {dessert_type}
개발 방향: {style}
단맛 정도: {sweetness}
제조 난이도: {difficulty}

[작성 조건]

1. 반드시 서로 다른 콘셉트의 디저트 3가지를 제안해.
2. 입력된 주요 재료를 적극적으로 활용해.
3. 단순히 재료를 섞는 것이 아니라 맛과 식감의 조화를 고려해.
4. 실제 제과제빵 기술을 바탕으로 제조 가능한 아이디어를 제시해.
5. 각 메뉴마다 다음 항목을 작성해.

- 메뉴 이름
- 메뉴 개발 콘셉트
- 사용 재료와 구성
- 메뉴의 특징
- 예상되는 맛
- 예상되는 식감
- 제조 과정에서 주의할 점
- 독창적인 차별화 요소

6. 마지막에는 세 가지 메뉴를 비교하고
가장 추천하는 메뉴 하나와 추천 이유를 설명해.
7. 전문적인 내용도 고등학생이 이해할 수 있게 설명해.
8. 식품 안전과 실제 제조 가능성을 고려해.
9. 검증되지 않은 보관 기간이나 건강 효능을 단정하지 마.

[출력 형식]

# 🍰 AI 신메뉴 개발 결과

## 01. 메뉴 이름
(메뉴 설명)

### 메뉴 특징
### 사용 재료와 구성
### 예상 맛
### 예상 식감
### 제조 시 주의점
### 차별화 요소

위 형식으로 3가지 메뉴를 작성해.

# 📊 메뉴 비교
표로 비교해 줘.

# 🏆 AI 최종 추천
가장 추천하는 메뉴와 이유를 설명해.

한국어로 작성해 줘.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


# ==========================================
# 6. AI 신메뉴 개발 버튼
# ==========================================

st.divider()

st.markdown(
    '<div class="section-title">🔬 04. AI 신메뉴 개발</div>',
    unsafe_allow_html=True
)

st.write(
    "선택한 재료와 조건을 바탕으로 AI가 새로운 디저트 3가지를 개발합니다."
)

if st.button("✨ AI 신메뉴 개발 시작하기"):

    ingredients = selected_ingredients.copy()

    if extra_ingredients.strip():
        ingredients.append(extra_ingredients.strip())

    if not ingredients:
        st.warning("재료를 한 가지 이상 선택해 주세요.")

    else:
        try:
            with st.spinner("🧁 AI 파티시에가 새로운 디저트를 개발하고 있어요..."):

                result = generate_desserts(
                    ingredients=ingredients,
                    dessert_type=dessert_type,
                    style=development_style,
                    sweetness=sweetness,
                    difficulty=difficulty
                )

                st.session_state["dessert_result"] = result

        except KeyError:
            st.error(
                "OpenAI API 키가 설정되지 않았어요. "
                "Streamlit Secrets에 API 키를 등록해 주세요."
            )

        except Exception as e:
            st.error(
                "메뉴 개발 중 오류가 발생했어요. "
                "API 키와 인터넷 연결, API 사용 가능 여부를 확인해 주세요."
            )
            st.caption(f"오류 정보: {str(e)}")


# ==========================================
# 7. AI 개발 결과 출력
# ==========================================

if "dessert_result" in st.session_state:

    st.divider()

    st.markdown(
        '<div class="section-title">🎂 AI 신메뉴 개발 결과</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        st.session_state["dessert_result"]
    )

    st.divider()

    st.success("신메뉴 개발이 완료되었습니다!")

    st.download_button(
        label="📥 개발 결과 다운로드",
        data=st.session_state["dessert_result"],
        file_name="AI_dessert_result.txt",
        mime="text/plain"
    )

    if st.button("🔄 다른 신메뉴 다시 개발하기"):
        del st.session_state["dessert_result"]
        st.rerun()


# ==========================================
# 8. 하단 안내
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#A58C8C; padding:15px;">
        🍓 AI Dessert Lab<br>
        나만의 디저트를 연구하고 개발하는 공간<br>
        <small>AI가 제안한 메뉴는 실제 제조 테스트를 거쳐야 합니다.</small>
    </div>
    """,
    unsafe_allow_html=True
)
