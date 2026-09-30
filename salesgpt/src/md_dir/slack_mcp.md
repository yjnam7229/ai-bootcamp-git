# Slack MCP 연동

## 목적

재무분석 결과를 Slack에 업무용 요약으로 공유

## 구조

``` text
Streamlit
  ↓
LangGraph Agent
  ├─ OpenDART MCP → 재무정보 조회
  └─ Slack MCP    → 분석 결과 공유
```

## Slack 설정

1.  [Slack App 생성](https://api.slack.com/apps)
2.  User Token에 `chat:write` 권한 추가
3.  [Slack MCP Server 활성화
    가이드](https://docs.slack.dev/ai/slack-mcp-server/developing/)
    -   Slack App → Agents → Slack MCP Server 활성화
4.  `.env`에 Token / Channel ID 설정
5.  LangGraph Agent에 `slack_send_message` Tool 등록

> 참고: [Slack MCP Server 공식
> 문서](https://docs.slack.dev/ai/slack-mcp-server/)

## 구현

-   `MultiServerMCPClient`에 Slack MCP 추가
-   Slack Tool 중 `slack_send_message`만 Agent에 등록
-   프롬프트에 Slack 공유 규칙 추가

## 동작

``` text
"삼성전자 재무분석하고 Slack에 공유해줘"
        ↓
OpenDART MCP 조회
        ↓
재무분석
        ↓
Slack용 핵심 요약
        ↓
Slack MCP 전송
```

## 결과

-   자체 OpenDART MCP + 외부 Slack MCP 연동
-   하나의 LangGraph Agent가 두 MCP Tool을 선택·실행
-   Streamlit은 상세 분석, Slack은 핵심 요약 제공
