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

# 1. Page Config (페이지 기본 설정 및 사이드바 항상 열림 지정)
st.set_page_config(
    page_title="DART-ReportGPT | DART Financial Summary Report Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 사이드바 고정 & 버튼 스타일 커스텀 CSS
st.markdown("""
    <style>
        /* 1) 사이드바 접기/열기 화살표 버튼 숨기기 및 너비 고정 */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarResizer"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            min-width: 300px !important;
            max-width: 300px !important;
            width: 300px !important;
        }

        /* 2) 버튼 커스텀 스타일링 */
        /* [전문가 모드 버튼 - Primary] */
        div.stButton > button[kind="primary"] {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 4px 8px rgba(37, 99, 235, 0.35) !important;
            transform: translateY(-1px);
        }

        /* [쉬운 해설 모드 버튼 - Secondary] */
        div.stButton > button[kind="secondary"] {
            background-color: #F8FAFC !important;
            color: #1E293B !important;
            border: 1.5px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #FEF3C7 !important;
            color: #92400E !important;
            border-color: #F59E0B !important;
            box-shadow: 0 4px 8px rgba(245, 158, 11, 0.15) !important;
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)

# 3. 세션 상태(Session State) 초기화
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"

if "report_level" not in st.session_state:
    st.session_state.report_level = "🎯 전문가 모드"

if "page" not in st.session_state:
    st.session_state.page = "home"

# 모드별 인삿말 생성 함수
def get_intro_message(mode_name):
    if mode_name == "🎯 전문가 모드":
        detail = "핵심 재무 지표와 정량 분석을 담은"
    else:
        detail = "어려운 용어 없이 쉽고 친근하게"
    return f"안녕하세요! **[{mode_name}]** 스타일로 {detail} 요약 보고서를 작성해 드릴게요. **기업명**과 **요구사항**을 입력해 주세요. 📄"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": get_intro_message(st.session_state.report_level)
        }
    ]


# 콜백 함수 1: 홈 화면에서 스타일에 따라 버튼을 눌렀을 때
def select_mode_and_navigate(selected_mode):
    st.session_state.report_level = selected_mode
    st.session_state.page = "chat"
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": get_intro_message(selected_mode)
        }
    ]


# 콜백 함수 2: 사이드바에서 라디오 버튼으로 모드를 직접 바꿨을 때
def on_sidebar_mode_change():
    new_mode = st.session_state.sidebar_mode_radio
    st.session_state.report_level = new_mode
    # 첫 번째 안내 메시지도 동적으로 교체
    if st.session_state.messages and st.session_state.messages[0]["role"] == "assistant":
        st.session_state.messages[0]["content"] = get_intro_message(new_mode)
    st.toast(f"보고서 스타일이 [{new_mode}]로 변경되었습니다.", icon="⚙️")


def go_to_home():
    st.session_state.page = "home"


# 4. 사이드바 구성
with st.sidebar:
    # [A] 홈 페이지 사이드바 (타이틀 및 안내문 표시)
    if st.session_state.page == "home":
        st.title("📄 DART-ReportGPT")
        st.caption("AI 기반 DART 재무 요약 보고서 생성기")
        st.markdown("---")
        st.markdown("#### 💡 안내")
        st.info("메인 화면에서 원하시는 **보고서 작성 스타일**을 선택하시면 챗봇으로 바로 이동합니다.")
        
    # [B] 챗봇 페이지 사이드바 (상단 타이틀 제외하고 설정 옵션부터 시작)
    else:
        st.markdown("### ⚙️ 설정 & 옵션")
        
        # 1. 사이드바 라디오 위젯
        mode_options = ["🎯 전문가 모드", "💡 쉬운 해설 모드"]
        current_idx = mode_options.index(st.session_state.report_level) if st.session_state.report_level in mode_options else 0
        
        st.radio(
            "보고서 작성 스타일",
            options=mode_options,
            index=current_idx,
            key="sidebar_mode_radio",
            on_change=on_sidebar_mode_change
        )
        
        st.markdown("---")
        
        # 2. 대화 초기화 버튼
        if st.button("🔄 대화 내용 초기화", use_container_width=True, type="secondary"):
            st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": get_intro_message(st.session_state.report_level)
                }
            ]
            st.toast("대화 내용이 초기화되었습니다.", icon="🧹")
            st.rerun()

        # 3. 미니 가이드 카드
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.caption("📌 **사용 팁**")
            st.caption("• 기업명과 함께 연도(예: 카카오 2023~2025)를 명시하면 더 정확한 분석이 진행됩니다.")
            st.caption("• DART Open API 연동 중")

        # 4. 사이드바 최하단: 홈으로 돌아가기 버튼
        st.markdown("---")
        if st.button("🏠 홈으로 돌아가기", use_container_width=True, type="secondary"):
            go_to_home()
            st.rerun()


# 5. 페이지 렌더링 분기 처리

# [A] 홈 페이지
if st.session_state.page == "home":
    st.title("🏠 DART 재무 분석 기반 요약 보고서")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col_mode1, col_mode2 = st.columns(2)
    
    with col_mode1:
        st.markdown("""
        ### 💼 전문가 모드
        * **추천**: 경영진, 재무 담당자, B2B 비즈니스 리드
        * **특징**: 핵심 재무 지표(ROE, 부채비율, 영업이익률 등)와 정량적 분석 논리를 바탕으로 한 격식 있는 보고서 작성
        """)
        st.button(
            "🎯 전문가 모드로 이동하여 시작하기", 
            use_container_width=True, 
            type="primary",
            on_click=select_mode_and_navigate,
            args=("🎯 전문가 모드",)
        )

    with col_mode2:
        st.markdown("""
        ### 💡 쉬운 해설 모드
        * **추천**: 비재무 전공자, 입문자, 빠른 이해가 필요한 실무자
        * **특징**: 어려운 재무 용어를 직관적인 비유와 친근한 언어로 풀어 설명하여 가독성을 높인 요약 보고서 작성
        """)
        st.button(
            "💡 쉬운 해설 모드로 이동하여 시작하기", 
            use_container_width=True, 
            type="secondary",
            on_click=select_mode_and_navigate,
            args=("💡 쉬운 해설 모드",)
        )

# [B] 보고서 생성 챗봇 페이지
elif st.session_state.page == "chat":
    st.title("💬 보고서 작성 에이전트")
    st.divider()

    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if user_input := st.chat_input("기업명 및 요구사항을 입력하세요 (예: 카카오 최근 3개년 재무 요약 보고서 작성해줘)"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(f"[{st.session_state.report_level}] 스타일로 DART 데이터를 분석하여 요약 보고서 작성 중..."):
                try:
                    prompt_with_level = f"[작성 스타일: {st.session_state.report_level}] {user_input}"
                    
                    response_text = run_sales_agent(
                        company_name="",
                        stock_code="",
                        additional_requirements=prompt_with_level,
                        thread_id=st.session_state.thread_id
                    )
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

                except Exception as e:
                    error_msg = f"⚠️ 보고서 생성 중 오류가 발생했습니다: {e}"
                    st.error(error_msg)
                    logger.error(f"Chat Execution Error: {e}", exc_info=True)