import asyncio 

async def func1():
    print('func1: Start')
    await asyncio.sleep(2)    # 비동기 상태로 2초간 대기
    print('func1: End')

async def func2():
    print('func2: Start')
    await asyncio.sleep(5)
    print('func2: End')

async def main():
    await asyncio.gather(func1(), func2())   # func1과 func2 동시에 실행

# 실행
if __name__ == '__main__':  
    asyncio.run(main())

