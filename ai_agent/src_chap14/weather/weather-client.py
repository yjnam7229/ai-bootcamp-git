# weather-client.py
from dotenv import load_dotenv
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
# llama인덱스에서 OpenAI 기반 모델을 사용하기 위한 레퍼 클래스
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent
# MCP 는 비동기로 처리
import asyncio

# 환경변수 로드
load_dotenv()

# MCP 서버 연결
mcp_client = BasicMCPClient('http://localhost:8000/mcp')

# MCP 도구를 LlamaIndex용으로 변환
tool_spec = McpToolSpec(client=mcp_client)

# FunctionTool 리스트 획득  
tools = tool_spec.to_tool_list()

# LLM 설정
llm = OpenAI(model='gpt-4o-mini')

prompt = """당신은 날씨 정보를 알려주는 에이전트입니다.
    사용자가 질문한 도시와 시간(오늘/내일)에 따라 적절한 날씨 도구를 호출해야 합니다.
    도시명을 사용할 때는 영어로 변환된 도시명을 사용하며,
    사용자에게 반환하는 답변은 항상 한국어로 자연스럽게 작성합니다.
"""

# FuctionAgent 생성
agent = FunctionAgent(
    tools=tools,
    llm=llm,
    system_prompt=prompt
)

async def run_agent():
    questions = [
        '오늘 날씨 어떄?',
        '서울 이에요',
        '내일 부산 날씨는?'
    ]

    for q in questions:
        print(f'사용자: {q}')
        result = await agent.run(q)
        print(f'에이전트: {result}')

if __name__ == '__main__':
    asyncio.run(run_agent())



