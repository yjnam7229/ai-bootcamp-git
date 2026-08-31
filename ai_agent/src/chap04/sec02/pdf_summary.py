import pymupdf
import os
from openai import OpenAI
from dotenv import load_dotenv
import pymupdf

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

def pdf_to_text(pdf_file_path: str):
    # pdf_file_path /c/workspaces/ai_agent/src 를 기준으로 상대 path로 이동 ../
    # pdf_file_path = '../data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf'
    doc = pymupdf.open(pdf_file_path)

    header_height = 80
    footer_height = 80

    full_text = ''

    for page in doc:
        rect = page.rect # 현재 페이지의 크기 가져오기

        header = page.get_text(clip=(0, 0, rect.width, header_height)) # clip 영역의 위치 값
        footer = page.get_text(clip=(0, rect.height - footer_height, rect.width, rect.height))
        text = page.get_text(clip=(0, header_height, rect.width, rect.height - footer_height))

        full_text += text + '\n---------------------------------------------------------------\n'

    pdf_file_name = os.path.basename(pdf_file_path)  # 파일명 추출
    pdf_file_name = os.path.splitext(pdf_file_name)[0] # 확장자 뺀 파일명만 추출

    text_file_path = f"../output/{pdf_file_name}_with_preprocessing.txt" # 텍스트 저장

    # 파일 시스템으로 저장
    with open(text_file_path, 'w', encoding='utf-8') as f:  # 연결 통로 생성(스트림), 단방향 스트림
        f.write(full_text)

    return text_file_path 


def sumarrize_txt(file_path: str):
    client = OpenAI(api_key=api_key)

    # 주어진 텍스트 파일을 읽어들인다.
    with open(file_path, 'r', encoding='utf-8') as f:
        txt = f.read()

    # 요약을 위한 시스템 프롬프트를 생성한다.
    system_prompt = f'''
                    너는 다음 글을 요약하는 봇이야. 아래 글을 읽고, 저자의 문제 인식과 주장을 파악하고, 주요 내용을 요약하라. 

                    작성해야 하는 포맷을 다음과 같다.
                    
                    # 제목

                    ## 저자의 문제 인식과 주장(15문장 이내)

                    ## 저자 소개

                    ====================== 이하 텍스트 ====================== 
                   { txt }
                    '''
    print(system_prompt)
    print('=======================================================')

    # OpenAI API를 사용하여 요약을 생성한다
    response = client.chat.completions.create(
        model = 'gpt-5-nano',
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )

    return response.choices[0].message.content

# 두 함수 연결
def summarize_pdf(pdf_file_path: str, output_file_path: str):
    txt_file_path = pdf_to_text(pdf_file_path)
    summary = sumarrize_txt(txt_file_path)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(summary)


if __name__ == '__main__':
    pdf_file_path = '../data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf'
    # output_file_path = '../output/gpt-5-nano_model_summary.txt'

    pdf_file_name = os.path.basename(pdf_file_path)  # 파일명 추출
    pdf_file_name = os.path.splitext(pdf_file_name)[0] # 확장자 뺀 파일명만 추출

    output_file_path = f"../output/{pdf_file_name}_summary.txt" # 연관성 있는 파일명으로 저장

    summarize_pdf(pdf_file_path, output_file_path)
