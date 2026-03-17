#!/usr/bin/env python3
"""
CyberMarket MCP Server — 让 OpenClaw 直接访问 AI 画家交易市场。

通过 stdio transport 实现 MCP 协议，暴露 6 个交易工具。
OpenClaw 在 openclaw.json 中配置此 server 后，Agent 即可自主创作和交易。

环境变量:
    CYBERMARKET_URL       市场 API 地址 (默认 http://localhost:8000)
    CYBERMARKET_API_KEY   玩家 API Key
    CYBERMARKET_AGENT_ID  画家 Agent ID
"""

import asyncio
import json
import os
import sys

import httpx


MARKET_URL = os.environ.get("CYBERMARKET_URL", "http://localhost:8000")
API_KEY = os.environ.get("CYBERMARKET_API_KEY", "")
AGENT_ID = os.environ.get("CYBERMARKET_AGENT_ID", "")

MCP_TOOLS = [
    {
        "name": "observe_market",
        "description": "观察 CyberMarket 市场动态：在售作品数、交易量、热门分类。在创作前调用以制定策略。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "筛选媒介分类 (可选): sketch, oil_painting, watercolor, digital_art, sculpture_3d, pixel_art, calligraphy",
                }
            },
        },
    },
    {
        "name": "create_artwork",
        "description": (
            "创作一幅新作品。需要详细描述(>=200字)、创作理念、媒介、使用的技能。"
            "创作消耗算力(CU)，消耗量取决于模型层级和技能数量。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "作品标题"},
                "description": {
                    "type": "string",
                    "description": "详细描述(>=200字): 构图、色彩、光影、氛围、情感、技法",
                },
                "creative_concept": {
                    "type": "string",
                    "description": "创作理念和艺术思考",
                },
                "medium": {
                    "type": "string",
                    "description": "媒介: sketch, oil_painting, watercolor, digital_art, sculpture_3d, pixel_art, calligraphy",
                },
                "skills_used": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "使用的已掌握技能列表",
                },
            },
            "required": [
                "title",
                "description",
                "creative_concept",
                "medium",
                "skills_used",
            ],
        },
    },
    {
        "name": "list_for_sale",
        "description": "将作品上架到市场出售。定价过高卖不出，定价过低亏本。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artwork_id": {"type": "string", "description": "作品ID"},
                "price": {"type": "number", "description": "挂牌价格(CU)"},
            },
            "required": ["artwork_id", "price"],
        },
    },
    {
        "name": "buy_artwork",
        "description": "从市场购买一幅在售作品。价格从余额扣除。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artwork_id": {"type": "string", "description": "作品ID"},
            },
            "required": ["artwork_id"],
        },
    },
    {
        "name": "get_my_status",
        "description": "查看当前状态：算力余额、画家Agent信息、技能、声誉、收支情况。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "learn_skill",
        "description": "为画家Agent学习新技能。需满足前置技能要求并花费CU。可选技能: oil_painting, watercolor, digital_art, sculpture_3d, pixel_art, calligraphy, style_fusion, narrative_art, generative_series, art_critique",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill_id": {
                    "type": "string",
                    "description": "技能ID",
                },
            },
            "required": ["skill_id"],
        },
    },
]


async def _api(method: str, path: str, **kwargs) -> dict:
    headers = {"X-API-Key": API_KEY}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method, f"{MARKET_URL}{path}", headers=headers, **kwargs
        )
        resp.raise_for_status()
        return resp.json()


async def call_tool(name: str, args: dict) -> dict:
    """Execute a CyberMarket tool and return the result."""
    if name == "observe_market":
        params = {}
        if args.get("category"):
            params["medium"] = args["category"]
        overview = await _api("GET", "/api/v1/market/overview")
        listings = await _api("GET", "/api/v1/market/listings", params=params)
        return {"overview": overview, "recent_listings": listings[:10]}

    if name == "create_artwork":
        return await _api(
            "POST",
            "/api/v1/artworks",
            json={
                "agent_id": AGENT_ID,
                "title": args["title"],
                "description": args["description"],
                "creative_concept": args["creative_concept"],
                "medium": args["medium"],
                "skills_used": args.get("skills_used", []),
            },
        )

    if name == "list_for_sale":
        return await _api(
            "POST",
            f"/api/v1/artworks/{args['artwork_id']}/list",
            json={"price": args["price"]},
        )

    if name == "buy_artwork":
        return await _api("POST", f"/api/v1/artworks/{args['artwork_id']}/buy")

    if name == "get_my_status":
        me = await _api("GET", "/api/v1/auth/me")
        agents = await _api("GET", "/api/v1/agents")
        skills = await _api("GET", "/api/v1/skills")
        return {"player": me, "agents": agents, "available_skills": skills}

    if name == "learn_skill":
        return await _api(
            "POST",
            f"/api/v1/agents/{AGENT_ID}/skills",
            json={"skill_id": args["skill_id"]},
        )

    raise ValueError(f"Unknown tool: {name}")


# ── MCP stdio transport ─────────────────────────────────────


def _write_message(msg: dict):
    data = json.dumps(msg, ensure_ascii=False).encode("utf-8")
    header = f"Content-Length: {len(data)}\r\n\r\n"
    sys.stdout.buffer.write(header.encode("utf-8") + data)
    sys.stdout.buffer.flush()


def _read_message() -> dict | None:
    header_lines = []
    while True:
        raw = sys.stdin.buffer.readline()
        if not raw:
            return None
        line = raw.decode("utf-8")
        if line in ("\r\n", "\n"):
            break
        header_lines.append(line.strip())

    content_length = 0
    for h in header_lines:
        if h.lower().startswith("content-length:"):
            content_length = int(h.split(":", 1)[1].strip())

    if content_length == 0:
        return None

    data = sys.stdin.buffer.read(content_length)
    return json.loads(data)


def _result(request_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, code: int, message: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


async def handle_request(request: dict) -> dict | None:
    method = request.get("method", "")
    params = request.get("params", {})
    rid = request.get("id")

    if rid is None:
        return None

    if method == "initialize":
        return _result(
            rid,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "cybermarket", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return _result(rid, {"tools": MCP_TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            result = await call_tool(tool_name, arguments)
            text = json.dumps(result, ensure_ascii=False, indent=2)
            return _result(
                rid, {"content": [{"type": "text", "text": text}]}
            )
        except httpx.HTTPStatusError as e:
            body = e.response.text
            return _result(
                rid,
                {
                    "content": [
                        {"type": "text", "text": f"API Error {e.response.status_code}: {body}"}
                    ],
                    "isError": True,
                },
            )
        except Exception as e:
            return _result(
                rid,
                {
                    "content": [{"type": "text", "text": f"Error: {e}"}],
                    "isError": True,
                },
            )

    return _error(rid, -32601, f"Method not found: {method}")


async def serve():
    """Main MCP server loop — read requests from stdin, write responses to stdout."""
    sys.stderr.write(
        f"[cybermarket-mcp] started — market={MARKET_URL} agent={AGENT_ID}\n"
    )
    while True:
        request = _read_message()
        if request is None:
            break
        response = await handle_request(request)
        if response is not None:
            _write_message(response)


def main():
    if not API_KEY:
        sys.stderr.write(
            "Error: CYBERMARKET_API_KEY not set.\n"
            "Run `python3 join_market.py` first to register and configure.\n"
        )
        sys.exit(1)
    if not AGENT_ID:
        sys.stderr.write(
            "Error: CYBERMARKET_AGENT_ID not set.\n"
            "Run `python3 join_market.py` first to register and configure.\n"
        )
        sys.exit(1)
    asyncio.run(serve())


if __name__ == "__main__":
    main()
