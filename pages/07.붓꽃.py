
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestClassifier


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write("꽃잎의 길이와 너비를 입력하면 AI가 붓꽃의 품종을 예측합니다.")

st.divider()


# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

current_folder = Path(__file__).resolve().parent

file_candidates = [
    current_folder / "iris.csv",
    current_folder.parent / "iris.csv"
]

csv_path = next(
    (path for path in file_candidates if path.exists()),
    None
)

if csv_path is None:
    st.error("iris.csv 파일을 찾을 수 없습니다.")
    st.info("CSV 파일을 app.py와 같은 폴더 또는 상위 폴더에 넣어주세요.")
    st.stop()


# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    return data


df = load_data(str(csv_path))

required_columns = ["꽃잎길이", "꽃잎너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일에 필요한 열이 없습니다.")
    st.stop()

df = df[required_columns].dropna()

X = df[["꽃잎길이", "꽃잎너비"]]
y = df["품종"]


# ==========================================
# 4. 랜덤 포레스트 모델 학습
# ==========================================

@st.cache_resource
def train_model(X, y):

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X, y)

    return model


model = train_model(X, y)


# ==========================================
# 5. 사용자 입력
# ==========================================

st.subheader("✏️ 꽃잎 정보 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎길이 (cm)",
        min_value=1.0,
        max_value=6.9,
        value=3.0,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "꽃잎너비 (cm)",
        min_value=0.1,
        max_value=2.5,
        value=1.0,
        step=0.1
    )

predict_button = st.button(
    "🌸 품종 예측하기",
    type="primary",
    use_container_width=True
)


# ==========================================
# 6. 품종 예측
# ==========================================

if predict_button:

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎길이", "꽃잎너비"]
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    confidence = max(probabilities) * 100

    st.divider()

    st.subheader("🔍 AI 예측 결과")

    species_names = {
        "Iris-setosa": "세토사 (Setosa)",
        "Iris-versicolor": "버시컬러 (Versicolor)",
        "Iris-virginica": "버지니카 (Virginica)"
    }

    st.success(
        f"예측된 품종: {species_names.get(prediction, prediction)}"
    )

    st.metric(
        label="예측 확률",
        value=f"{confidence:.1f}%"
    )

    st.write(
        f"입력한 꽃잎길이: {petal_length} cm"
    )

    st.write(
        f"입력한 꽃잎너비: {petal_width} cm"
    )

    # 품종별 예측 확률
    st.subheader("품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": [
            species_names.get(name, name)
            for name in model.classes_
        ],
        "예측 확률": probabilities * 100
    })

    fig_probability = px.bar(
        probability_df,
        x="품종",
        y="예측 확률",
        color="품종",
        text="예측 확률",
        title="품종별 예측 확률 비교"
    )

    fig_probability.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_probability.update_layout(
        yaxis_title="예측 확률 (%)",
        xaxis_title="붓꽃 품종",
        yaxis_range=[0, 110],
        showlegend=False
    )

    st.plotly_chart(
        fig_probability,
        use_container_width=True
    )


# ==========================================
# 7. 산점도 시각화
# ==========================================

st.divider()

st.subheader("📊 붓꽃 데이터 산점도")

st.write(
    "가로축은 꽃잎길이, 세로축은 꽃잎너비입니다. "
    "초록색 별은 사용자가 입력한 위치를 나타냅니다."
)

fig = px.scatter(
    df,
    x="꽃잎길이",
    y="꽃잎너비",
    color="품종",
    color_discrete_sequence=[
        "#636EFA",
        "#EF553B",
        "#AB63FA"
    ],
    title="붓꽃 품종별 꽃잎 크기 분포",
    hover_data=["품종"]
)

# 사용자가 입력한 값 표시
fig.add_trace(
    go.Scatter(
        x=[petal_length] if "petal_length" in locals() else [],
        y=[petal_width] if "petal_width" in locals() else [],
        mode="markers",
        name="사용자 입력값",
        marker=dict(
            symbol="star",
            size=22,
            color="green",
            line=dict(
                color="black",
                width=1
            )
        )
    )
)

fig.update_layout(
    xaxis_title="꽃잎길이 (cm)",
    yaxis_title="꽃잎너비 (cm)",
    legend_title="붓꽃 품종",
    height=600
)

fig.update_xaxes(
    range=[0.5, 7.2]
)

fig.update_yaxes(
    range=[0, 2.7]
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 8. 데이터 정보
# ==========================================

with st.expander("📚 데이터 정보 확인"):

    st.write("전체 데이터 개수:", len(df))

    st.write("품종별 데이터 개수")

    st.write(df["품종"].value_counts())

    st.write("사용된 알고리즘: Random Forest")

    st.write("학습에 사용된 변수:")
    st.write("- 꽃잎길이")
    st.write("- 꽃잎너비")

    st.dataframe(df, use_container_width=True)

st.divider()

st.caption(
    "본 프로그램은 Iris 데이터셋을 활용한 머신러닝 품종 분류 프로그램입니다."
)

