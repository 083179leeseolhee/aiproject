```python
import streamlit as st

st.set_page_config(
    page_title="MBTI 진로 탐험소 🔎",
    page_icon="🧭",
    layout="wide"
)

# 화면 디자인
st.markdown("""
<style>
    .stApp {
        background-color: #F7F7FF;
    }
    h1, h2, h3 {
        color: #5546A8;
    }
    .career-card {
        background-color: white;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #E3DFFD;
        margin-bottom: 15px;
    }
    .tip {
        background-color: #EDEAFF;
        padding: 15px;
        border-radius: 12px;
        color: #40357F;
    }
</style>
""", unsafe_allow_html=True)

# 직업 데이터
# 연봉은 정확한 최신 통계값이 아닌 진로 탐색용 예시 범위이며,
# 실제 직업별 임금 통계와 구분해서 표시한다.
careers = {
    "ISTJ": [
        {
            "name": "회계사",
            "emoji": "📊",
            "major": "회계학과, 경영학과, 경제학과",
            "personality": "꼼꼼하고 책임감이 강하며 숫자와 규칙을 정확하게 다루는 사람",
            "salary": "약 4,000만~8,000만 원 이상",
            "description": "기업의 재무 상태를 확인하고 회계 자료와 세금 관련 업무를 처리해.",
            "skill": "수리 능력, 분석력, 세심함"
        },
        {
            "name": "품질관리 전문가",
            "emoji": "🔍",
            "major": "산업공학과, 화학공학과, 기계공학과",
            "personality": "기준을 잘 지키고 문제를 체계적으로 해결하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "제품이 정해진 기준에 맞게 만들어졌는지 검사하고 개선점을 찾아.",
            "skill": "관찰력, 논리력, 책임감"
        }
    ],
    "ISFJ": [
        {
            "name": "간호사",
            "emoji": "🩺",
            "major": "간호학과",
            "personality": "다른 사람을 세심하게 살피고 책임감 있게 행동하는 사람",
            "salary": "약 3,500만~5,500만 원",
            "description": "환자의 건강 상태를 살피고 치료와 회복을 도와.",
            "skill": "공감 능력, 관찰력, 협동심"
        },
        {
            "name": "초등교사",
            "emoji": "🍎",
            "major": "초등교육과",
            "personality": "인내심이 있고 다른 사람의 성장을 돕는 것을 좋아하는 사람",
            "salary": "약 3,000만~6,000만 원",
            "description": "초등학생에게 여러 과목을 가르치고 학교생활을 지도해.",
            "skill": "설명 능력, 인내심, 소통 능력"
        }
    ],
    "INFJ": [
        {
            "name": "상담심리사",
            "emoji": "💬",
            "major": "심리학과, 상담학과",
            "personality": "다른 사람의 이야기를 잘 듣고 감정과 행동을 이해하려는 사람",
            "salary": "약 2,800만~4,500만 원",
            "description": "사람들이 고민을 정리하고 문제를 해결하도록 상담을 진행해.",
            "skill": "경청, 공감, 의사소통"
        },
        {
            "name": "작가",
            "emoji": "✍️",
            "major": "국어국문학과, 문예창작학과",
            "personality": "생각이 깊고 글로 자신의 생각과 이야기를 표현하는 사람",
            "salary": "수입 편차가 커서 일률적인 평균 제시가 어려움",
            "description": "책, 웹 콘텐츠, 시나리오 등 다양한 글을 기획하고 써.",
            "skill": "창의력, 표현력, 관찰력"
        }
    ],
    "INTJ": [
        {
            "name": "소프트웨어 개발자",
            "emoji": "💻",
            "major": "컴퓨터공학과, 소프트웨어학과",
            "personality": "논리적으로 생각하고 복잡한 문제를 해결하는 것을 좋아하는 사람",
            "salary": "약 3,500만~7,000만 원",
            "description": "컴퓨터 프로그램과 앱을 설계하고 개발해.",
            "skill": "논리력, 문제 해결력, 집중력"
        },
        {
            "name": "연구원",
            "emoji": "🔬",
            "major": "관심 분야에 따른 자연과학·공학 계열 학과",
            "personality": "호기심이 많고 한 가지 주제를 깊이 탐구하는 사람",
            "salary": "약 3,500만~6,500만 원",
            "description": "새로운 지식을 발견하거나 기술과 제품을 연구해.",
            "skill": "분석력, 탐구심, 끈기"
        }
    ],
    "ISTP": [
        {
            "name": "기계공학 기술자",
            "emoji": "⚙️",
            "major": "기계공학과, 메카트로닉스공학과",
            "personality": "기계의 작동 원리를 파악하고 직접 문제를 해결하는 것을 좋아하는 사람",
            "salary": "약 3,500만~6,000만 원",
            "description": "기계와 장비를 설계하거나 성능을 개선해.",
            "skill": "분석력, 실용적인 사고, 문제 해결력"
        },
        {
            "name": "자동차 정비사",
            "emoji": "🚗",
            "major": "자동차공학과, 자동차정비 관련 학과",
            "personality": "도구를 활용해 고장 원인을 찾고 직접 해결하는 것을 좋아하는 사람",
            "salary": "약 2,800만~4,500만 원",
            "description": "자동차의 고장 원인을 진단하고 정비와 점검을 해.",
            "skill": "관찰력, 손재주, 실습 능력"
        }
    ],
    "ISFP": [
        {
            "name": "제품 디자이너",
            "emoji": "🎨",
            "major": "산업디자인학과, 제품디자인학과",
            "personality": "미적 감각이 있고 새로운 형태와 아이디어를 표현하는 사람",
            "salary": "약 3,000만~5,000만 원",
            "description": "사람들이 편리하게 사용할 수 있는 제품의 모양과 기능을 디자인해.",
            "skill": "창의력, 관찰력, 시각적 표현력"
        },
        {
            "name": "제과제빵사",
            "emoji": "🥐",
            "major": "제과제빵과, 호텔조리학과, 식품영양학과",
            "personality": "손으로 무언가를 만들고 맛과 모양을 섬세하게 표현하는 사람",
            "salary": "약 2,600만~4,000만 원",
            "description": "빵과 케이크, 디저트를 만들고 새로운 메뉴를 개발해.",
            "skill": "섬세함, 창의력, 꾸준함"
        }
    ],
    "INFP": [
        {
            "name": "콘텐츠 작가",
            "emoji": "📖",
            "major": "문예창작학과, 국어국문학과, 미디어학과",
            "personality": "상상력이 풍부하고 자신의 생각을 글로 표현하는 것을 좋아하는 사람",
            "salary": "수입 편차가 커서 일률적인 평균 제시가 어려움",
            "description": "웹 콘텐츠, 소설, 영상 대본 등 다양한 이야기를 만들어.",
            "skill": "창의력, 표현력, 공감 능력"
        },
        {
            "name": "일러스트레이터",
            "emoji": "🖌️",
            "major": "시각디자인학과, 회화과, 일러스트레이션 관련 학과",
            "personality": "자신만의 시각과 감성을 그림으로 표현하는 것을 좋아하는 사람",
            "salary": "수입 편차가 커서 일률적인 평균 제시가 어려움",
            "description": "책, 광고, 캐릭터, 디지털 콘텐츠에 들어가는 그림을 제작해.",
            "skill": "표현력, 창의력, 관찰력"
        }
    ],
    "INTP": [
        {
            "name": "데이터 분석가",
            "emoji": "📈",
            "major": "통계학과, 데이터사이언스학과, 컴퓨터공학과",
            "personality": "자료 속에서 규칙을 찾고 논리적으로 원인을 분석하는 사람",
            "salary": "약 3,500만~7,000만 원",
            "description": "데이터를 분석해 문제의 원인을 찾고 의사결정에 필요한 정보를 제공해.",
            "skill": "논리력, 수리 능력, 분석력"
        },
        {
            "name": "수학 연구원",
            "emoji": "➗",
            "major": "수학과, 응용수학과, 통계학과",
            "personality": "추상적인 개념과 어려운 문제를 깊이 탐구하는 사람",
            "salary": "약 3,500만~6,500만 원",
            "description": "수학적 이론을 연구하고 다양한 분야에 적용할 방법을 찾아.",
            "skill": "논리력, 집중력, 탐구심"
        }
    ],
    "ESTP": [
        {
            "name": "마케팅 기획자",
            "emoji": "📣",
            "major": "경영학과, 광고홍보학과, 마케팅 관련 학과",
            "personality": "변화에 빠르게 대응하고 사람들의 반응을 관찰하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "상품과 브랜드를 알리기 위한 홍보 전략과 캠페인을 기획해.",
            "skill": "실행력, 소통 능력, 상황 판단력"
        },
        {
            "name": "스포츠 지도자",
            "emoji": "🏃",
            "major": "체육학과, 스포츠과학과, 스포츠지도학과",
            "personality": "활동적인 환경을 좋아하고 사람들에게 동기를 주는 사람",
            "salary": "약 2,800만~4,500만 원",
            "description": "운동 기술을 가르치고 훈련과 체력 관리를 도와.",
            "skill": "지도력, 체력, 소통 능력"
        }
    ],
    "ESFP": [
        {
            "name": "이벤트 기획자",
            "emoji": "🎉",
            "major": "이벤트학과, 관광학과, 광고홍보학과",
            "personality": "사람들과 어울리고 즐거운 경험을 만드는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,000만 원",
            "description": "축제, 행사, 공연 등 사람들이 즐길 수 있는 이벤트를 기획해.",
            "skill": "소통 능력, 순발력, 기획력"
        },
        {
            "name": "호텔 서비스 매니저",
            "emoji": "🏨",
            "major": "호텔경영학과, 관광학과, 호텔관광학과",
            "personality": "사람을 대하는 것을 좋아하고 예상치 못한 상황에 유연하게 대응하는 사람",
            "salary": "약 3,000만~5,000만 원",
            "description": "호텔의 서비스 운영을 관리하고 고객의 편안한 이용을 도와.",
            "skill": "친절함, 소통 능력, 상황 대처 능력"
        }
    ],
    "ENFP": [
        {
            "name": "광고 기획자",
            "emoji": "💡",
            "major": "광고홍보학과, 미디어학과, 경영학과",
            "personality": "아이디어가 풍부하고 새로운 방식으로 사람들의 관심을 끄는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "브랜드와 제품을 효과적으로 알릴 광고 아이디어를 기획해.",
            "skill": "창의력, 설득력, 소통 능력"
        },
        {
            "name": "방송·영상 콘텐츠 기획자",
            "emoji": "🎬",
            "major": "미디어학과, 영상학과, 방송영상학과",
            "personality": "새로운 이야기를 떠올리고 여러 사람과 협업하는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "영상과 방송 콘텐츠의 주제를 정하고 제작 과정을 기획해.",
            "skill": "기획력, 창의력, 협업 능력"
        }
    ],
    "ENTP": [
        {
            "name": "창업가",
            "emoji": "🚀",
            "major": "경영학과, 창업학과, 산업공학과 등",
            "personality": "새로운 아이디어를 실험하고 문제를 다른 관점에서 바라보는 사람",
            "salary": "사업 성과에 따라 편차가 매우 큼",
            "description": "새로운 제품이나 서비스를 기획하고 사업으로 발전시켜.",
            "skill": "기획력, 도전 정신, 문제 해결력"
        },
        {
            "name": "브랜드 전략 기획자",
            "emoji": "🌟",
            "major": "경영학과, 광고홍보학과, 소비자학과",
            "personality": "기존 방식을 분석하고 차별화된 전략을 만드는 것을 좋아하는 사람",
            "salary": "약 3,500만~6,000만 원",
            "description": "브랜드의 이미지와 목표 고객을 분석하고 성장 전략을 세워.",
            "skill": "분석력, 창의력, 설득력"
        }
    ],
    "ESTJ": [
        {
            "name": "프로젝트 매니저",
            "emoji": "📋",
            "major": "경영학과, 산업공학과, 정보시스템학과",
            "personality": "목표와 일정을 정리하고 여러 사람의 업무를 체계적으로 관리하는 사람",
            "salary": "약 4,000만~7,000만 원",
            "description": "프로젝트의 일정과 예산, 인력을 관리해 목표 달성을 도와.",
            "skill": "조직력, 책임감, 의사소통"
        },
        {
            "name": "물류관리 전문가",
            "emoji": "📦",
            "major": "물류학과, 산업공학과, 유통학과",
            "personality": "계획을 세우고 자원을 효율적으로 관리하는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "상품의 보관과 운송, 재고 흐름을 효율적으로 관리해.",
            "skill": "계획력, 분석력, 문제 해결력"
        }
    ],
    "ESFJ": [
        {
            "name": "인사 담당자",
            "emoji": "🤝",
            "major": "경영학과, 심리학과, 행정학과",
            "personality": "사람들과 협력하고 조직 안에서 원활한 관계를 만드는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "직원 채용과 교육, 조직문화 및 인사 관련 업무를 담당해.",
            "skill": "소통 능력, 배려, 조직력"
        },
        {
            "name": "사회복지사",
            "emoji": "💗",
            "major": "사회복지학과",
            "personality": "다른 사람의 어려움을 이해하고 현실적인 도움을 주려는 사람",
            "salary": "약 2,800만~4,000만 원",
            "description": "도움이 필요한 사람들에게 복지 서비스와 지원 제도를 안내해.",
            "skill": "공감 능력, 책임감, 상담 능력"
        }
    ],
    "ENFJ": [
        {
            "name": "교사",
            "emoji": "📚",
            "major": "교육학과 또는 담당 과목 관련 학과",
            "personality": "다른 사람의 성장을 돕고 이해하기 쉽게 설명하는 것을 좋아하는 사람",
            "salary": "약 3,000만~6,000만 원",
            "description": "학생들에게 지식을 가르치고 학습과 성장을 지원해.",
            "skill": "설명 능력, 공감, 지도력"
        },
        {
            "name": "교육 프로그램 기획자",
            "emoji": "🧩",
            "major": "교육학과, 교육공학과, 평생교육학과",
            "personality": "사람들의 필요를 이해하고 유익한 학습 경험을 만드는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,000만 원",
            "description": "학교나 기업, 기관에서 진행할 교육 과정과 프로그램을 설계해.",
            "skill": "기획력, 소통 능력, 공감 능력"
        }
    ],
    "ENTJ": [
        {
            "name": "경영 컨설턴트",
            "emoji": "📌",
            "major": "경영학과, 경제학과, 산업공학과",
            "personality": "문제를 분석하고 목표를 정해 개선 방향을 제시하는 사람",
            "salary": "약 4,000만~8,000만 원 이상",
            "description": "기업의 문제를 분석하고 경영 성과를 높일 전략을 제안해.",
            "skill": "분석력, 논리력, 의사소통"
        },
        {
            "name": "사업 기획자",
            "emoji": "🗂️",
            "major": "경영학과, 경제학과, 산업공학과",
            "personality": "큰 목표를 세우고 여러 자원을 활용해 계획을 실행하는 사람",
            "salary": "약 3,500만~6,500만 원",
            "description": "새로운 사업의 가능성을 분석하고 실행 계획을 세워.",
            "skill": "기획력, 리더십, 분석력"
        }
    ],
    "INFP": [
        {
            "name": "콘텐츠 작가",
            "emoji": "📖",
            "major": "문예창작학과, 국어국문학과, 미디어학과",
            "personality": "상상력이 풍부하고 글로 자신의 생각을 표현하는 것을 좋아하는 사람",
            "salary": "수입 편차가 커서 일률적인 평균 제시가 어려움",
            "description": "웹 콘텐츠, 소설, 시나리오 등 다양한 이야기를 만들어.",
            "skill": "창의력, 표현력, 공감 능력"
        },
        {
            "name": "일러스트레이터",
            "emoji": "🖌️",
            "major": "시각디자인학과, 회화과, 일러스트레이션 관련 학과",
            "personality": "자신만의 시각과 감성을 그림으로 표현하는 것을 좋아하는 사람",
            "salary": "수입 편차가 커서 일률적인 평균 제시가 어려움",
            "description": "책, 광고, 캐릭터, 디지털 콘텐츠에 들어가는 그림을 제작해.",
            "skill": "표현력, 창의력, 관찰력"
        }
    ],
    "ISFP": [
        {
            "name": "제품 디자이너",
            "emoji": "🎨",
            "major": "산업디자인학과, 제품디자인학과",
            "personality": "미적 감각이 있고 새로운 형태와 아이디어를 표현하는 사람",
            "salary": "약 3,000만~5,000만 원",
            "description": "사람들이 편리하게 사용할 수 있는 제품의 모양과 기능을 디자인해.",
            "skill": "창의력, 관찰력, 시각적 표현력"
        },
        {
            "name": "제과제빵사",
            "emoji": "🥐",
            "major": "제과제빵과, 호텔조리학과, 식품영양학과",
            "personality": "손으로 무언가를 만들고 맛과 모양을 섬세하게 표현하는 사람",
            "salary": "약 2,600만~4,000만 원",
            "description": "빵과 케이크, 디저트를 만들고 새로운 메뉴를 개발해.",
            "skill": "섬세함, 창의력, 꾸준함"
        }
    ],
    "ENFP": [
        {
            "name": "광고 기획자",
            "emoji": "💡",
            "major": "광고홍보학과, 미디어학과, 경영학과",
            "personality": "아이디어가 풍부하고 새로운 방식으로 사람들의 관심을 끄는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "브랜드와 제품을 효과적으로 알릴 광고 아이디어를 기획해.",
            "skill": "창의력, 설득력, 소통 능력"
        },
        {
            "name": "방송·영상 콘텐츠 기획자",
            "emoji": "🎬",
            "major": "미디어학과, 영상학과, 방송영상학과",
            "personality": "새로운 이야기를 떠올리고 여러 사람과 협업하는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "영상과 방송 콘텐츠의 주제를 정하고 제작 과정을 기획해.",
            "skill": "기획력, 창의력, 협업 능력"
        }
    ]
}

# 유형별 소개
type_info = {
    "ISTJ": ("🧱 현실적인 관리자", "계획과 책임을 중요하게 생각해요."),
    "ISFJ": ("🌷 따뜻한 수호자", "주변 사람을 세심하게 살피는 편이에요."),
    "INFJ": ("🌙 통찰력 있는 조언자", "의미와 가치를 중요하게 생각해요."),
    "INTJ": ("♟️ 전략적인 설계자", "큰 그림을 그리고 체계적으로 해결해요."),
    "ISTP": ("🛠️ 실용적인 탐험가", "직접 분석하고 해결하는 것을 좋아해요."),
    "ISFP": ("🎨 감각적인 예술가", "자신만의 감성과 표현을 중요하게 생각해요."),
    "INFP": ("🦋 상상력 풍부한 중재자", "가치와 창의적인 표현을 중요하게 생각해요."),
    "INTP": ("🧠 호기심 많은 분석가", "원리를 알아내고 깊이 탐구하는 것을 좋아해요."),
    "ESTP": ("⚡ 행동력 있는 도전자", "직접 경험하며 빠르게 대응하는 편이에요."),
    "ESFP": ("🎉 활기찬 분위기 메이커", "사람들과 즐거운 경험을 만드는 것을 좋아해요."),
    "ENFP": ("🌈 열정적인 아이디어 뱅크", "새로운 가능성을 발견하는 것을 좋아해요."),
    "ENTP": ("💡 재치 있는 발명가", "기존 방식에 질문하고 새로운 아이디어를 내요."),
    "ESTJ": ("📋 체계적인 운영자", "목표와 규칙을 세우고 실행하는 것을 좋아해요."),
    "ESFJ": ("💞 다정한 협력가", "사람들과 협력하고 관계를 소중히 여겨요."),
    "ENFJ": ("🌟 사람을 이끄는 리더", "다른 사람의 성장과 발전을 돕는 편이에요."),
    "ENTJ": ("🚀 목표 지향적인 리더", "전략을 세우고 목표를 향해 나아가요.")
}

# 화면
st.title("🧭 MBTI 진로 탐험소")
st.markdown("### 나에게 어울리는 미래 직업을 찾아보자! ✨")
st.write(
    "MBTI를 선택하면 관련 진로 2가지를 추천해 줄게요. "
    "관심 있는 직업을 발견하는 탐험이라고 생각해 봐요!"
)

st.markdown("---")
st.subheader("1️⃣ 나의 MBTI를 선택해 줘!")

groups = {
    "🧩 분석가": ["INTJ", "INTP", "ENTJ", "ENTP"],
    "🌱 외교관": ["INFJ", "INFP", "ENFJ", "ENFP"],
    "🛡️ 관리자": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
    "🎨 탐험가": ["ISTP", "ISFP", "ESTP", "ESFP"]
}

selected = st.session_state.get("selected_mbti", "INFP")

for group_name, types in groups.items():
    st.markdown(f"#### {group_name}")
    cols = st.columns(4)

    for i, mbti in enumerate(types):
        with cols[i]:
            if st.button(
                mbti,
                key=f"btn_{mbti}",
                use_container_width=True
            ):
                st.session_state["selected_mbti"] = mbti

selected = st.session_state.get("selected_mbti", "INFP")
title, intro = type_info[selected]

st.markdown("---")
st.markdown(f"## {selected} | {title}")
st.markdown(f"<div class='tip'>✨ {intro}</div>", unsafe_allow_html=True)
st.markdown("### 2️⃣ 추천 진로를 확인해 봐!")

# 중복 데이터가 있더라도 화면에 같은 직업이 반복되지 않도록 방어
shown = set()
recommendations = []

for career in careers[selected]:
    if career["name"] not in shown:
        recommendations.append(career)
        shown.add(career["name"])

for index, career in enumerate(recommendations[:2], start=1):
    st.markdown(
        f"### {career['emoji']} 추천 진로 {index}: {career['name']}"
    )

    st.markdown("<div class='career-card'>", unsafe_allow_html=True)
    st.markdown(f"**📝 어떤 일을 할까?**  \n{career['description']}")
    st.markdown(f"**🎓 관련 학과**  \n{career['major']}")
    st.markdown(f"**🧠 도움이 되는 성격·역량**  \n{career['personality']}")
    st.markdown(f"**💪 중요 역량**  \n{career['skill']}")
    st.markdown(f"**💰 참고용 연봉**  \n{career['salary']}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("🌱 진로 탐색 꿀팁")
st.info(
    "MBTI는 성격을 이해하는 여러 방법 중 하나예요. "
    "특정 MBTI에 반드시 어울리는 직업이 정해져 있는 것은 아니랍니다. "
    "관심 분야, 잘하는 일, 가치관, 실제 경험도 함께 고려해 보세요!"
)

st.caption(
    "💡 연봉은 실제 최신 공식 통계를 직접 조회한 값이 아닌 참고용 예시입니다. "
    "직업별 실제 임금은 경력, 근무 지역, 기업 규모, 자격 및 고용 형태에 따라 달라집니다."
)

st.markdown(
    "📚 실제 직업별 임금 확인: "
    "[임금직업포털 워크피디아](https://www.wagework.go.kr/)"
)
```
