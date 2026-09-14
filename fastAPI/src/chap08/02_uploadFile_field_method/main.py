# main.py
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile=File(...)):
    # 파일 이름과 콘텐츠 타입 출력
    print("파일 이름:", file.filename)
    print("콘텐츠 타입:", file.content_type)

    # 파일 읽기(비동기)
    contents = await file.read()
    print("파일 크기:", len(contents))

    # 파일 포인터를 처음으로 이동
    await file.seek(0)

    # 파일 내용 다시 읽기(비동기)
    contents_again = await file.read()
    print("파일 크기(다시 읽기):", len(contents_again))

    # 파일 리소스 해제
    await file.close()

    return {"filename": file.filename}



