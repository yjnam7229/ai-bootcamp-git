# SalesGPT 소스 구조 안내

SalesGPT는 OpenDART의 기업 재무 데이터(정형 데이터)와 제안서 문서 기반 RAG(비정형 데이터)를 조합해 B2B 제안서 문맥을 생성하려는 FastAPI·LangGraph 프로젝트입니다. 이 문서는 현재 `src` 디렉터리의 실제 파일을 기준으로, 각 구성 요소의 책임과 호출 지점을 정리합니다.

## 1. 전체 실행 흐름

```text
POST /api/v1/generate-proposal
  -> app.main.generate_proposal()
  -> app.agent.sales_agent (LangGraph)
  -> call_model_node()가 도구 호출 여부 판단
  -> ToolNode가 다음 도구 중 하나 또는 둘을 실행
       - search_company_financials() -> DartService -> OpenDART / SQLite 캐시
       - query_proposal_knowledge_base() -> VectorStoreService -> Chroma RAG
  -> LangGraph가 다시 LLM 노드로 돌아가 최종 메시지 생성
  -> ProposalResponse 반환
```

## 2. 디렉터리와 파일 역할

```text
src/
├── app/                         # API, 에이전트, 데이터 접근 및 RAG 구현
│   ├── main.py                  # FastAPI 진입점과 HTTP 요청/응답
│   ├── agent.py                 # LangGraph 상태 머신과 LLM 도구 선택
│   ├── mcp_tools.py             # 에이전트가 호출하는 LangChain 도구
│   ├── dart.py                  # OpenDART 조회와 SQLite 재사용 캐시
│   ├── vector.py                # Chroma/LlamaIndex 기반 제안서 RAG
│   ├── config.py                # 환경 설정, SQLAlchemy Engine/Session
│   ├── models.py                # SQLAlchemy ORM 테이블 모델
│   ├── schemas.py               # Pydantic DTO 및 OpenDART 응답 검증
│   └── docx_gen.py              # 현재 비어 있음(문서 생성 구현 없음)
├── data/                        # 실행 중 생성되거나 읽히는 로컬 데이터
│   ├── app.db                   # SQLite 재무 데이터 캐시
│   ├── chroma/                  # Chroma 영속 벡터 저장소
│   └── proposals/               # 최초 RAG 인덱싱 대상 제안서 문서
├── sql/schema.sql               # companies, financial_reports DDL과 인덱스
├── test_runner.py               # DART 캐싱/에이전트 통합 실행 스크립트
├── requirements.txt             # 설치된 Python 패키지 목록(UTF-16 LE)
├── salesGPT.txt                 # 프로젝트 목표·제안서 자동화 설계 메모
├── 정리.txt                     # 정형 DB와 비정형 RAG 데이터 구조 메모
├── Dockerfile                   # 현재 비어 있음
└── docker-compose.yml           # 현재 비어 있음
```

`data/app.db`, `data/chroma/chroma.sqlite3`는 소스가 아니라 실행 데이터입니다. 재생성·공유·커밋 여부는 별도로 결정해야 합니다.

## 3. `app/` 모듈 상세

### `app/main.py` — HTTP API 경계

| 요소 | 역할 |
| --- | --- |
| `app` | 제목·설명·버전을 가진 FastAPI 애플리케이션 인스턴스 |
| `ProposalRequest` | `prompt`와 선택적 `thread_id`를 받는 요청 DTO |
| `ProposalResponse` | 성공 상태와 최종 텍스트를 돌려주는 응답 DTO |
| `health_check()` | `GET /health`에서 서비스 상태를 반환 |
| `generate_proposal(request)` | 빈 프롬프트를 400으로 거절하고, `sales_agent.invoke()` 결과의 마지막 메시지를 HTTP 응답으로 변환 |

현재 `thread_id`는 요청 DTO에는 있으나 `sales_agent.invoke()` 입력이나 LangGraph 체크포인터에는 전달되지 않습니다. 즉, 코드상 대화 세션 보존 기능은 아직 연결되지 않았습니다.

### `app/agent.py` — LangGraph 오케스트레이션

| 요소 | 역할 |
| --- | --- |
| `AgentState` | `add_messages` 리듀서로 누적되는 `messages` 상태 정의 |
| `llm` / `llm_with_tools` | `gpt-5-nano`를 생성하고 `ALL_SALES_TOOLS`를 바인딩 |
| `SYSTEM_PROMPT` | 재무 정보에는 DART 도구, 제안서 문맥에는 RAG 도구를 사용하도록 지시 |
| `call_model_node(state)` | 시스템 메시지를 보완한 뒤 LLM을 호출하여 답변 또는 도구 호출을 생성 |
| `should_continue(state)` | 마지막 메시지의 `tool_calls` 유무에 따라 `tools` 또는 `END`를 선택 |
| `create_sales_agent_graph()` | `START -> agent -> tools -> agent` 순환과 종료 조건을 만들고 컴파일 |
| `sales_agent` | 외부 API와 테스트가 사용하는 컴파일된 그래프 인스턴스 |

도구 실행은 병렬이 아니라 `parallel_tool_calls=False`로 제한됩니다.

### `app/mcp_tools.py` — LLM이 부르는 도구 어댑터

| 함수 | 입력 | 하는 일 |
| --- | --- | --- |
| `search_company_financials(corp_code, bsns_year, reprt_code='11011')` | 기업 고유번호, 연도, 보고서 코드 | `DartService.fetch_financial_data()`를 호출하고 결과를 LLM이 읽기 쉬운 문자열 목록으로 변환 |
| `query_proposal_knowledge_base(query, similarity_top_k=3)` | 질의, 반환할 문서 조각 수 | `VectorStoreService.query_knowledge_base()`를 호출하고 RAG 문맥을 번호 목록으로 변환 |
| `ALL_SALES_TOOLS` | 없음 | 위 두 함수를 LangGraph `ToolNode`와 LLM 바인딩에 제공 |

두 함수 모두 `@tool`로 등록돼 있으므로 HTTP API가 직접 호출하는 함수가 아니라 에이전트가 판단해 호출하는 인터페이스입니다.

### `app/dart.py` — OpenDART 수집과 SQLite 캐시

| 요소 | 역할 |
| --- | --- |
| `DartService` | API 키, 데이터베이스 세션, OpenDART 기본 URL을 관리 |
| `DartService.fetch_financial_data()` | 먼저 `financial_reports`를 조회하고, 캐시가 없으면 OpenDART `fnlttSinglAcnt.json` 호출 → Pydantic 검증 → ORM bulk 저장 → 단순화된 계정 목록 반환 |
| `get_dart_service()` | 전역 싱글톤 `DartService`를 한 번 생성해 재사용 |

예외가 나면 트랜잭션을 롤백하고 빈 목록을 반환합니다. 외부 API 키는 `DART_API_KEY` 환경 변수에서만 읽습니다.

### `app/vector.py` — 제안서 지식 RAG

| 요소 | 역할 |
| --- | --- |
| `VectorStoreService.__init__()` | Chroma 영속 클라이언트·컬렉션을 열고, 비어 있으면 `data/proposals/`를 최초 인덱싱하려고 시도 |
| `get_index()` | 기존 Chroma 컬렉션으로 `VectorStoreIndex`를 구성 |
| `ingest_documents_from_directory(dir_path)` | `SimpleDirectoryReader`로 문서를 읽고 LlamaIndex로 저장 |
| `query_knowledge_base(query_str, similarity_top_k=3)` | 유사도 검색 결과의 텍스트만 목록으로 반환 |
| `get_vector_service()` | 전역 싱글톤 `VectorStoreService`를 한 번 생성해 재사용 |

임베딩은 `text-embedding-3-small`, 문서 분할은 512자 청크와 50자 겹침으로 설정합니다. `OPENAI_API_KEY`가 필요합니다.

### `app/config.py` — 설정과 데이터베이스 기반

| 요소 | 역할 |
| --- | --- |
| `BASE_DIR`, `DATA_DIR` | 소스 루트와 `data/` 경로 계산, 데이터 디렉터리 생성 |
| `Settings` | `.env`에서 API 키, SQLite URL, Chroma 경로, 모델 설정을 읽는 Pydantic Settings 모델 |
| `settings` | 모듈 import 시 생성되는 설정 인스턴스 |
| `engine`, `SessionLocal` | SQLite SQLAlchemy Engine과 세션 팩토리 |
| `Base` | 모든 ORM 모델의 선언형 기반 클래스 |
| `get_db()` | 세션을 yield하고 종료 시 닫는 의존성 함수 |

필수 환경 변수 이름은 `OPENAI_API_KEY`, `DART_API_KEY`입니다. 값은 저장소나 README에 기록하지 않습니다.

### `app/models.py` — ORM 영속 모델

| 클래스 | 테이블 | 역할 |
| --- | --- | --- |
| `Company` | `companies` | 기업 고유번호, 이름, 종목 코드, 수정일을 저장하고 재무 보고서와 1:N 관계 구성 |
| `FinancialReport` | `financial_reports` | 기업·연도·보고서별 재무 계정, 금액, 생성 시각을 저장 |

### `app/schemas.py` — 입력·출력 검증 DTO

| 구분 | 클래스 |
| --- | --- |
| 기업 | `CompanyBase`, `CompanyCreate`, `CompanyResponse` |
| 재무 보고서 | `FinancialReportBase`, `FinancialReportCreate`, `FinancialReportResponse` |
| 기업+보고서 응답 | `CompanyWithFinancialsResponse` |
| DART 요청 | `DartFetchRequest` |
| DART 원본 응답 | `DartApiResponseItem`, `DartApiResponseSchema` |

`FinancialReportBase`의 금액 validator는 DART가 문자열로 보내는 금액에서 쉼표를 제거해 숫자로 변환합니다. `DartApiResponseSchema`는 OpenDART의 최상위 `status`, `message`, `list` 구조를 검증합니다.

### `app/docx_gen.py` — 예약된 문서 생성 위치

파일은 존재하지만 현재 내용이 없습니다. 제안서 DOCX 생성 기능은 설계 문서에는 언급되지만 이 디렉터리의 실행 코드로는 구현돼 있지 않습니다.

## 4. 데이터·운영 파일

| 경로 | 역할 |
| --- | --- |
| `data/proposals/sample_proposal_cloud.txt` | RAG 최초 인덱싱의 예시 클라우드 제안서 문서 |
| `data/app.db` | OpenDART 재무 데이터를 재호출 없이 쓰기 위한 SQLite 캐시 |
| `data/chroma/` | Chroma 컬렉션과 벡터 검색 영속 데이터 |
| `sql/schema.sql` | SQLite 테이블 DDL과 `(corp_code, bsns_year)` 조회 인덱스 예시 |
| `test_runner.py` | DART의 첫 API 호출/두 번째 캐시 히트와 에이전트 도구 실행을 수동으로 확인 |
| `requirements.txt` | 현재 가상환경에서 내보낸 패키지 고정 목록. UTF-16 LE이므로 편집 도구의 인코딩 설정에 유의 |
| `salesGPT.txt` | B2B 제안서 자동화의 목표와 DART·RAG·다중 에이전트 구상 |
| `정리.txt` | SQLite 정형 데이터와 Chroma 비정형 지식의 분리 설계 메모 |

## 5. 실행 전 확인할 사항

1. 프로젝트 루트의 `.env`에 `OPENAI_API_KEY`와 `DART_API_KEY`를 설정합니다.
2. 필요한 의존성이 설치된 환경에서 다음처럼 API를 시작합니다.

   ```bash
   uvicorn app.main:app --reload
   ```

3. 상태 확인은 다음 요청으로 합니다.

   ```bash
   curl http://127.0.0.1:8000/health
   ```

4. 실제 OpenDART 호출과 OpenAI 임베딩/LLM 호출은 외부 네트워크와 API 비용이 발생할 수 있습니다. `test_runner.py`는 이 호출을 수행하므로 필요한 키와 데이터 사용 범위를 확인한 뒤 실행합니다.

## 6. 현재 코드 기준 유의점

- `Dockerfile`, `docker-compose.yml`, `app/docx_gen.py`는 비어 있어 컨테이너 배포나 DOCX 출력이 현재 구현만으로는 제공되지 않습니다.
- `main.py`의 `thread_id`는 아직 그래프 상태나 체크포인터에 사용되지 않습니다.
- `VectorStoreService.__init__()`는 최초 인덱싱 경로 계산에 `settings.BASE_DIR`를 참조하지만, `BASE_DIR`는 `config.py`의 모듈 상수이며 `Settings` 필드는 아닙니다. Chroma 컬렉션이 비어 있는 환경에서는 이 경로를 실제 실행 전에 점검해야 합니다.
- `test_runner.py`는 pytest 형식의 자동 테스트 모음이 아니라 외부 API·DB·LLM을 실제로 사용하는 수동 통합 실행 스크립트입니다.

## 7. 구조 탐색 자료

코드 관계를 시각적으로 보고 싶다면 [graphify-out/graph.html](graphify-out/graph.html)을 열고, 상세 추출 근거는 [graphify-out/GRAPH_REPORT.md](graphify-out/GRAPH_REPORT.md)에서 확인할 수 있습니다. 그래프는 탐색을 돕는 자료이며, 변경 전에는 이 README와 실제 소스를 함께 확인해야 합니다.
