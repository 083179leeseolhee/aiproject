
import streamlit as st
import pandas as pd
import re
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="TEA & DESSERT",
    page_icon="🍵",
    layout="wide"
)

# ==========================================
# 2. 디자인
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #FAF8F3;
}

.main-title {
    text-align: center;
    color: #536B45;
    font-size: 42px;
    font-weight: 800;
    padding-top: 15px;
}

.sub-title {
    text-align: center;
    color: #888888;
    font-size: 16px;
    margin-bottom: 30px;
}

.section-title {
    color: #536B45;
    font-size: 23px;
    font-weight: 700;
    margin-top: 20px;
}

div[data-testid="stSelectbox"] {
    background-color: white;
    border-radius: 10px;
}

div.stButton > button {
    background-color: #6D805A;
    color: white;
    border-radius: 10px;
    border: none;
}

div.stButton > button:hover {
    background-color: #526542;
    color: white;
}

.recipe-box {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E7E2D8;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. CSV 파일 불러오기
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "tea_dessert.csv"

# 인코딩 자동 확인
@st.cache_data
def load_data():

    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                DATA_PATH,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    else:
        raise ValueError("CSV 파일 인코딩을 확인해주세요.")

    # 열 이름 공백 제거
    data.columns = data.columns.str.strip()

    # 필요한 열 확인
    required_columns = [
        "요리명",
        "주재료",
        "부재료",
        "조리법",
        "상세설명"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{col}' 열이 없습니다."
            )

    # 빈 데이터 처리
    data = data.fillna("")

    # 요리명 공백 제거
    data["요리명"] = data["요리명"].astype(str).str.strip()

    # 요리명이 없는 행 제거
    data = data[data["요리명"] != ""]

    # 중복 메뉴 제거
    data = data.drop_duplicates(
        subset=["요리명"],
        keep="first"
    )

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.info(
        "data 폴더 안에 tea_dessert.csv 파일이 있는지 확인해주세요."
    )
    st.stop()


# ==========================================
# 4. 메뉴 종류 자동 분류
# ==========================================

dessert_keywords = [
    "케이크", "마카롱", "아포가토", "푸딩",
    "아이스크림", "쿠키", "타르트", "파이",
    "빙수", "초콜릿", "가나슈", "브라우니",
    "무스", "젤리", "양갱", "와플",
    "팬케이크", "크레이프", "티라미수",
    "머핀", "스콘", "디저트", "다쿠아즈",
    "슈", "에클레어", "파르페", "찹쌀케이크",
    "생크림", "과일청"
]

drink_keywords = [
    "라떼", "에이드", "스무디", "밀크티",
    "아이스티", "차 음료", "주스", "음료",
    "차"
]

# 일반 음식에 해당하는 단어
food_keywords = [
    "삼겹살", "불고기", "찌개", "볶음밥",
    "비빔밥", "전골", "국수", "조림",
    "구이", "무침", "탕", "전"
]


def classify_menu(name):

    name = str(name)

    # 일반 음식 우선 분류
    if any(word in name for word in food_keywords):
        return "기타 음식"

    # 디저트 분류
    if any(word in name for word in dessert_keywords):
        return "디저트"

    # 음료 분류
    if any(word in name for word in drink_keywords):
        return "음료"

    return "기타 음식"


df["메뉴종류"] = df["요리명"].apply(classify_menu)


# ==========================================
# 5. 상단 제목
# ==========================================

st.markdown(
    '<div class="main-title">🍵 TEA & DESSERT</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '차와 디저트의 다양한 레시피를 만나보세요.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 6. 데이터 요약
# ==========================================

dessert_count = len(
    df[df["메뉴종류"] == "디저트"]
)

drink_count = len(
    df[df["메뉴종류"] == "음료"]
)

col1, col2, col3 = st.columns(3)

col1.metric("전체 메뉴", f"{len(df)}개")
col2.metric("디저트", f"{dessert_count}개")
col3.metric("음료", f"{drink_count}개")


# ==========================================
# 7. 메뉴 검색 및 선택
# ==========================================

st.markdown(
    '<div class="section-title">🔎 메뉴 검색</div>',
    unsafe_allow_html=True
)

category = st.radio(
    "메뉴 종류",
    ["디저트", "음료", "전체 음식"],
    horizontal=True
)

if category == "전체 음식":
    menu_df = df.copy()

else:
    menu_df = df[
        df["메뉴종류"] == category
    ].copy()


search = st.text_input(
    "메뉴 이름 검색",
    placeholder="예: 녹차케이크, 마카롱, 푸딩"
)

if search:
    menu_df = menu_df[
        menu_df["요리명"].str.contains(
            search,
            case=False,
            na=False
        )
    ]


if menu_df.empty:

    st.warning("검색 결과가 없습니다.")

    st.stop()


selected_menu = st.selectbox(
    "원하는 메뉴를 선택하세요.",
    menu_df["요리명"].tolist()
)


# ==========================================
# 8. 선택한 메뉴 데이터 불러오기
# ==========================================

recipe = menu_df[
    menu_df["요리명"] == selected_menu
].iloc[0]


st.divider()


# ==========================================
# 9. 메뉴 이름 표시
# ==========================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        background-color:#E9EDE2;
        padding:25px;
        border-radius:15px;
        margin-bottom:20px;
    ">
        <h1 style="color:#536B45;">
            {recipe['요리명']}
        </h1>
        <p style="color:#777777;">
            {recipe['메뉴종류']} 레시피
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 10. 재료 정보
# ==========================================

st.markdown(
    '<div class="section-title">🥣 재료 준비</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 주재료")

    if recipe["주재료"]:
        st.info(recipe["주재료"])
    else:
        st.write("등록된 주재료가 없습니다.")


with col2:

    st.markdown("### 부재료")

    if recipe["부재료"]:
        st.info(recipe["부재료"])
    else:
        st.write("등록된 부재료가 없습니다.")


# ==========================================
# 11. 제조방법
# ==========================================

st.divider()

st.markdown(
    '<div class="section-title">👩‍🍳 제조 방법</div>',
    unsafe_allow_html=True
)

method = str(recipe["조리법"]).strip()

if method:

    # ① ② ③ 등의 번호를 기준으로 단계 분리
    pattern = r'(?=[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳])'

    steps = re.split(pattern, method)

    steps = [
        step.strip()
        for step in steps
        if step.strip()
    ]

    if len(steps) > 1:

        for i, step in enumerate(steps, 1):

            st.markdown(
                f"""
                <div style="
                    background-color:white;
                    border:1px solid #E7E2D8;
                    border-radius:12px;
                    padding:17px;
                    margin-bottom:10px;
                    line-height:1.8;
                ">
                    <b style="color:#536B45;">
                        STEP {i}
                    </b>
                    <br>
                    {step}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.write(method)

else:

    st.warning("등록된 제조방법이 없습니다.")


# ==========================================
# 12. 상세 설명
# ==========================================

if recipe["상세설명"]:

    st.divider()

    st.markdown(
        '<div class="section-title">💡 조리 팁 및 상세 설명</div>',
        unsafe_allow_html=True
    )

    st.success(recipe["상세설명"])


# ==========================================
# 13. 데이터 출처
# ==========================================

st.divider()

with st.expander("📚 데이터 출처 및 정보"):

    st.write(
        "데이터명: 보성군 차 음식 및 디저트 정보"
    )

    st.write(
        "데이터 기준일자: 2022-10-30"
    )

    st.write(
        "데이터 항목: 요리명, 주재료, 부재료, "
        "조리법, 상세설명"
    )

    st.caption(
        "본 사이트는 제공된 CSV 데이터를 활용하여 "
        "메뉴별 레시피 정보를 제공합니다."
    )


st.markdown(
    """
    <div style="
        text-align:center;
        color:#999999;
        padding:25px;
        font-size:13px;
    ">
        TEA & DESSERT | Recipe Archive
    </div>
    """,
    unsafe_allow_html=True
)
