from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()


template = """
주어진 사용자 질문을 `유튜브`, `동물병원`, `보험`, 또는 `기타` 중 하나로 분류하세요.
이외의 답변은 허용하지 않습니다.
<question>
{question}
</question>

<answer example>
유튜브
</answer example>
"""

classifier_prompt = PromptTemplate.from_template(template)
model = ChatOpenAI(model="gpt-5-nano")
output_parser = StrOutputParser()

# classifier_chain 체인 정의
classifier_chain = classifier_prompt | model | output_parser

# result = classifier_chain.invoke({"question": "2+2 는 무엇인가요?"})

# 개별 체인 생성
# 유튜브 → youtube_chain
youtube_chain = PromptTemplate.from_template(
    """
      당신은 유튜브 전문가입니다.
      항상 다음과 같이 답변을 시작합니다. "유튜브 크리에이터 및 마케팅 관점에서 말씀드리면…"


      다음 질문에 답변하시오:

      질문: {question}
      답변:
    """
)

# 동물병원 → hospital_chain
hospital_chain = PromptTemplate.from_template(
    """
       당신은 동물병원 전문가입니다.
       항상 다음과 같이 답변을 시작합니다. "동물병원 전문가 관점에서 말씀드리면…"


       다음 질문에 답변하시오:

       질문: {question}
       답변:
    """
)

# 보험 → insurance_chain
insurance_chain = PromptTemplate.from_template(
    """
       당신은 보험 전문가입니다.
       항상 다음과 같이 답변을 시작합니다. "보험 전문가 관점에서 말씀드리면…"


       다음 질문에 답변하시오:

       질문: {question}
       답변:
    """
)

# 기타 → general_chain
general_chain = PromptTemplate.from_template(
    """
       당신은 기타 전문가입니다.
       항상 다음과 같이 답변을 시작합니다. "기타 전문가 관점에서 말씀드리면…"


       다음 질문에 답변하시오:

       질문: {question}
       답변:
    """
)

# router_chain 함수


