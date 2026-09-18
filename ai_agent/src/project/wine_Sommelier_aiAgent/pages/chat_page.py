import asyncio

import streamlit as st
from dotenv import load_dotenv

from agent_builder import execute_agent


# ============================================================
# 환경변수
# ============================================================

load_dotenv()


# ============================================================
# 페이지
# ============================================================

st.subheader("💬 와인 챗봇")


# ============================================================
# Session State
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# 기존 대화 출력
# ============================================================

for message in st.session_state.messages:
    speaker = (
        "user"
        if message["role"] == "user"
        else "assistant"
    )

    with st.chat_message(speaker):
        st.markdown(message["content"])


# ============================================================
# 사용자 입력
# ============================================================

THREAD_ID = "wine_agent"

prompt = st.chat_input(
    "와인에 대해 물어보세요..."
)


# ============================================================
# Agent 실행
# ============================================================

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        try:
            with st.spinner("답변 생성 중..."):

                response = asyncio.run(
                    execute_agent(
                        query=prompt,
                        thread_id=THREAD_ID,
                    )
                )

            if response:

                st.markdown(response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

            else:

                st.warning(
                    "Agent가 응답을 생성하지 못했습니다."
                )

        except KeyboardInterrupt:

            print(
                "\n[SHUTDOWN] Ctrl+C detected."
            )

            raise

        except asyncio.CancelledError:

            print(
                "\n[SHUTDOWN] Task cancelled."
            )

            raise

        except Exception as e:

            st.error(
                f"Agent 실행 중 오류가 발생했습니다: {e}"
            )
