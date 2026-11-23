
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="대한민국 카페 분석소",
    page_icon="☕",
    layout="wide"
)

st.title("☕ 대한민국 카페 분석소")
st.caption("전국 카페 점포 현황 및 연도별 변화 분석")


# =====================================
# 2. 파일 경로 설정
# =====================================

BASE_DIR = Path(__file__).resolve().parent

POSSIBLE_DIRS = [
    BASE_DIR,
    BASE_DIR.parent
]

CAFE_FILE = "소상공인시장진흥공단_전국 카페 점포수_11_04_2019.csv"

REGION_FILE = "지역별_카페수.csv"


def find_file(filename):
    for folder in POSSIBLE_DIRS:
        path = folder / filename
        if path.exists():
            return path
    return None


def read_csv_file(path):
    for encoding in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")


# =====================================
# 3. 전국 카페 데이터 불러오기
# =====================================

cafe_path = find_file(CAFE_FILE)

if cafe_path is None:
    st.error(f"CSV 파일을 찾을 수 없습니다: {CAFE_FILE}")
    st.stop()

df = read_csv_file(cafe_path)

required_columns = ["기준월", "업소수"]

if not all(col in df.columns for col in required_columns):
    st.error("전국 카페 CSV의 컬럼명이 올바르지 않습니다.")
    st.write("필요한 컬럼: 기준월, 업소수")
    st.stop()

df["기준월"] = pd.to_datetime(df["기준월"], errors="coerce")
df["업소수"] = pd.to_numeric(df["업소수"], errors="coerce")

df = df.dropna(subset=["기준월", "업소수"])
df = df.sort_values("기준월")

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

df["연도"] = df["기준월"].dt.year
df["월"] = df["기준월"].dt.month


# =====================================
# 4. 연도별 카페 수 변화 분석
# =====================================

st.header("📈 연도별 카페 점포 수 변화")

# 각 연도에서 가장 마지막으로 기록된 값
year_df = (
    df.sort_values("기준월")
    .groupby("연도", as_index=False)
    .tail(1)
    .sort_values("연도")
    .copy()
)

year_df["전년 대비 증감"] = year_df["업소수"].diff()

year_df["전년 대비 증감률(%)"] = (
    year_df["업소수"].pct_change() * 100
)

# 최신 관측값
latest = df.iloc[-1]

col1, col2, col3 = st.columns(3)

col1.metric(
    "최근 관측 카페 수",
    f"{latest['업소수']:,.0f}개",
    help=f"기준월: {latest['기준월'].strftime('%Y년 %m월')}"
)

if len(year_df) >= 2:
    previous = year_df.iloc[-2]
    current = year_df.iloc[-1]

    difference = current["업소수"] - previous["업소수"]

    col2.metric(
        "최근 연도 간 증감",
        f"{difference:+,.0f}개"
    )

    rate = current["전년 대비 증감률(%)"]

    col3.metric(
        "최근 연도 간 증감률",
        f"{rate:+.2f}%"
    )

# 연도별 그래프
fig_year = px.bar(
    year_df,
    x="연도",
    y="업소수",
    text="업소수",
    title="연도별 마지막 관측 카페 점포 수",
    labels={
        "연도": "연도",
        "업소수": "카페 점포 수(개)"
    },
    color="업소수",
    color_continuous_scale="Blues"
)

fig_year.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig_year.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1
    ),
    yaxis_title="카페 점포 수(개)",
    coloraxis_showscale=False
)

st.plotly_chart(fig_year, use_container_width=True)


# =====================================
# 5. 월별 카페 수 변화
# =====================================

st.subheader("월별 카페 점포 수 변화")

fig_month = px.line(
    df,
    x="기준월",
    y="업소수",
    markers=True,
    title="전국 카페 점포 수 추이",
    labels={
        "기준월": "기준월",
        "업소수": "카페 점포 수(개)"
    }
)

fig_month.update_layout(
    hovermode="x unified",
    yaxis_title="카페 점포 수(개)"
)

st.plotly_chart(fig_month, use_container_width=True)


# =====================================
# 6. 연도별 증감 데이터 표
# =====================================

st.subheader("연도별 카페 점포 수 상세 분석")

display_year = year_df[
    ["연도", "기준월", "업소수",
     "전년 대비 증감", "전년 대비 증감률(%)"]
].copy()

display_year["기준월"] = (
    display_year["기준월"].dt.strftime("%Y-%m")
)

display_year = display_year.rename(columns={
    "연도": "연도",
    "기준월": "마지막 관측월",
    "업소수": "카페 점포 수",
    "전년 대비 증감": "전년 대비 증감(개)",
    "전년 대비 증감률(%)": "전년 대비 증감률(%)"
})

st.dataframe(
    display_year,
    use_container_width=True,
    hide_index=True
)


# =====================================
# 7. 지역별 카페 수 분석
# =====================================

st.divider()

st.header("🗺️ 지역별 카페 총개수")

region_path = find_file(REGION_FILE)

if region_path is None:

    st.warning(
        "지역별 카페 데이터가 아직 없습니다. "
        "지역별_카페수.csv 파일을 추가하면 지역 분석이 활성화됩니다."
    )

    st.info(
        "필요한 CSV 형식: 지역, 업소수 "
        "(예: 서울특별시, 12000)"
    )

else:

    region_df = read_csv_file(region_path)

    if not {"지역", "업소수"}.issubset(region_df.columns):
        st.error(
            "지역별 CSV에는 '지역', '업소수' 컬럼이 필요합니다."
        )

    else:

        region_df["업소수"] = pd.to_numeric(
            region_df["업소수"],
            errors="coerce"
        )

        region_df = region_df.dropna(
            subset=["지역", "업소수"]
        )

        # 동일 지역이 여러 행이면 합산
        region_df = (
            region_df.groupby("지역", as_index=False)["업소수"]
            .sum()
            .sort_values("업소수", ascending=False)
        )

        if not region_df.empty:

            selected_region = st.selectbox(
                "분석할 지역을 선택하세요.",
                region_df["지역"].tolist()
            )

            selected_data = region_df[
                region_df["지역"] == selected_region
            ].iloc[0]

            st.metric(
                f"{selected_region} 카페 총개수",
                f"{selected_data['업소수']:,.0f}개"
            )

            fig_region = px.bar(
                region_df,
                x="지역",
                y="업소수",
                text="업소수",
                title="전국 지역별 카페 점포 수 비교",
                labels={
                    "지역": "지역",
                    "업소수": "카페 점포 수(개)"
                },
                color="업소수",
                color_continuous_scale="Blues"
            )

            fig_region.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside"
            )

            fig_region.update_layout(
                xaxis_tickangle=-30,
                coloraxis_showscale=False
            )

            st.plotly_chart(
                fig_region,
                use_container_width=True
            )

            st.subheader("지역별 카페 점포 수 순위")

            ranking = region_df.reset_index(drop=True)
            ranking.index = ranking.index + 1
            ranking.index.name = "순위"

            st.dataframe(
                ranking,
                use_container_width=True
            )


# =====================================
# 8. 데이터 출처
# =====================================

st.divider()

st.caption(
    "자료 출처: 소상공인시장진흥공단 "
    "| 업로드된 전국 카페 점포 수 CSV"
)

st.caption(
    "주의: 연도별 수치는 해당 연도의 마지막 관측값이며, "
    "연간 평균이나 연말 확정치가 아닙니다."
)

