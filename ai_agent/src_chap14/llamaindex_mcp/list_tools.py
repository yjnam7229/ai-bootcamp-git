# list_tools.py
# 라마인덱스(LlamaIndex) MCP

import json
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
# MCP 서버 연결
mcp_client = BasicMCPClient("http://localhost:8000/mcp")
mcp_tool_spec = McpToolSpec(client=mcp_client)

tools = mcp_tool_spec.to_tool_list()

for tool in tools:
    tool_dict = {
        "name": tool.metadata.name,                     # summarize_text
        "description": tool.metadata.description,       # 서버의 @mcp.tool()안에 별도의 descrption이 정의 안됨(doc string 내용이 에이전트의 descrption으로 전달)
        "parameters": json.loads(tool.metadata.fn_schema_str)
    }

    print(json.dumps(tool_dict, indent=2, ensure_ascii=False))

