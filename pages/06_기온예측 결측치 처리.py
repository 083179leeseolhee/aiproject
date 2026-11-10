from pathlib import Path
import calendar
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures


# ==========================================
# 1. 기본 페이지 설정
# ==========================================

st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 미래 예측")

st.caption(
    "1907~2025년의 월별 평균기온을 분석하고 "
    "세 가지 머신러닝 알고리즘의 예측 결과를 비교합니다."
)

BASE_DIR = Path(__file__).resolve().parent

CSV_CANDIDATES = [
    BASE_DIR / "temperature.csv",
    BASE_DIR.parent / "temperature.csv",
]


# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_temperature_data(file_path):

    raw = None
    last_error = None

    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            raw = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError as error:
            last_error = error

    if raw is None:
        raise ValueError(
            f"CSV 인코딩 오류: {last_error}"
        )

    raw.columns = [
        str(column).strip()
        for column in raw.columns
    ]

    date_col = next(
        (c for c in raw.columns if c == "일시"),
        None
    )

    temp_col = next(
        (
            c for c in raw.columns
            if "평균기온" in c
            and "최고" not in c
            and "최저" not in c
        ),
        None
    )

    if date_col is None or temp_col is None:
        raise ValueError(
            "CSV에서 일시 또는 평균기온 열을 찾지 못했습니다."
        )

    month_lookup = {
        name.lower(): number
        for number, name in enumerate(
            calendar.month_abbr
        )
        if name
    }

    # 날짜 처리
    def parse_date(value, previous_year=None):

        text = str(value).strip()

        match = re.fullmatch(
            r"([A-Za-z]{3})-(\d{2,4})",
            text
        )

        if match:

            month_text, year_text = match.groups()

            month = month_lookup.get(
                month_text.lower()
            )

            year_number = int(year_text)

            if len(year_text) == 2:

                if previous_year is None:
                    year = 1900 + year_number

                else:
                    century = (
                        previous_year // 100
                    ) * 100

                    year = century + year_number

                    if year < previous_year:
                        year += 100

            else:
                year = year_number

            if month is not None:
                return year, month

        parsed = pd.to_datetime(
            text,
            errors="coerce"
        )

        if pd.isna(parsed):
            return np.nan, np.nan

        return parsed.year, parsed.month

    parsed_values = []
    previous_year = None

    for value in raw[date_col]:

        year, month = parse_date(
            value,
            previous_year
        )

        parsed_values.append((year, month))

        if pd.notna(year):
            previous_year = int(year)

    raw["연도"] = [
        value[0] for value in parsed_values
    ]

    raw["월"] = [
        value[1] for value in parsed_values
    ]

    raw["평균기온"] = pd.to_numeric(
        raw[temp_col]
        .astype(str)
        .str.replace(",", "", regex=False),
        errors="coerce"
    )

    data = raw.dropna(
        subset=["연도", "월", "평균기온"]
    ).copy()

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    # 1907~2025년 자료만 사용
    data = data[
        data["연도"].between(1907, 2025)
        & data["월"].between(1, 12)
    ]

    # 같은 연도와 월의 자료가 여러 개라면 평균 계산
    data = (
        data.groupby(
            ["연도", "월"],
            as_index=False
        )["평균기온"]
        .mean()
        .sort_values(["연도", "월"])
    )

    if data.empty:
        raise ValueError(
            "유효한 평균기온 자료가 없습니다."
        )

    return data


# CSV 경로 확인
csv_path = next(
    (
        path for path in CSV_CANDIDATES
        if path.exists()
    ),
    None
)

if csv_path is None:

    st.error(
        "temperature.csv 파일을 찾을 수 없습니다."
    )

    st.stop()


try:

    all_data = load_temperature_data(
        str(csv_path)
    )

except Exception as error:

    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {error}"
    )

    st.stop()


# ==========================================
# 3. 사용자 입력
# ==========================================

st.sidebar.header("📌 분석 조건")

selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda month: f"{month}월"
)

forecast_year = st.sidebar.number_input(
    "예측할 연도를 입력하세요.",
    min_value=2026,
    max_value=2100,
    value=2035,
    step=1
)


# 선택한 월의 데이터
month_data = all_data[
    all_data["월"] == selected_month
].copy()

month_data = month_data.sort_values("연도")


if len(month_data) < 5:

    st.error(
        "선택한 월의 데이터가 부족합니다."
    )

    st.stop()


X = month_data[["연도"]].astype(float)

y = month_data["평균기온"].astype(float)


# 미래 예측 연도
future_years = np.arange(
    2025,
    int(forecast_year) + 1
).reshape(-1, 1).astype(float)


# 과거 학습 연도
history_years = np.arange(
    int(month_data["연도"].min()),
    2026
).reshape(-1, 1).astype(float)


# ==========================================
# 4. 예측 알고리즘 3가지
# ==========================================

models = {

    "선형 회귀": LinearRegression(),

    "다항 회귀 (2차)": Pipeline([
        (
            "polynomial",
            PolynomialFeatures(
                degree=2,
                include_bias=False
            )
        ),

        (
            "regression",
            LinearRegression()
        )
    ]),

    "랜덤 포레스트": RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )

}


# ==========================================
# 5. 알고리즘 학습 및 예측
# ==========================================

predictions = {}
history_fits = {}

for model_name, model in models.items():

    # 모델 학습
    model.fit(X, y)

    # 미래 예측
    predictions[model_name] = model.predict(
        future_years
    )

    # 과거 학습 결과
    history_fits[model_name] = model.predict(
        history_years
    )


# ==========================================
# 6. 예측 결과 표시
# ==========================================

st.subheader(
    f"📅 {selected_month}월 평균기온 분석"
)

st.write(
    f"실제 관측 자료 "
    f"**{int(month_data['연도'].min())}~2025년**을 "
    f"사용해 {int(forecast_year)}년의 평균기온을 예측합니다."
)

result_columns = st.columns(3)

for column, (model_name, values) in zip(
    result_columns,
    predictions.items()
):

    column.metric(
        label=f"{model_name} 예측",
        value=f"{values[-1]:.2f} ℃"
    )


# ==========================================
# 7. 통합 비교 그래프
# ==========================================

st.subheader(
    "📈 실제 기온과 알고리즘별 예측 비교"
)

fig = go.Figure()


# 실제 평균기온
fig.add_trace(
    go.Scatter(
        x=month_data["연도"],
        y=month_data["평균기온"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            size=6,
            color="#222222"
        ),
        hovertemplate=(
            "%{x}년 실제 평균기온: "
            "%{y:.2f}℃<extra></extra>"
        )
    )
)


# 알고리즘별 색상
algorithm_styles = {

    "선형 회귀": "#1f77b4",

    "다항 회귀 (2차)": "#e67e22",

    "랜덤 포레스트": "#2ca02c"

}


# 과거 학습 곡선
for model_name in models:

    color = algorithm_styles[model_name]

    fig.add_trace(
        go.Scatter(
            x=history_years.ravel(),
            y=history_fits[model_name],
            mode="lines",
            name=f"{model_name} 학습 곡선",
            line=dict(
                color=color,
                width=2,
                dash="dot"
            )
        )
    )


# 미래 예측 그래프
for model_name in models:

    color = algorithm_styles[model_name]

    future_values = predictions[model_name]

    fig.add_trace(
        go.Scatter(
            x=future_years.ravel(),
            y=future_values,
            mode="lines+markers",
            name=f"{model_name} 미래 예측",
            line=dict(
                color=color,
                width=3
            ),
            marker=dict(size=5),
            hovertemplate=(
                "%{x}년 예측 평균기온: "
                "%{y:.2f}℃<extra></extra>"
            )
        )
    )


# 2025년 기준선
fig.add_vline(
    x=2025,
    line_width=2,
    line_dash="dash",
    line_color="gray",
    annotation_text="실제 데이터 마지막 연도(2025)",
    annotation_position="top"
)


fig.update_layout(

    height=650,

    xaxis_title="연도",

    yaxis_title="월평균기온 (℃)",

    hovermode="x unified",

    legend_title="자료 및 예측 알고리즘",

    template="plotly_white",

    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    )

)


st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    "점: 실제 관측값 / 점선: 과거 학습 결과 / "
    "실선: 미래 예측 결과"
)


# ==========================================
# 8. 알고리즘별 작동 원리 설명
# ==========================================

st.subheader(
    "🧠 알고리즘별 작동 방식과 차이"
)

col1, col2, col3 = st.columns(3)


# 선형 회귀
with col1:

    st.markdown("### 1. 선형 회귀")

    st.markdown("**작동 방식**")

    st.write(
        "연도와 평균기온 사이에 가장 잘 맞는 "
        "직선을 찾아 전체적인 상승 또는 하락 추세를 표현합니다."
    )

    st.markdown("**그래프 특징**")

    st.write(
        "학습 곡선이 직선으로 나타납니다. "
        "미래에도 같은 기울기가 이어진다고 가정합니다."
    )

    st.markdown("**장점과 한계**")

    st.write(
        "계산과 해석이 쉽지만 복잡한 기온 변화 패턴을 "
        "충분히 반영하지 못할 수 있습니다."
    )


# 다항 회귀
with col2:

    st.markdown("### 2. 다항 회귀 (2차)")

    st.markdown("**작동 방식**")

    st.write(
        "연도뿐 아니라 연도의 제곱 항도 사용하여 "
        "곡선 형태의 관계를 학습합니다."
    )

    st.markdown("**그래프 특징**")

    st.write(
        "학습 곡선이 휘어질 수 있습니다. "
        "완만한 기온 변화 추세를 표현할 수 있습니다."
    )

    st.markdown("**장점과 한계**")

    st.write(
        "곡선 형태의 추세를 표현하지만 "
        "먼 미래에는 예측값이 크게 벗어날 수 있습니다."
    )


# 랜덤 포레스트
with col3:

    st.markdown("### 3. 랜덤 포레스트")

    st.markdown("**작동 방식**")

    st.write(
        "여러 결정 트리를 만들고 각 트리의 예측값을 "
        "평균 내어 최종 결과를 계산합니다."
    )

    st.markdown("**그래프 특징**")

    st.write(
        "학습 곡선이 구간별로 계단처럼 변할 수 있습니다. "
        "미래에는 예측값이 거의 일정하게 나타날 수 있습니다."
    )

    st.markdown("**장점과 한계**")

    st.write(
        "복잡한 패턴을 학습할 수 있지만 "
        "학습 범위 밖의 미래 추세를 연장하는 데 약합니다."
    )


# ==========================================
# 9. 예측 결과 비교표
# ==========================================

st.subheader(
    "📋 예측 결과 비교표"
)

result_df = pd.DataFrame({

    "알고리즘": list(predictions.keys()),

    f"{int(forecast_year)}년 {selected_month}월 예측 평균기온(℃)": [

        round(float(values[-1]), 2)

        for values in predictions.values()

    ]

})


st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 10. 데이터 및 분석 안내
# ==========================================

st.info(
    "주의: 이 결과는 과거 평균기온과 연도만 사용한 "
    "통계적 예측입니다. 실제 미래 기온을 보장하지 않습니다. "
    "온실가스 배출량, 해류, 태양활동 등 다른 기후 요인은 "
    "모델에 직접 포함하지 않았습니다."
)


with st.expander("📚 데이터 및 분석 기준"):

    st.write(f"- 사용 파일: {csv_path.name}")

    st.write("- 분석 변수: 평균기온(℃)")

    st.write("- 분석 기간: 1907~2025년")

    st.write(
        f"- 선택 월의 유효 관측 개수: {len(month_data)}개"
    )

    st.write("- 2026년 자료는 분석 기간에서 제외했습니다.")

    st.write("- 데이터가 없는 연도는 관측값이 표시되지 않습니다.")

    st.write(
        "- 원본 자료가 1907년 10월부터 시작하므로 "
        "1907년 1~9월 자료는 없습니다."
    )
