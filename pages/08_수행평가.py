
import streamlit as st
import pandas as pd
from pathlib import Path
import html

# =====================================
# 1. 페이지 기본 설정
# =====================================

st.set_page_config(
    page_title="우리 동네 디저트 레시피",
    page_icon="🍰",
    layout="wide"
)

# =====================================
# 2. 디자인
# =====================================

st.markdown("""
<style>
.stApp {
    background-color: #FFF9F5;
}

h1, h2, h3 {
    color: #795548;
}

.recipe-card {
    background-color: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #F0DED2;
    margin-bottom: 15px;
    line-height: 1.8;
}

.ingredient {
    background-color: #FFF0E5;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    line-height: 1.8;
}

div.stButton > button {
    background-color: #B98770;
    color: white;
    border-radius: 10px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# 3. 제목
# =====================================

st.title("🍰 우리 동네 디저트 레시피")

st.write(
    "다양한 디저트와 음료를 선택하고 "
    "필요한 재료와 조리 방법을 확인해 보세요!"
)

st.divider()

# =====================================
# 4. CSV 파일 경로 설정
# =====================================

BASE_DIR = Path(__file__).resolve().parent

possible_paths = [
    BASE_DIR / "data" / "tea_dessert.csv",
    BASE_DIR.parent / "data" / "tea_dessert.csv",
    BASE_DIR / "tea_dessert.csv",
    BASE_DIR.parent / "tea_dessert.csv"
]

DATA_PATH = next(
    (path for path in possible_paths if path.exists()),
    None
)

if DATA_PATH is None:
    st.error("CSV 파일을 찾을 수 없습니다.")

    st.write("확인한 파일 경로:")

    for path in possible_paths:
        st.write(str(path))

    st.info(
        "tea_dessert.csv 파일을 프로젝트 최상위 폴더의 "
        "data 폴더 안에 넣어 주세요."
    )

    st.stop()

# =====================================
# 5. CSV 데이터 불러오기
# =====================================

@st.cache_data
def load_data(file_path):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding
            )

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")

try:
    df = load_data(str(DATA_PATH))

except Exception as e:
    st.error(f"CSV 파일을 불러오지 못했습니다: {e}")
    st.stop()

# =====================================
# 6. 열 이름 정리
# =====================================

# 열 이름 앞뒤 공백 제거
df.columns = df.columns.astype(str).str.strip()

required_columns = [
    "요리명",
    "주재료",
    "부재료",
    "조리법",
    "상세설명"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )

    st.write("현재 CSV 파일의 열 이름:")
    st.write(list(df.columns))

    st.stop()

# =====================================
# 7. 데이터 정리
# =====================================

df = df.copy()

for col in required_columns:
    df[col] = (
        df[col]
        .fillna("")
        .astype(str)
        .str.strip()
    )

df = df[df["요리명"] != ""]

df = df.drop_duplicates(
    subset=["요리명"]
).reset_index(drop=True)

# =====================================
# 8. 메뉴 자동 분류
# =====================================

def classify_menu(name):

    name = str(name)

    dessert_keywords = [
        "케이크", "쿠키", "푸딩", "떡",
        "아이스크림", "빙수", "타르트",
        "파이", "과자", "초콜릿", "디저트",
        "양갱", "젤리", "머핀", "팬케이크",
        "와플", "마카롱", "스콘", "정과",
        "다식", "강정", "한과", "과일"
    ]

    drink_keywords = [
        "차", "음료", "주스", "에이드",
        "라떼", "커피", "스무디",
        "식혜", "수정과", "청"
    ]

    if any(word in name for word in dessert_keywords):
        return "디저트"

    elif any(word in name for word in drink_keywords):
        return "음료"

    else:
        return "기타 음식"


df["분류"] = df["요리명"].apply(classify_menu)

# =====================================
# 9. 메뉴 종류 선택
# =====================================

st.subheader("🍮 메뉴 선택")

menu_type = st.radio(
    "메뉴 종류를 선택하세요.",
    ["전체", "디저트", "음료", "기타 음식"],
    horizontal=True
)

if menu_type == "전체":
    filtered_df = df.copy()

else:
    filtered_df = df[
        df["분류"] == menu_type
    ].copy()

if filtered_df.empty:
    st.warning("해당 종류의 메뉴가 없습니다.")
    st.stop()

# =====================================
# 10. 메뉴 선택창
# =====================================

menu_list = sorted(
    filtered_df["요리명"].unique()
)

selected_menu = st.selectbox(
    "레시피를 확인할 메뉴를 선택하세요.",
    menu_list
)

selected_data = filtered_df[
    filtered_df["요리명"] == selected_menu
].iloc[0]

# =====================================
# 11. 선택한 메뉴 정보
# =====================================

st.divider()

st.title(f"🍮 {selected_data['요리명']}")

st.caption(
    f"메뉴 분류: {selected_data['분류']}"
)

# =====================================
# 12. 재료 정보
# =====================================

st.subheader("🧺 필요한 재료")

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 주재료")

    main_ingredient = (
        html.escape(selected_data["주재료"])
        if selected_data["주재료"]
        else "등록된 정보가 없습니다."
    )

    st.markdown(
        f'<div class="ingredient">{main_ingredient}</div>',
        unsafe_allow_html=True
    )

with col2:

    st.markdown("### 부재료")

    sub_ingredient = (
        html.escape(selected_data["부재료"])
        if selected_data["부재료"]
        else "등록된 정보가 없습니다."
    )

    st.markdown(
        f'<div class="ingredient">{sub_ingredient}</div>',
        unsafe_allow_html=True
    )

# =====================================
# 13. 조리 방법
# =====================================

st.subheader("👩‍🍳 조리 방법")

recipe = selected_data["조리법"]

if recipe:

    safe_recipe = html.escape(recipe).replace(
        "\n", "<br>"
    )

    st.markdown(
        f'<div class="recipe-card">{safe_recipe}</div>',
        unsafe_allow_html=True
    )

else:

    st.info("등록된 조리 방법이 없습니다.")

# =====================================
# 14. 상세 설명
# =====================================

st.subheader("📖 메뉴 상세 설명")

description = selected_data["상세설명"]

if description:
    st.write(description)

else:
    st.info("등록된 상세 설명이 없습니다.")

# =====================================
# 15. 데이터 기준일자
# =====================================

if "데이터기준일자" in df.columns:

    st.caption(
        "데이터 기준일자: "
        + str(selected_data["데이터기준일자"])
    )

# =====================================
# 16. 데이터 통계
# =====================================

st.divider()

st.subheader("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 메뉴 수",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "선택 종류 메뉴 수",
        f"{len(filtered_df):,}개"
    )

with col3:
    st.metric(
        "현재 선택 메뉴",
        selected_data["분류"]
    )

# =====================================
# 17. 하단 안내
# =====================================

st.divider()

st.caption(
    "※ 제공된 CSV 데이터에 수록된 정보를 바탕으로 구성한 레시피입니다."
)

st.caption(
    "데이터에 따라 일부 메뉴의 재료 또는 조리 방법이 없을 수 있습니다."
)
