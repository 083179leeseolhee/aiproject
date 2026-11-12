
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write(
    "꽃잎의 길이와 너비를 입력하고 "
    "분류 알고리즘을 선택하면 붓꽃의 품종을 예측합니다."
)

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

required_columns = [
    "꽃잎길이",
    "꽃잎너비",
    "품종"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.stop()

df = df[required_columns].copy()

df["꽃잎길이"] = pd.to_numeric(
    df["꽃잎길이"], errors="coerce"
)

df["꽃잎너비"] = pd.to_numeric(
    df["꽃잎너비"], errors="coerce"
)

df = df.dropna()

if df.empty or df["품종"].nunique() < 2:
    st.error("학습에 사용할 데이터가 부족합니다.")
    st.stop()


# ==========================================
# 4. 입력값 범위 자동 설정
# ==========================================

length_min = float(df["꽃잎길이"].min())
length_max = float(df["꽃잎길이"].max())

width_min = float(df["꽃잎너비"].min())
width_max = float(df["꽃잎너비"].max())


# ==========================================
# 5. 분류 알고리즘 선택
# ==========================================

st.subheader("🤖 분류 알고리즘 선택")

algorithm_names = {
    "Random Forest": "랜덤 포레스트",
    "KNN": "K-최근접 이웃",
    "SVM": "서포트 벡터 머신"
}

selected_algorithm = st.selectbox(
    "사용할 알고리즘을 선택하세요.",
    list(algorithm_names.keys())
)

st.info(
    f"현재 선택된 알고리즘: "
    f"**{algorithm_names[selected_algorithm]} ({selected_algorithm})**"
)


# ==========================================
# 6. 알고리즘별 모델 생성 및 학습
# ==========================================

@st.cache_resource
def train_model(X, y, algorithm):

    if algorithm == "Random Forest":

        model = RandomForestClassifier(
            n_estimators=200,
            random_state=42
        )

    elif algorithm == "KNN":

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", KNeighborsClassifier(
                n_neighbors=5
            ))
        ])

    elif algorithm == "SVM":

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", SVC(
                kernel="rbf",
                probability=True,
                random_state=42
            ))
        ])

    model.fit(X, y)

    return model


X = df[["꽃잎길이", "꽃잎너비"]]
y = df["품종"]

model = train_model(
    X,
    y,
    selected_algorithm
)


# ==========================================
# 7. 사용자 입력
# ==========================================

st.divider()
st.subheader("✏️ 꽃잎 정보 입력")

col1, col2 = st.columns(2)

with col1:

    petal_length = st.number_input(
        "꽃잎길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=float(df["꽃잎길이"].median()),
        step=0.1,
        format="%.1f"
    )

with col2:

    petal_width = st.number_input(
        "꽃잎너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=float(df["꽃잎너비"].median()),
        step=0.1,
        format="%.1f"
    )

st.caption(
    f"꽃잎길이 입력 범위: {length_min} ~ {length_max} cm"
)

st.caption(
    f"꽃잎너비 입력 범위: {width_min} ~ {width_max} cm"
)

predict_button = st.button(
    "🌸 붓꽃 품종 예측하기",
    type="primary",
    use_container_width=True
)


# ==========================================
# 8. 품종 예측 결과
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
        f"예측된 붓꽃 품종: "
        f"{species_names.get(prediction, prediction)}"
    )

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.metric(
            "예측 확률",
            f"{confidence:.1f}%"
        )

    with result_col2:
        st.metric(
            "사용한 알고리즘",
            algorithm_names[selected_algorithm]
        )

    st.write("**입력한 데이터**")
    st.write(f"- 꽃잎길이: {petal_length} cm")
    st.write(f"- 꽃잎너비: {petal_width} cm")

    # 품종별 예측 확률
    st.subheader("📊 품종별 예측 확률")

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
        title=f"{algorithm_names[selected_algorithm]} 예측 결과"
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
# 9. 산점도 시각화
# ==========================================

st.divider()
st.subheader("📈 붓꽃 데이터 산점도")

st.write(
    "가로축은 꽃잎길이, 세로축은 꽃잎너비입니다."
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
    title="붓꽃 품종별 꽃잎 크기 분포"
)

# 사용자 입력값 표시
fig.add_trace(
    go.Scatter(
        x=[petal_length],
        y=[petal_width],
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
    range=[
        max(0, length_min - 0.5),
        length_max + 0.5
    ]
)

fig.update_yaxes(
    range=[
        max(0, width_min - 0.2),
        width_max + 0.2
    ]
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 10. 데이터 정보
# ==========================================

with st.expander("📚 데이터 및 알고리즘 정보"):

    st.write("**전체 데이터 개수**")
    st.write(f"{len(df)}개")

    st.write("**품종별 데이터 개수**")
    st.write(df["품종"].value_counts())

    st.write("**사용 가능한 알고리즘**")

    for key, name in algorithm_names.items():
        st.write(f"- {name} ({key})")

    st.write("**학습에 사용한 변수**")
    st.write("- 꽃잎길이")
    st.write("- 꽃잎너비")

    st.write("**데이터 최솟값 및 최댓값**")

    st.write(
        f"꽃잎길이: {length_min} ~ {length_max}"
    )

    st.write(
        f"꽃잎너비: {width_min} ~ {width_max}"
    )

    st.dataframe(
        df,
        use_container_width=True
    )


st.divider()

st.caption(
    "Iris 데이터셋을 활용한 머신러닝 붓꽃 품종 분류 프로그램"
)
