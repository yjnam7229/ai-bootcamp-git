# main.py
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile = File(...)): # ... 입력값은 필수값이다.
    return {'filename': file.filename}

 



