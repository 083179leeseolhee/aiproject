
import streamlit as st
import pandas as pd
from pathlib import Path
import html

# ---------------------------------
# 1. 기본 페이지 설정
# ---------------------------------

st.set_page_config(
    page_title="우리 동네 디저트 레시피",
    page_icon="🍰",
    layout="wide"
)

# ---------------------------------
# 2. 디자인
# ---------------------------------

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
}

.ingredient {
    background-color: #FFF0E5;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}

div.stButton > button {
    background-color: #B98770;
    color: white;
    border-radius: 10px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# 3. 제목
# ---------------------------------

st.title("🍰 우리 동네 디저트 레시피")
st.write("다양한 디저트와 음료를 검색하고 재료 및 조리 방법을 확인해 보세요!")
st.divider()

# ---------------------------------
# 4. CSV 파일 경로 찾기
# ---------------------------------

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
    st.write("다음 경로를 확인했지만 파일이 없습니다.")

    for path in possible_paths:
        st.write(str(path))

    st.info(
        "tea_dessert.csv 파일을 프로젝트 최상위 폴더의 "
        "data 폴더 안에 넣어 주세요."
    )
    st.stop()

# ---------------------------------
# 5. CSV 불러오기
# ---------------------------------

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
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            return data

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

try:
    df = load_data(str(DATA_PATH))

except Exception as e:
    st.error(f"CSV 파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ---------------------------------
# 6. 데이터 정리
# ---------------------------------

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
    st.write("현재 CSV 파일의 열 이름:", list(df.columns))
    st.stop()

df = df.copy()

for col in required_columns:
    df[col] = df[col].fillna("").astype(str).str.strip()

df = df[df["요리명"] != ""]
df = df.drop_duplicates(subset=["요리명"])

# ---------------------------------
# 7. 디저트 / 음료 / 기타 음식 분류
# ---------------------------------

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
        "라떼", "커피", "스무디", "식혜",
        "수정과", "청", "차류"
    ]

    if any(keyword in name for keyword in dessert_keywords):
        return "디저트"

    elif any(keyword in name for keyword in drink_keywords):
        return "음료"

    else:
        return "기타 음식"


df["분류"] = df["요리명"].apply(classify_menu)

# ---------------------------------
# 8. 메뉴 선택
# ---------------------------------

st.subheader("🔎 원하는 메뉴 찾기")

menu_type = st.radio(
    "메뉴 종류를 선택하세요.",
    ["전체", "디저트", "음료", "기타 음식"],
    horizontal=True
)

if menu_type == "전체":
    filtered_df = df.copy()
else:
    filtered_df = df[df["분류"] == menu_type].copy()

search_word = st.text_input(
    "메뉴 이름 검색",
    placeholder="예: 녹차, 케이크, 쿠키..."
)

if search_word:
    filtered_df = filtered_df[
        filtered_df["요리명"].str.contains(
            search_word,
            case=False,
            na=False
        )
    ]

if filtered_df.empty:
    st.warning("검색 결과가 없습니다. 다른 메뉴를 검색해 주세요.")
    st.stop()

# ---------------------------------
# 9. 메뉴 선택창
# ---------------------------------

menu_list = sorted(filtered_df["요리명"].unique())

selected_menu = st.selectbox(
    "레시피를 확인할 메뉴를 선택하세요.",
    menu_list
)

selected_data = filtered_df[
    filtered_df["요리명"] == selected_menu
].iloc[0]

# ---------------------------------
# 10. 선택한 메뉴 정보
# ---------------------------------

st.divider()

st.title(f"🍮 {selected_data['요리명']}")

st.caption(f"메뉴 분류: {selected_data['분류']}")

# ---------------------------------
# 11. 재료 정보
# ---------------------------------

st.subheader("🧺 필요한 재료")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 주재료")
    st.markdown(
        f'<div class="ingredient">'
        f'{html.escape(selected_data["주재료"]) or "등록된 정보가 없습니다."}'
        f'</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown("### 부재료")
    st.markdown(
        f'<div class="ingredient">'
        f'{html.escape(selected_data["부재료"]) or "등록된 정보가 없습니다."}'
        f'</div>',
        unsafe_allow_html=True
    )

# ---------------------------------
# 12. 조리 방법
# ---------------------------------

st.subheader("👩‍🍳 조리 방법")

recipe = selected_data["조리법"]

if recipe:
    st.markdown(
        f'<div class="recipe-card">'
        f'{html.escape(recipe).replace(chr(10), "<br>")}'
        f'</div>',
        unsafe_allow_html=True
    )
else:
    st.info("등록된 조리 방법이 없습니다.")

# ---------------------------------
# 13. 상세 설명
# ---------------------------------

st.subheader("📖 메뉴 상세 설명")

description = selected_data["상세설명"]

if description:
    st.write(description)
else:
    st.info("등록된 상세 설명이 없습니다.")

# ---------------------------------
# 14. 데이터 정보
# ---------------------------------

st.divider()

st.subheader("📊 데이터 정보")

col1, col2 = st.columns(2)

with col1:
    st.metric("전체 데이터 수", f"{len(df):,}개")

with col2:
    st.metric("검색된 메뉴 수", f"{len(filtered_df):,}개")

if "기준일자" in df.columns:
    st.caption(f"데이터 기준일자: {selected_data.get('기준일자', '정보 없음')}")

st.caption("※ 제공된 CSV 데이터에 수록된 정보를 바탕으로 구성한 레시피입니다.")
