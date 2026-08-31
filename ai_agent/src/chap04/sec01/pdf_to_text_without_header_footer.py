import pymupdf
import os

# pdf_file_path : vsCode에서 실행시(Run python File)
# pdf_file_path /c/workspaces/ai_agent/src 를 기준으로 상대 path로 이동 ../
pdf_file_path = '../data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf'
doc = pymupdf.open(pdf_file_path)

header_height = 80
footer_height = 80

full_text = ""

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

