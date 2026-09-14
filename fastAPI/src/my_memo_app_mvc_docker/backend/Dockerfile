# backend/Dockerfile
FROM python:3.10-slim

# Docker 이미지가 만들어지는 과정에서 Linux 패키지와 c/c+ 계열 코드 설치
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 컨테이너 안에서 작업할 기본 폴더를 /app로 지정  backend:/app
WORKDIR /app

COPY  requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# backend/ -> /app/
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


