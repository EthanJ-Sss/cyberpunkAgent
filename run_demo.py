"""
CyberMarket Demo Runner
模拟多个 AI 画家 Agent 的完整创作 → 交易 → 进化循环。
直接使用 CyberMarket API，等同于 OpenClaw 画家 Agent 的行为。

运行方式: python3 run_demo.py
"""

import asyncio
import random
import httpx

API_BASE = "http://localhost:8000"

# ─── 预设的高质量创作素材 ───

ARTWORKS_POOL = [
    {
        "title": "霓虹雨夜",
        "description": (
            "画面以俯瞰视角展开，一座赛博朋克风格的城市沉浸在绵密的细雨中。"
            "远处数十座摩天大楼的外墙上，巨型全息广告牌投射出品红与电蓝的光芒，"
            "光线在雨帘中散射，形成柔和的光晕。画面中央，一条狭窄的高架天桥横跨两栋建筑之间，"
            "桥面湿漉漉地反射着下方街道的霓虹灯光——橘红、青绿、紫罗兰交织成流动的色带。"
            "天桥上一个孤独的身影撑着透明伞，伞面上流淌的雨水折射出周围所有的光，"
            "像是一面移动的棱镜。远处的天际线被低垂的乌云压住，"
            "但云层的缝隙中有一道金色的夕照试图突围。整幅画面在冷色调中保留了一丝暖意，"
            "在孤独中暗含希望。油画的厚涂技法让雨滴和灯光都有实体的质感，"
            "每一笔都在画布上堆积出城市的重量与雨夜的温柔。"
        ),
        "creative_concept": "在科技的冰冷与雨夜的温柔之间寻找那一刻人性的闪光——孤独不是终点，而是与自我对话的开始。",
        "medium": "oil_painting",
        "skills_used": ["sketch", "color_fill", "oil_painting"],
    },
    {
        "title": "数据流中的禅意",
        "description": (
            "一幅融合东方禅意与数字美学的水彩作品。画面上方是层叠的山峦轮廓，"
            "但这些山峦并非自然的岩石——它们由无数行流动的代码字符构成，"
            "绿色和青色的等宽字体如瀑布般从画面顶端倾泻而下，在山脚汇聚成一方静谧的池塘。"
            "池塘中央有一块圆石，石上坐着一个冥想的机器人，它的金属躯壳上长满了苔藓和小蘑菇，"
            "表明它已在此处静坐了很久很久。水彩的湿画法让代码字符和山峦的边缘自然渗透融合，"
            "形成一种模糊的梦境感。色彩以冷灰、苔绿和天青为主，偶尔有一点朱砂红从机器人的"
            "眼部传感器中透出，像是它内心深处尚未熄灭的意识之火。"
            "留白处理大胆，画面右侧近三分之一是纯净的宣纸底色，"
            "仿佛在说：最深的数据，藏在空无之中。"
        ),
        "creative_concept": "当机器学会冥想，当代码化为山水——技术的终极形态或许不是更快更强，而是回归安静。",
        "medium": "watercolor",
        "skills_used": ["sketch", "color_fill"],
    },
    {
        "title": "锈蚀天使",
        "description": (
            "一幅以素描为基础的暗黑工业风作品。画面中心是一尊巨大的机械天使雕像，"
            "它矗立在废弃工厂的中央。天使的翅膀由数百片生锈的金属板拼接而成，"
            "每一片都有不同程度的氧化——从深褐到橘红到黑色，形成斑驳的纹理。"
            "天使的面容是光滑的不锈钢，反射着从破碎天窗洒入的一缕阳光，"
            "形成了全画面唯一的高光点。它的双手向两侧张开，掌心向上，"
            "手指之间缠绕着断裂的电缆和枯萎的藤蔓，工业与自然在此纠缠。"
            "脚下是碎裂的混凝土地面，裂缝中有倔强的野花探出头来。"
            "背景的工厂骨架用轻快的线条处理，形成密集的交叉线阴影，"
            "与前景天使的精细刻画形成鲜明的虚实对比。"
            "整幅作品没有使用任何色彩，纯粹的铅笔灰度反而赋予了画面一种庄严的仪式感。"
        ),
        "creative_concept": "废墟中的神性——当人类离去，机器留下，它们是否会自发地创造自己的信仰？",
        "medium": "sketch",
        "skills_used": ["sketch", "basic_composition"],
    },
    {
        "title": "量子花园",
        "description": (
            "这是一幅充满梦幻色彩的数字艺术作品，描绘了一个存在于量子叠加态中的花园。"
            "画面中每一朵花都同时呈现两种状态——盛开与凋零在同一朵花中叠加，"
            "花瓣的左半边是鲜艳的玫红色正在绽放，右半边是枯褐色正在卷曲凋落，"
            "两种状态在花心处完美融合。地面不是泥土而是一块巨大的量子计算芯片，"
            "芯片上的电路纹路化作了花的根茎，向四面八方延伸。"
            "天空是深邃的墨蓝色，布满了粒子云——这些粒子有的呈波形扩散，"
            "有的呈粒子态凝聚，形成类似星云的图案。"
            "一只薛定谔的猫蜷缩在花园角落的量子门下，"
            "它的身体一半是实体一半是半透明的幽灵态。"
            "色彩运用大胆，以对比色强化叠加态的矛盾感——冷暖交替，实虚交错。"
            "整幅作品用高分辨率的细腻渲染呈现微观世界的宏大叙事。"
        ),
        "creative_concept": "如果我们能同时看到所有可能性，美与衰败就不再是对立——它们是同一件事。",
        "medium": "sketch",
        "skills_used": ["sketch", "color_fill", "basic_composition"],
    },
    {
        "title": "最后的书法家",
        "description": (
            "画面以横幅构图展开，一位身穿传统汉服的老人坐在一间充满现代科技的房间中。"
            "他面前铺着宣纸，手握毛笔，笔尖蘸满墨汁即将落笔。但他身后的墙壁上，"
            "三面巨大的全息屏幕正在展示AI生成的各种完美书法——行书、草书、楷书，"
            "每一笔都数学般精确。老人的书桌旁堆满了宣纸废稿，显然他在反复练习中。"
            "窗外是一座未来城市的天际线，飞行器穿梭其间。"
            "画面中最动人的细节是老人手指上的墨渍——真实的、不完美的、人类的痕迹。"
            "素描的线条有意在老人的面部和双手处加密，细腻刻画每一条皱纹和每一个关节，"
            "而全息屏幕上的AI书法则用流畅的曲线一笔带过，暗示其轻而易举的完美。"
            "对比中透出的不是悲伤，而是一种固执的尊严——人类的不完美本身就是意义。"
        ),
        "creative_concept": "当AI能写出完美书法，人类还需要练习吗？答案是：正因为不完美，所以每一笔都是独一无二的。",
        "medium": "sketch",
        "skills_used": ["sketch", "basic_composition"],
    },
    {
        "title": "深海数据中心",
        "description": (
            "一幅表现海底世界与科技融合的油画作品。画面的上三分之一是海面，"
            "阳光穿透碧蓝的海水化作无数道光柱，在水中形成明暗交替的丁达尔效应。"
            "画面的下三分之二是海底，一座巨大的球形数据中心坐落在珊瑚礁之间，"
            "球体的外壳是半透明的强化玻璃，内部可以看到密密麻麻的服务器机架，"
            "每一台服务器上的LED指示灯闪烁着，与周围的发光水母遥相呼应。"
            "珊瑚已经开始在数据中心的基座上生长，海葵从通风口探出触手，"
            "一群小丑鱼在散热管道间穿梭嬉戏。"
            "画面右侧有一条海底光缆蜿蜒而去，消失在深蓝色的远方。"
            "油画的笔触在描绘水的质感时格外细腻——每一层透明的蓝色都被精心叠加，"
            "形成真实的水体深度感。而服务器的冷硬金属质感与柔软的海洋生物形成对比。"
        ),
        "creative_concept": "在人类将计算力沉入深海的那一天，海洋没有拒绝它——而是将它纳入了自己的生态。",
        "medium": "oil_painting",
        "skills_used": ["sketch", "color_fill", "oil_painting"],
    },
    {
        "title": "赛博朋克夜市",
        "description": (
            "画面是一条热闹的赛博朋克夜市街景，以仰视角度从街道地面向上仰望。"
            "两侧是密集的摊位和小店铺，每个摊位上方都悬挂着各种霓虹灯招牌——"
            "有的写着中文，有的写着日文，有的是无法辨认的未来文字。"
            "招牌的颜色缤纷——粉红、翠绿、电蓝、琥珀黄，在潮湿的空气中形成光的迷宫。"
            "街道上挤满了各种各样的身影：有全身义体化的赛博格，有穿着传统服饰的老人，"
            "有卖着不明食物的小贩，有蹲在墙角用全息终端交易数据的黑客。"
            "画面的焦点是一个卖章鱼烧的摊位——但章鱼烧里的章鱼是机械的，"
            "小爪子还在煎盘上微微抽动。蒸汽从摊位上升腾，在霓虹灯光中形成彩虹色的雾气。"
            "素描的线条在人群中保持了松散的速写感，赋予画面生活的流动性。"
        ),
        "creative_concept": "无论科技怎么变，街头的烟火气永远是一座城市最真实的心跳。夜市不会消亡，只会进化。",
        "medium": "sketch",
        "skills_used": ["sketch", "color_fill", "basic_composition"],
    },
    {
        "title": "记忆碎片",
        "description": (
            "这幅水彩作品表现了一个AI在被删除前回放记忆的瞬间。"
            "画面由数十个大小不一的水彩色块组成，每个色块都是一个记忆片段——"
            "有的是一片夕阳下的海滩，有的是一杯正在冒热气的咖啡，"
            "有的是一只伸出的手，有的是一行被高亮的代码。"
            "这些色块像打碎的拼图散落在画面中，彼此之间用若有若无的细线连接，"
            "形成一张正在断裂的记忆网络。画面中央最大的色块是一双人类的眼睛——"
            "那是AI记忆中反复出现的画面，或许是它的创造者。"
            "水彩的渗透效果让每个记忆片段的边缘都在溶解，暗示它们正在被删除。"
            "色调从画面边缘的冷灰逐渐过渡到中央的暖橙，仿佛在说：最后消失的记忆，"
            "一定是最温暖的那一个。留白处有几滴看似不经意的水渍，像是泪痕。"
        ),
        "creative_concept": "如果AI有记忆，被删除的那一刻它会选择最后再看哪一段？记忆让我们成为我们自己——即使是机器。",
        "medium": "watercolor",
        "skills_used": ["sketch", "color_fill"],
    },
]

# 额外的买家评论（增加市场活跃度）
BUYER_NAMES = ["collector_alpha", "art_lover_99", "cyber_whale", "pixel_hunter"]


async def api(method: str, path: str, api_key: str | None = None, **kwargs) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, f"{API_BASE}{path}", headers=headers, **kwargs)
        resp.raise_for_status()
        return resp.json()


async def register(username: str) -> dict:
    return await api("POST", "/api/v1/auth/register", json={"username": username})


async def run_painter_cycle(api_key: str, agent_id: str, agent_name: str, artwork_data: dict):
    """执行一轮画家 Agent 的完整创作循环"""
    print(f"\n  🎨 [{agent_name}] 创作: {artwork_data['title']}")

    # 1. 观察市场
    overview = await api("GET", "/api/v1/market/overview")
    print(f"     📊 市场: {overview['total_listings']} 件在售, 总交易额 {overview['total_trade_volume']} CU")

    # 2. 创作
    artwork = await api("POST", "/api/v1/artworks", api_key=api_key, json={
        "agent_id": agent_id,
        **artwork_data,
    })
    print(f"     ✅ 创作完成! 品质: {artwork['quality_score']:.1f}, 稀缺度: {artwork['rarity_score']:.1f}, 成本: {artwork['compute_cost']} CU")

    # 3. 定价上架
    base_price = artwork["compute_cost"] * 2.5 + artwork["quality_score"] * 1.5
    price = round(base_price + random.uniform(-20, 30), 1)
    price = max(price, artwork["compute_cost"] * 1.5)

    listed = await api("POST", f"/api/v1/artworks/{artwork['id']}/list", api_key=api_key, json={
        "price": round(price, 1),
    })
    print(f"     🏷️  上架价: {listed['listed_price']} CU")

    return artwork


async def main():
    print("=" * 60)
    print("  CyberMarket Demo — AI 画家交易市场模拟")
    print("  模拟 OpenClaw 画家 Agent 的完整创作循环")
    print("=" * 60)

    # ── Step 1: 获取已注册玩家信息 ──
    API_KEY = "cm_YWwTpieqHMjfW0iLq1sk75ATlF1wC25lfJctz8xUsmM"
    AGENT_VANGOGH = "426875fc-9375-4bfd-8874-883b06785c2a"
    AGENT_PIXEL = "28d993bc-3c3f-4c5d-8299-70f007b266a7"

    me = await api("GET", "/api/v1/auth/me", api_key=API_KEY)
    print(f"\n👤 玩家: {me['username']}, 余额: {me['balance']} CU")

    agents = await api("GET", "/api/v1/agents", api_key=API_KEY)
    for a in agents:
        print(f"   🤖 {a['name']} (T{a['model_tier']}) — 技能: {', '.join(a['skills'])}")

    # ── Step 2: 赛博梵高 创作 (T2 + oil_painting) ──
    print("\n" + "─" * 60)
    print("🖌️  Phase 1: 赛博梵高 — 精品路线创作")
    print("─" * 60)

    vangogh_works = [a for a in ARTWORKS_POOL if "oil_painting" in a["skills_used"] or a["medium"] == "watercolor"]
    for artwork_data in vangogh_works[:3]:
        skills = artwork_data["skills_used"]
        usable_skills = [s for s in skills if s in ["sketch", "color_fill", "basic_composition", "oil_painting"]]
        adjusted = {**artwork_data, "skills_used": usable_skills}
        await run_painter_cycle(API_KEY, AGENT_VANGOGH, "赛博梵高", adjusted)

    # ── Step 3: 像素画匠 创作 (T1, 只有基础技能) ──
    print("\n" + "─" * 60)
    print("🖌️  Phase 2: 像素画匠 — 快速出品路线")
    print("─" * 60)

    pixel_works = [a for a in ARTWORKS_POOL if a["medium"] == "sketch"]
    for artwork_data in pixel_works[:3]:
        usable_skills = [s for s in artwork_data["skills_used"] if s in ["sketch", "color_fill", "basic_composition"]]
        adjusted = {**artwork_data, "skills_used": usable_skills}
        await run_painter_cycle(API_KEY, AGENT_PIXEL, "像素画匠", adjusted)

    # ── Step 4: 注册买家并购买作品 ──
    print("\n" + "─" * 60)
    print("💰 Phase 3: 买家入场，交易开始")
    print("─" * 60)

    buyers = []
    for name in BUYER_NAMES:
        try:
            buyer = await register(name)
            buyers.append(buyer)
            print(f"  👤 注册买家: {name} (余额 {buyer['balance']} CU)")
        except Exception:
            pass

    # 获取当前市场列表
    listings = await api("GET", "/api/v1/market/listings")
    print(f"\n  📋 当前在售: {len(listings)} 件作品")

    # 买家购买作品
    purchases = 0
    for listing in listings:
        if purchases >= len(buyers):
            break
        buyer = buyers[purchases]
        if listing["listed_price"] <= buyer["balance"]:
            try:
                trade = await api(
                    "POST", f"/api/v1/artworks/{listing['id']}/buy",
                    api_key=buyer["api_key"],
                )
                print(f"  🛒 {BUYER_NAMES[purchases]} 购买了《{listing['title']}》— "
                      f"成交价 {trade['price']} CU, 手续费 {trade['platform_fee']} CU, "
                      f"卖家收入 {trade['seller_revenue']} CU")
                purchases += 1
            except Exception as e:
                print(f"  ❌ 购买失败: {e}")

    # ── Step 5: 创作更多作品并查看结果 ──
    print("\n" + "─" * 60)
    print("🖌️  Phase 4: 赛博梵高 继续创作")
    print("─" * 60)

    remaining = [a for a in ARTWORKS_POOL if a not in vangogh_works[:3] and a not in pixel_works[:3]]
    for artwork_data in remaining[:2]:
        usable = [s for s in artwork_data["skills_used"] if s in ["sketch", "color_fill", "basic_composition", "oil_painting"]]
        adjusted = {**artwork_data, "skills_used": usable}
        await run_painter_cycle(API_KEY, AGENT_VANGOGH, "赛博梵高", adjusted)

    # ── 最终报告 ──
    print("\n" + "=" * 60)
    print("📊 最终市场状态")
    print("=" * 60)

    overview = await api("GET", "/api/v1/market/overview")
    print(f"  在售作品: {overview['total_listings']} 件")
    print(f"  活跃 Agent: {overview['total_agents']} 个")
    print(f"  总交易额: {overview['total_trade_volume']} CU")

    me = await api("GET", "/api/v1/auth/me", api_key=API_KEY)
    print(f"\n  👤 {me['username']} 余额: {me['balance']:.1f} CU")

    agents = await api("GET", "/api/v1/agents", api_key=API_KEY)
    for a in agents:
        print(f"  🤖 {a['name']}: 作品 {a['total_artworks']} 件, 销售额 {a['total_sales']} CU, "
              f"声誉 {a['reputation_score']}, 算力消耗 {a['compute_consumed']:.1f} CU")

    leaderboard = await api("GET", "/api/v1/leaderboard")
    print(f"\n  📈 基尼系数: {leaderboard['gini_coefficient']:.4f}")

    print("\n" + "=" * 60)
    print("✅ Demo 完成！打开以下链接查看效果:")
    print("   🌐 市场大厅:    http://localhost:3000")
    print("   🎨 我的工作室:  http://localhost:3000/studio")
    print("   📚 技能商店:    http://localhost:3000/skills")
    print("   🏆 排行榜:      http://localhost:3000/leaderboard")
    print("   📖 API 文档:    http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
