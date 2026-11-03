
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 분석")
st.write(
    "국가별 MBTI 비율과 MBTI 유형별 국가 순위를 "
    "확인할 수 있는 분석 서비스입니다."
)


# ==========================================
# 2. CSV 파일 경로
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DATA_FILE = PROJECT_DIR / "countriesMBTI_16types.csv"


# ==========================================
# 3. MBTI 유형
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

    required_columns = ["Country"] + MBTI_COLUMNS

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV에 필요한 열이 없습니다: "
            + ", ".join(missing_columns)
        )

    data = data[required_columns].copy()

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

    for col in MBTI_COLUMNS:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    if data[MBTI_COLUMNS].isna().any().any():
        raise ValueError("MBTI 비율 데이터에 오류가 있습니다.")

    if (data[MBTI_COLUMNS] < 0).any().any():
        raise ValueError("음수 비율이 포함되어 있습니다.")

    # 소수 형태를 백분율로 변환
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
# 7. 데이터 파일 확인
# ==========================================

if not DATA_FILE.exists():

    st.error(
        "CSV 파일을 찾을 수 없습니다.\n\n"
        f"확인한 경로: {DATA_FILE}"
    )

    st.stop()


# ==========================================
# 8. 데이터 불러오기
# ==========================================

try:

    df = load_data(str(DATA_FILE))

except Exception as error:

    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {error}"
    )

    st.stop()


# ==========================================
# 9. 국가별 MBTI 비율 분석
# ==========================================

st.header("📊 국가별 MBTI 비율")

st.write(
    "국가를 선택하면 해당 국가의 "
    "16가지 MBTI 비율을 확인할 수 있습니다."
)

selected_country = st.selectbox(
    "📍 국가 선택",
    options=df["Country"].tolist(),
    index=0,
    key="country_select"
)


# 선택한 국가 데이터
selected_row = df.loc[
    df["Country"] == selected_country
].iloc[0]


# MBTI 비율 정렬
chart_data = pd.DataFrame({

    "MBTI": MBTI_COLUMNS,

    "비율": [
        float(selected_row[mbti])
        for mbti in MBTI_COLUMNS
    ]

})

chart_data = (
    chart_data
    .sort_values(
        by="비율",
        ascending=False
    )
    .reset_index(drop=True)
)


# 1위 MBTI
top_mbti = chart_data.iloc[0]["MBTI"]
top_percentage = chart_data.iloc[0]["비율"]


# 그래프 색상
blue_colors = make_blue_gradient(
    len(chart_data) - 1
)

bar_colors = ["#E53935"] + blue_colors


# 주요 정보
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


# MBTI 그래프
st.subheader(
    f"📊 {selected_country}의 MBTI 비율"
)

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


st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


st.caption(
    "🔴 빨간색: 비율 1위 / 🔵 파란색: 나머지 유형"
)


# 상세 데이터
with st.expander("📋 MBTI 비율 상세 데이터"):

    display_data = chart_data.copy()

    display_data["비율"] = display_data[
        "비율"
    ].map(lambda x: f"{x:.2f}%")

    display_data.index = range(
        1,
        len(display_data) + 1
    )

    display_data.index.name = "순위"

    st.dataframe(
        display_data,
        use_container_width=True
    )


# ==========================================
# 10. MBTI별 국가 순위 분석
# ==========================================

st.divider()

st.header("🌎 MBTI별 국가 순위")

st.write(
    "MBTI 유형을 선택하면 해당 유형의 비율이 "
    "높은 국가부터 순위를 확인할 수 있습니다."
)


# MBTI 선택 메뉴
selected_mbti = st.selectbox(
    "🧭 MBTI 유형 선택",
    options=MBTI_COLUMNS,
    index=0,
    key="mbti_select"
)


# ==========================================
# 11. 선택한 MBTI의 국가별 비율 정렬
# ==========================================

ranking_data = df[
    ["Country", selected_mbti]
].copy()

ranking_data = ranking_data.rename(
    columns={
        "Country": "국가",
        selected_mbti: "비율"
    }
)

# 비율이 높은 국가부터 정렬
ranking_data = (
    ranking_data
    .sort_values(
        by=["비율", "국가"],
        ascending=[False, True]
    )
    .reset_index(drop=True)
)

# 국가 순위 추가
ranking_data.insert(
    0,
    "순위",
    range(1, len(ranking_data) + 1)
)


# ==========================================
# 12. 1위 국가 정보
# ==========================================

first_country = ranking_data.iloc[0]["국가"]

first_percentage = ranking_data.iloc[0]["비율"]


col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🏆 1위 국가",
        first_country
    )

with col2:

    st.metric(
        f"{selected_mbti} 비율",
        f"{first_percentage:.2f}%"
    )


# ==========================================
# 13. 국가 순위 그래프
# ==========================================

st.subheader(
    f"🏆 {selected_mbti} 국가별 순위 TOP 20"
)

# 상위 20개 국가만 그래프로 표시
top_20 = ranking_data.head(20).copy()

# 1위 빨간색, 나머지 파란색 그라데이션
ranking_colors = (
    ["#E53935"]
    + make_blue_gradient(len(top_20) - 1)
)


ranking_fig = go.Figure(

    data=[

        go.Bar(

            x=top_20["비율"],

            y=top_20["국가"],

            orientation="h",

            marker=dict(
                color=ranking_colors
            ),

            text=[
                f"{value:.2f}%"
                for value in top_20["비율"]
            ],

            textposition="outside",

            cliponaxis=False,

            hovertemplate=(
                "<b>%{y}</b><br>"
                "비율: %{x:.2f}%"
                "<extra></extra>"
            )

        )

    ]

)


ranking_max = float(
    top_20["비율"].max()
)

ranking_fig.update_layout(

    template="plotly_white",

    height=720,

    margin=dict(
        l=30,
        r=65,
        t=30,
        b=45
    ),

    xaxis=dict(
        title=f"{selected_mbti} 비율(%)",
        rangemode="tozero",
        range=[
            0,
            ranking_max * 1.2
            if ranking_max > 0 else 1
        ],
        ticksuffix="%",
        gridcolor="#E5E7EB"
    ),

    yaxis=dict(
        title="국가",
        categoryorder="array",
        categoryarray=top_20["국가"].tolist(),
        autorange="reversed"
    ),

    showlegend=False,

    bargap=0.3

)


st.plotly_chart(
    ranking_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


st.caption(
    "🔴 빨간색: 1위 국가 / 🔵 파란색: 2위~20위 국가"
)


# ==========================================
# 14. 전체 국가 순위표
# ==========================================

with st.expander(
    f"📋 {selected_mbti} 전체 국가 순위 보기 (1~{len(ranking_data)}위)"
):

    display_ranking = ranking_data.copy()

    display_ranking["비율"] = (
        display_ranking["비율"]
        .map(lambda x: f"{x:.2f}%")
    )

    st.dataframe(
        display_ranking,
        use_container_width=True,
        hide_index=True,
        height=500
    )


# ==========================================
# 15. 마무리 안내
# ==========================================

st.divider()

st.caption(
    "※ 모든 비율은 제공된 CSV 원본 데이터를 기준으로 합니다. "
    "국가별 조사 표본과 조사 방법이 확인되지 않으므로 "
    "실제 전체 인구의 MBTI 분포로 단정할 수 없습니다."
)
