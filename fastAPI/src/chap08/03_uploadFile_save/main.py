# UploadFile 객체
from fastapi import FastAPI, File, UploadFile
from pathlib import Path
import shutil

app = FastAPI()

@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile=File(...)):
    folder_name = 'uploaded_files'
    Path(folder_name).mkdir(exist_ok=True)  # 폴더가 없다면 생성
    file_location = f'{folder_name}/{file.filename}'

    # 읽기 쓰기 포인터를 파일의 시작 위치로 이동
    file.file.seek(0)

    # 업로드된 파일을 서버에 저장
    # wb+는 이진 모드로 파일을 쓰고 읽을 수 있음
    with open(file_location, 'wb+') as buffer: 
        shutil.copyfileobj(file.file, buffer)  # 파일의 내용을 buffer에 복사

    return {'Info': f'Your file {file.file.name} has been uploaded at {file_location}'}    
