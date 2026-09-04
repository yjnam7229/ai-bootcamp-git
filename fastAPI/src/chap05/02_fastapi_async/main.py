from fastapi import FastAPI
import asyncio

app = FastAPI()

async def fetch_data():
    await asyncio.sleep(2)
    return {'data': 'some data'}


@app.get('/')
async def read_root():
    data = await fetch_data()
    return {'message': 'Hellow, World!', 'fetch data': data}

# 비동기 처리를 하면 단일 쓰레드에서 여러 작업을 효율적으로 수행할 수 있음
