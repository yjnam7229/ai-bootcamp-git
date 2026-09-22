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

# 1. Page Config (레이아웃 및 타이틀 설정)
st.set_page_config(
    page_title=f"{settings.PROJECT_NAME} - B2B Proposal Agent",
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
            "content": (
                "안녕하세요! B2B 영업 제안서 작성 에이전트 **SalesGPT**입니다. 💼\n\n"
                "제안서를 작성할 **기업명**과 **요구사항**을 자유롭게 입력해 주세요.\n\n"
                "*예시: '삼성전자 B2B 클라우드 전환 제안서 작성해줘. ISMS-P 보안 요건 반영 필수.'*"
            )
        }
    ]

# 3. 사이드바 내비게이션 구성
with st.sidebar:
    st.title("💼 SalesGPT")
    st.caption("B2B 제안서 자동 생성 시스템")
    
    st.markdown("---")
    
    # 내비게이션 메뉴 선택 (index=0 으로 변경하여 '🏠 홈'을 디폴트로 설정)
    page_selection = st.radio(
        "메뉴 선택",
        options=["🏠 홈", "💬 SalesGPT 챗봇"],
        index=0,
        key="navigation_menu",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 챗봇 페이지일 경우 세션 제어 옵션 추가 제공
    if page_selection == "💬 SalesGPT 챗봇":
        st.caption(f"**현재 세션 ID**:\n`{st.session_state.thread_id}`")
        if st.button("🔄 새 대화 시작하기", use_container_width=True, type="secondary"):
            st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "새로운 대화 세션이 시작되었습니다. 제안서를 작성할 기업명과 요구사항을 입력해 주세요!"
                }
            ]
            st.rerun()

# 4. 페이지 렌더링 분기 처리

# [A] 홈 페이지 (기본 선택 화면)
if page_selection == "🏠 홈":
    st.title("🏠 SalesGPT B2B Proposal Agent")
    st.subheader("실시간 DART 재무 데이터 & ChromaDB RAG 기반 제안서 생성 솔루션")
    
    st.markdown("""
    ---
    ### 🚀 주요 기능
    1. **DART 재무 데이터 자동 연동**: 기업명을 기반으로 실시간 재무제표 및 주요 지표를 자동 조회합니다.
    2. **ChromaDB RAG 지식베이스 구축**: 표준 B2B 제안서 템플릿, 아키텍처 가이드, 보안 규정 문서를 자동 탐색합니다.
    3. **LangGraph 세션 관리**: 대화 맥락을 `SqliteSaver` 체크포인터로 유지하여 지속적인 수정 요청을 반영합니다.
    
    ### 💡 사용 방법
    * 좌측 사이드바 메뉴에서 **[💬 SalesGPT 챗봇]**을 선택하여 제안서 작성을 시작하세요.
    """)

# [B] SalesGPT 챗봇 페이지
elif page_selection == "💬 SalesGPT 챗봇":
    st.title("💬 SalesGPT 챗봇")
    st.caption("DART 실시간 재무 데이터 & ChromaDB RAG 기반 B2B 제안서 작성 챗봇")
    st.divider()

    # 기존 대화 기록 화면 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력 및 에이전트 실행
    if user_input := st.chat_input("기업명 및 제안서 요구사항을 입력하세요..."):
        # 1. 사용자 메시지 추가 및 출력
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Assistant 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("DART 재무 정보 조회 및 RAG 지식베이스 검색 중..."):
                try:
                    # agent.py의 run_sales_agent 직접 호출
                    response_text = run_sales_agent(
                        company_name=user_input,
                        stock_code="",
                        additional_requirements=user_input,
                        thread_id=st.session_state.thread_id
                    )
                    
                    st.markdown(response_text)
                    
                    # 대화 기록 저장
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

                except Exception as e:
                    error_msg = f"⚠️ 제안서 생성 중 오류가 발생했습니다: {e}"
                    st.error(error_msg)
                    logger.error(f"Chat Execution Error: {e}", exc_info=True)