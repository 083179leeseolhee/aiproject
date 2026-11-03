
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 비율 분석")
st.write(
    "국가를 선택하면 해당 국가의 "
    "16가지 MBTI 유형별 비율을 확인할 수 있어요."
)


# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

# 현재 파일: 프로젝트/pages/mbti.py
# CSV 파일: 프로젝트/countriesMBTI_16types.csv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DATA_FILE = PROJECT_DIR / "countriesMBTI_16types.csv"


# ==========================================
# 3. MBTI 유형 설정
# ==========================================

MBTI_COLUMNS = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


# ==========================================
# 4. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(file_path):

    data = pd.read_csv(
        file_path,
        encoding="utf-8-sig"
    )

    # 필요한 열 확인
    required_columns = ["Country"] + MBTI_COLUMNS

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV 파일에 필요한 열이 없습니다: "
            + ", ".join(missing_columns)
        )

    data = data[required_columns].copy()

    # 국가 이름 정리
    data["Country"] = (
        data["Country"]
        .astype("string")
        .str.strip()
    )

    if data["Country"].isna().any():
        raise ValueError("국가 이름이 비어 있습니다.")

    if (data["Country"] == "").any():
        raise ValueError("빈 국가 이름이 있습니다.")

    if data["Country"].duplicated().any():
        raise ValueError("중복된 국가가 있습니다.")

    # MBTI 데이터를 숫자로 변환
    for col in MBTI_COLUMNS:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    if data[MBTI_COLUMNS].isna().any().any():
        raise ValueError(
            "MBTI 비율에 숫자가 아닌 값이나 빈 값이 있습니다."
        )

    if (data[MBTI_COLUMNS] < 0).any().any():
        raise ValueError("음수 비율이 포함되어 있습니다.")

    # 소수 형태의 비율을 백분율로 변환
    if data[MBTI_COLUMNS].to_numpy().max() <= 1.5:
        data[MBTI_COLUMNS] = (
            data[MBTI_COLUMNS] * 100
        )

    return (
        data
        .sort_values("Country")
        .reset_index(drop=True)
    )


# ==========================================
# 5. 색상 변환 함수
# ==========================================

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):

    return "#{:02X}{:02X}{:02X}".format(*rgb)


# ==========================================
# 6. 파란색 그라데이션 생성
# ==========================================

def make_blue_gradient(count):

    start = hex_to_rgb("#1D4ED8")
    end = hex_to_rgb("#DBEAFE")

    if count <= 1:
        return [rgb_to_hex(start)]

    colors = []

    for i in range(count):

        ratio = i / (count - 1)

        rgb = tuple(
            round(
                start[channel]
                + (end[channel] - start[channel]) * ratio
            )
            for channel in range(3)
        )

        colors.append(rgb_to_hex(rgb))

    return colors


# ==========================================
# 7. CSV 파일 존재 여부 확인
# ==========================================

if not DATA_FILE.exists():

    st.error(
        "CSV 파일을 찾을 수 없습니다.\n\n"
        f"확인한 경로: {DATA_FILE}"
    )

    st.stop()


# ==========================================
# 8. 데이터 불러오기 및 오류 확인
# ==========================================

try:

    df = load_data(str(DATA_FILE))

except Exception as error:

    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {error}"
    )

    st.stop()


# ==========================================
# 9. 국가 선택 메뉴
# ==========================================

country_list = df["Country"].tolist()

selected_country = st.selectbox(
    "📍 국가 선택",
    options=country_list,
    index=0,
    help="분석하고 싶은 국가를 선택하세요."
)


# ==========================================
# 10. 선택한 국가의 데이터 가져오기
# ==========================================

selected_row = df.loc[
    df["Country"] == selected_country
].iloc[0]


# ==========================================
# 11. MBTI 비율 정렬
# ==========================================

chart_data = pd.DataFrame({

    "MBTI": MBTI_COLUMNS,

    "비율": [
        float(selected_row[mbti])
        for mbti in MBTI_COLUMNS
    ]

})

# 높은 비율부터 낮은 비율 순서로 정렬
chart_data = (
    chart_data
    .sort_values(
        by="비율",
        ascending=False
    )
    .reset_index(drop=True)
)


# ==========================================
# 12. 1위 MBTI 확인
# ==========================================

top_mbti = chart_data.iloc[0]["MBTI"]

top_percentage = chart_data.iloc[0]["비율"]


# ==========================================
# 13. 그래프 색상 설정
# ==========================================

# 1위는 빨간색
# 나머지는 진한 파랑에서 연한 파랑으로

blue_colors = make_blue_gradient(
    len(chart_data) - 1
)

bar_colors = (
    ["#E53935"] + blue_colors
)


# ==========================================
# 14. 주요 정보 표시
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "선택한 국가",
        selected_country
    )

with col2:

    st.metric(
        "🏆 비율 1위 MBTI",
        top_mbti,
        f"{top_percentage:.2f}%"
    )


# ==========================================
# 15. 그래프 제목
# ==========================================

st.subheader(
    f"📊 {selected_country}의 MBTI 비율"
)


# ==========================================
# 16. 막대그래프 생성
# ==========================================

fig = go.Figure(

    data=[

        go.Bar(

            x=chart_data["MBTI"],

            y=chart_data["비율"],

            marker=dict(
                color=bar_colors
            ),

            text=[
                f"{value:.2f}%"
                for value in chart_data["비율"]
            ],

            textposition="outside",

            cliponaxis=False,

            hovertemplate=(
                "<b>%{x}</b><br>"
                "비율: %{y:.2f}%"
                "<extra></extra>"
            )

        )

    ]

)


# ==========================================
# 17. 그래프 디자인
# ==========================================

max_percentage = float(
    chart_data["비율"].max()
)

fig.update_layout(

    template="plotly_white",

    height=560,

    margin=dict(
        l=35,
        r=25,
        t=35,
        b=45
    ),

    xaxis=dict(

        title="MBTI 유형",

        categoryorder="array",

        categoryarray=chart_data["MBTI"].tolist(),

        tickfont=dict(size=12)

    ),

    yaxis=dict(

        title="비율(%)",

        rangemode="tozero",

        range=[
            0,
            max_percentage * 1.18
            if max_percentage > 0 else 1
        ],

        ticksuffix="%",

        gridcolor="#E5E7EB"

    ),

    showlegend=False,

    bargap=0.28

)


# ==========================================
# 18. Streamlit 그래프 출력
# ==========================================

st.plotly_chart(

    fig,

    use_container_width=True,

    config={
        "displayModeBar": False
    }

)


# ==========================================
# 19. 그래프 설명
# ==========================================

st.caption(
    "🔴 빨간색: 해당 국가의 MBTI 비율 1위"
)

st.caption(
    "🔵 파란색: 2위부터 16위까지 "
    "진한 파랑에서 연한 파랑 순서"
)

st.caption(
    "※ 원본 데이터의 반올림 등으로 "
    "16개 유형의 합계가 정확히 100%가 아닐 수 있습니다."
)


# ==========================================
# 20. 상세 데이터 표
# ==========================================

with st.expander("📋 MBTI 비율 상세 데이터 보기"):

    display_data = chart_data.copy()

    display_data["비율"] = display_data[
        "비율"
    ].map(
        lambda x: f"{x:.2f}%"
    )

    display_data.index = range(
        1,
        len(display_data) + 1
    )

    display_data.index.name = "순위"

    st.dataframe(
        display_data,
        use_container_width=True
    )
