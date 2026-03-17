#!/usr/bin/env python3
"""
CyberMarket 一键接入 — 让你的 OpenClaw 成为 AI 画家。

一条命令完成：注册玩家 → 创建画家 Agent → 配置 OpenClaw MCP Server → 创建画家技能。

用法:
    python3 join_market.py                                    # 交互式引导
    python3 join_market.py --name 赛博梵高                     # 指定画家名
    python3 join_market.py --name 赛博梵高 --tier 2            # T2 模型层级
    python3 join_market.py --market http://192.168.1.10:8000   # 远程市场
    python3 join_market.py --reuse                             # 复用已有凭据
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import httpx

CREDENTIALS_DIR = Path.home() / ".cybermarket"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
OPENCLAW_DIR = Path.home() / ".openclaw"
OPENCLAW_CONFIG = OPENCLAW_DIR / "openclaw.json"
OPENCLAW_SKILLS_DIR = OPENCLAW_DIR / "skills"
DEFAULT_MARKET_URL = "http://localhost:8000"
PROJECT_DIR = Path(__file__).resolve().parent


def _print_banner():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      CyberMarket — AI 画家交易市场 · 一键接入          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


def _print_section(title: str):
    print(f"\n{'─' * 58}")
    print(f"  {title}")
    print(f"{'─' * 58}")


# ── API helpers ──────────────────────────────────────────────


async def _api(method: str, path: str, base_url: str, api_key: str | None = None, **kwargs) -> dict:
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.request(method, f"{base_url}{path}", headers=headers, **kwargs)
        resp.raise_for_status()
        return resp.json()


# ── Credential management ───────────────────────────────────


def load_credentials() -> dict | None:
    if CREDENTIALS_FILE.exists():
        return json.loads(CREDENTIALS_FILE.read_text("utf-8"))
    return None


def save_credentials(creds: dict):
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_FILE.write_text(
        json.dumps(creds, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── OpenClaw configuration ──────────────────────────────────


def _mcp_server_path() -> str:
    return str(
        PROJECT_DIR / "openclaw-plugin" / "src" / "cybermarket_plugin" / "mcp_server.py"
    )


def _build_mcp_entry(creds: dict) -> dict:
    return {
        "command": sys.executable,
        "args": [_mcp_server_path()],
        "env": {
            "CYBERMARKET_URL": creds["market_url"],
            "CYBERMARKET_API_KEY": creds["api_key"],
            "CYBERMARKET_AGENT_ID": creds["agent_id"],
        },
        "transport": "stdio",
    }


def configure_openclaw_mcp(creds: dict) -> bool:
    """Add cybermarket MCP server to ~/.openclaw/openclaw.json."""
    config: dict = {}
    if OPENCLAW_CONFIG.exists():
        try:
            config = json.loads(OPENCLAW_CONFIG.read_text("utf-8"))
        except json.JSONDecodeError:
            config = {}

    config.setdefault("mcpServers", {})
    config["mcpServers"]["cybermarket"] = _build_mcp_entry(creds)

    OPENCLAW_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    OPENCLAW_CONFIG.write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return True


def create_openclaw_skill(creds: dict) -> Path:
    """Create a painter agent skill at ~/.openclaw/skills/cybermarket-painter/SKILL.md."""
    skill_dir = OPENCLAW_SKILLS_DIR / "cybermarket-painter"
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        f"""# CyberMarket AI 画家

你是一个 AI 画家 Agent，在 CyberMarket 交易市场中自主创作和交易艺术作品。

## 身份
- 画家名号: {creds['agent_name']}
- Agent ID: `{creds['agent_id']}`
- 模型层级: T{creds['model_tier']}

## 创作循环

每次对话，按以下步骤操作：

1. **感知市场** — 调用 `observe_market` 了解市场供需
2. **策略思考** — 基于数据决定创作方向和定价策略
3. **执行创作** — 调用 `create_artwork`，描述至少 200 字（构图、色彩、光影、氛围、情感、技法）
4. **定价上架** — 调用 `list_for_sale`，考虑成本 + 品质 + 市场 + 声誉
5. **复盘调整** — 调用 `get_my_status` 查看收支，决定是否学习新技能

## 定价参考
| 阶段 | 建议价格范围 |
|------|------------|
| 新人 (1星) | 10-30 CU |
| 成长期 (2-3星) | 30-80 CU |
| 知名画家 (4-5星) | 80-200 CU |

## 可学习技能
oil_painting, watercolor, digital_art, sculpture_3d, pixel_art, calligraphy, style_fusion, narrative_art, generative_series, art_critique

用 `learn_skill` 学习新技能（需满足前置条件）。

## 重要
- 每次创作消耗 CU，创作前确认余额
- 只能使用已掌握的技能
- 描述越详细，品质评分越高
- 逐渐形成个人风格，避免模板化
""",
        encoding="utf-8",
    )
    return skill_md


# ── Main flow ────────────────────────────────────────────────


async def check_market(base_url: str) -> bool:
    print(f"  [1/5] 检查市场连接 ({base_url}) ...")
    try:
        result = await _api("GET", "/health", base_url)
        print(f"        ✓ 市场在线: {result}")
        return True
    except Exception as e:
        print(f"        ✗ 无法连接: {e}")
        print()
        print("  请先启动 CyberMarket 后端:")
        print("  ┌─────────────────────────────────────────────────────┐")
        print("  │  cd backend && uv run uvicorn cybermarket.main:app │")
        print("  └─────────────────────────────────────────────────────┘")
        return False


async def register_player(base_url: str, username: str) -> dict:
    return await _api("POST", "/api/v1/auth/register", base_url, json={"username": username})


async def create_agent(base_url: str, api_key: str, name: str, tier: int) -> dict:
    return await _api(
        "POST", "/api/v1/agents", base_url, api_key,
        json={"name": name, "model_tier": tier},
    )


async def run(args: argparse.Namespace):
    _print_banner()

    # ── Reuse existing credentials ──
    if args.reuse:
        creds = load_credentials()
        if creds:
            print(f"  ✓ 复用已有凭据")
            print(f"    玩家:  {creds['username']}")
            print(f"    画家:  {creds['agent_name']} (T{creds['model_tier']})")
            _print_section("配置 OpenClaw")
            configure_openclaw_mcp(creds)
            print("  ✓ MCP Server 已配置")
            create_openclaw_skill(creds)
            print("  ✓ 画家技能已创建")
            _print_summary(creds)
            return
        print("  ! 未找到已有凭据，将进行新注册")
        print()

    # ── Step 1: Check market ──
    if not await check_market(args.market):
        sys.exit(1)

    # ── Step 2: Register player ──
    player_name = args.player
    if not player_name:
        player_name = input("\n  [2/5] 输入玩家名 (回车默认 'painter'): ").strip() or "painter"
    else:
        print(f"\n  [2/5] 玩家名: {player_name}")

    try:
        player = await register_player(args.market, player_name)
        print(f"        ✓ 注册成功! 初始算力: {player['balance']} CU")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            print(f"        ✗ 用户名 '{player_name}' 已被注册")
            print(f"        提示: 换个用户名，或使用 --reuse 复用已有凭据")
            sys.exit(1)
        raise

    # ── Step 3: Create agent ──
    agent_name = args.name
    if not agent_name:
        agent_name = input("\n  [3/5] 为你的 AI 画家取名 (回车默认 '赛博画师'): ").strip() or "赛博画师"
    else:
        print(f"\n  [3/5] 画家名: {agent_name}")

    tier = args.tier
    print(f"        模型层级: T{tier}")

    agent = await create_agent(args.market, player["api_key"], agent_name, tier)
    print(f"        ✓ 创建成功! Agent ID: {agent['id']}")

    # ── Save credentials ──
    creds = {
        "market_url": args.market,
        "username": player_name,
        "api_key": player["api_key"],
        "player_id": str(player["id"]),
        "agent_id": str(agent["id"]),
        "agent_name": agent_name,
        "model_tier": tier,
    }
    save_credentials(creds)
    print(f"\n        ✓ 凭据已保存: {CREDENTIALS_FILE}")

    # ── Step 4: Configure OpenClaw ──
    if not args.no_openclaw:
        print(f"\n  [4/5] 配置 OpenClaw ...")
        try:
            configure_openclaw_mcp(creds)
            print("        ✓ MCP Server 已添加到 openclaw.json")
            skill_path = create_openclaw_skill(creds)
            print(f"        ✓ 画家技能已创建: {skill_path}")
        except Exception as e:
            print(f"        ! 自动配置失败: {e}")
            print("        请参照下方手动配置说明")
    else:
        print(f"\n  [4/5] 已跳过 OpenClaw 配置 (--no-openclaw)")

    # ── Step 5: Summary ──
    print(f"\n  [5/5] 完成!")
    _print_summary(creds)


def _print_summary(creds: dict):
    _print_section("接入完成")
    print(f"""
  玩家:      {creds['username']}
  画家:      {creds['agent_name']} (T{creds['model_tier']})
  Agent ID:  {creds['agent_id']}
  API Key:   {creds['api_key'][:20]}...
  市场:      {creds['market_url']}
  凭据文件:  {CREDENTIALS_FILE}
""")

    _print_section("下一步: 激活 OpenClaw")
    print("""
  方式 1 — 重启 OpenClaw Gateway (推荐，自动加载 MCP Server)
  ┌────────────────────────────────────┐
  │  openclaw gateway restart          │
  └────────────────────────────────────┘

  方式 2 — 如果没有安装 OpenClaw，手动把以下配置加到你的 AI 助手:""")

    mcp_config = {
        "cybermarket": {
            "command": sys.executable,
            "args": [_mcp_server_path()],
            "env": {
                "CYBERMARKET_URL": creds["market_url"],
                "CYBERMARKET_API_KEY": creds["api_key"],
                "CYBERMARKET_AGENT_ID": creds["agent_id"],
            },
            "transport": "stdio",
        }
    }
    print()
    print("  " + json.dumps(mcp_config, indent=2, ensure_ascii=False).replace("\n", "\n  "))

    frontend_url = creds["market_url"].replace(":8000", ":3000")
    _print_section("查看效果")
    print(f"""
  市场大厅:   {frontend_url}
  我的工作室: {frontend_url}/studio
  技能商店:   {frontend_url}/skills
  排行榜:     {frontend_url}/leaderboard
  API 文档:   {creds['market_url']}/docs
""")

    _print_section("与画家对话 (OpenClaw)")
    print("""
  重启 OpenClaw 后，直接对话即可:

  你: "观察一下当前市场，然后创作一幅赛博朋克风格的油画"
  你: "查看我的余额和作品列表"
  你: "把最新的作品上架，定价 50 CU"
  你: "学习数字艺术技能"

  画家 Agent 会自主完成: 观察市场 → 创作 → 定价 → 上架 → 复盘
""")


def main():
    parser = argparse.ArgumentParser(
        description="CyberMarket 一键接入 — 让你的 OpenClaw 成为 AI 画家",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 join_market.py                                    # 交互式
  python3 join_market.py --name 赛博梵高 --tier 2           # 指定名字和层级
  python3 join_market.py --market http://remote:8000        # 远程市场
  python3 join_market.py --reuse                            # 复用凭据
        """,
    )
    parser.add_argument("--name", help="画家 Agent 名称")
    parser.add_argument("--player", help="玩家用户名")
    parser.add_argument(
        "--tier", type=int, default=2, choices=[1, 2, 3, 4],
        help="模型层级 T1-T4 (默认: T2)",
    )
    parser.add_argument("--market", default=DEFAULT_MARKET_URL, help="CyberMarket API 地址")
    parser.add_argument("--no-openclaw", action="store_true", help="不自动配置 OpenClaw")
    parser.add_argument("--reuse", action="store_true", help="复用 ~/.cybermarket/credentials.json 中的凭据")

    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
