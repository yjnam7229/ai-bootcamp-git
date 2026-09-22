import os
import sys
import uuid
import logging
import streamlit as st

# 현재 파일(main.py)의 디렉터리 경로를 모듈 검색 경로에 최우선 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from agent import run_sales_agent

# 표준 로거 설정
logger = logging.getLogger(__name__)

# 1. Page Config (페이지 기본 설정)
st.set_page_config(
    page_title="DART-SalesGPT | B2B Financial Intelligence Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 세션 상태(Session State) 초기화
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 제안서를 작성할 **기업명**과 **제안 요구사항**을 자유롭게 입력해 주세요. 💼"
        }
    ]

# 3. 사이드바 내비게이션 구성
# 3. 사이드바 내비게이션 구성
with st.sidebar:
    st.title("💼 DART-SalesGPT")
    st.caption("B2B 제안서 자동화 솔루션")
    st.markdown("---")

    # 메뉴 선택 (라디오 버튼)
    page_selection = st.radio(
        "메뉴 선택",
        options=["🏠 홈", "💬 제안서 생성 챗봇"],
        index=0,
        key="navigation_menu",
        label_visibility="collapsed"
    )

    # 🔥 챗봇 페이지일 때만 상단에 '새 대화' 버튼 노출
    if page_selection == "💬 제안서 생성 챗봇":
        st.markdown("---")
        if st.button("🔄 대화 초기화", use_container_width=False, type="secondary"):
            st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "안녕하세요! 제안서를 작성할 **기업명**과 **제안 요구사항**을 자유롭게 입력해 주세요. 💼"
                }
            ]
            st.rerun()

    # st.markdown("---")

# 4. 페이지 렌더링 분기 처리

# [A] 홈 페이지
if page_selection == "🏠 홈":
    st.title("🏠 DART 재무 분석 기반 제안서 자동화")
    st.caption("DART 공시 데이터를 정밀 분석하여 경영진을 설득하는 맞춤형 제안서를 자동 생성합니다.")
    st.markdown("---")

    # 가치 전달 메트릭 카드 ('기업 과제 도출' 반영)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📊 재무 진단", value="DART API 연동", delta="3개년 재무제표 분석")
    with col2:
        st.metric(label="💡 핵심 명분", value="기업 과제 도출", delta="정량적 ROI 산출")
    with col3:
        st.metric(label="📄 제안서 완결", value="문서 자동화", delta=".pdf 파일 즉시 생성")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 한 줄 요약 배너
    # st.info("💡 **DART 재무 분석 기반, 경영진을 설득하는 B2B 제안서 자동 생성**")

    st.markdown("---")
    st.subheader("🚀 시작하기")
    st.markdown("좌측 사이드바의 **[💬 제안서 생성 챗봇]** 메뉴에서 제안서 작성을 시작하세요.")

# [B] 제안서 생성 챗봇 페이지 (자연어 기업명 파싱 처리 방식)
elif page_selection == "💬 제안서 생성 챗봇":
    st.title("💬 제안서 작성 에이전트")
    # st.caption("DART 재무 분석 기반 B2B 맞춤 제안서 자동화")
    st.divider()

    # 대화 기록 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 간결한 자연어 채팅 입력창
    if user_input := st.chat_input("기업명 및 제안 요구사항을 입력하세요 (예: 카카오 차세대 ERP 구축 제안서 작성해줘)"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("DART 재무 지표 분석 및 B2B 제안 논리 구성 중..."):
                try:
                    # 백엔드 run_sales_agent 내부에서 user_input으로부터 기업명 파싱 및 corp_code 매핑 수행
                    response_text = run_sales_agent(
                        company_name="",
                        stock_code="",
                        additional_requirements=user_input,
                        thread_id=st.session_state.thread_id
                    )
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

                except Exception as e:
                    error_msg = f"⚠️ 제안서 생성 중 오류가 발생했습니다: {e}"
                    st.error(error_msg)
                    logger.error(f"Chat Execution Error: {e}", exc_info=True)