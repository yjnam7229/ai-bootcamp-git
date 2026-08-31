# file_server.py
# 파일 읽기 도구 만들기
# FastMCP로 간단한 서버 만들기(스스로 행동하는 AI를 위한 도구)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('FileManager') # 서버 도구에 접근을 위한 고유 이름

# @mcp.tool 데코레이터
# MCP 서버 = MCP 도구
# MCP 서버에 도구 등록(에이전트에게 제공할 컨텍스트(context)를 가지고 있는 주체)
@mcp.tool('read_file', description='파일을 읽어 내용을 반환합니다.')
def read_file(path): 
    """
    지정된 경로의 파일을 읽어 내용을 반환합니다.
    Args:
    path: 읽을 파일의 경로 (예: './data/report.txt')
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error : '{path}' 파일을 찾을 수 없습니다."
    except Exception as e:
        return f"Error: 파일을 읽는 중 오류가 발생했습니다. {str(e)}"
    

@mcp.tool('write_file', description='저장된 경로에 내용을 파일로 저장합니다.')
def write_file(path, content):
    """
    지정된 경로에 내용을 파일로 저장합니다.
    (이미 존재하는 파일이면 덮어씁니다.)

    Args:
        path: 저장한 파일의 경로
        content: 파일에 작성할 텍스트 내용
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{path}'"    
    except Exception as e:
        return f"Error: 파일 저장 중 오류가 발생했습니다. {str(e)}"

# 이 파일이 직접 실행될 때 서버가 켜지도록 설정
# stdio : Standard I/O
if __name__ == '__main__':
    mcp.run(transport='stdio')  

# mcp.run(transport=“stdio”)가 핵심
# 이는 서버를 인터넷(HTTP)이 아닌, 표준 입출력(Standard I/O) 방식으로 실행하겠다는 뜻 
# 로컬에서 에이전트와 빠르고 안전하게 통신하기 위해 주로 사용되는 방식



