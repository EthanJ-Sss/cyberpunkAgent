CYBERMARKET_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "observe_market",
            "description": "观察 CyberMarket 当前市场情况：在售作品数量、交易量趋势、热门分类。用于在创作前了解市场供需，制定创作策略。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "可选，筛选特定媒介分类。可选值：sketch, oil_painting, watercolor, digital_art, sculpture_3d, pixel_art, calligraphy",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_artwork",
            "description": "创作一幅新的艺术作品。需要提供详细的作品描述（至少200字，包含构图、色彩、氛围、情感、技法细节）、创作理念和使用的技能。创作会消耗算力（CU），消耗量取决于模型层级和使用的技能数量。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "作品标题，简洁有力",
                    },
                    "description": {
                        "type": "string",
                        "description": "详细的作品描述，至少200字。包含：画面构图、色彩搭配、光影效果、氛围意境、情感表达、技法运用等细节",
                    },
                    "creative_concept": {
                        "type": "string",
                        "description": "创作理念，阐述创作动机和艺术思考",
                    },
                    "medium": {
                        "type": "string",
                        "description": "媒介类型。可选：sketch, oil_painting, watercolor, digital_art, sculpture_3d, pixel_art, calligraphy",
                    },
                    "skills_used": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "创作使用的技能列表，必须是已掌握的技能",
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
    },
    {
        "type": "function",
        "function": {
            "name": "list_for_sale",
            "description": "将已创作的作品上架到市场出售。需要设定合理的挂牌价格（CU），定价过高可能卖不出去，定价过低则亏本。",
            "parameters": {
                "type": "object",
                "properties": {
                    "artwork_id": {
                        "type": "string",
                        "description": "要上架的作品ID",
                    },
                    "price": {
                        "type": "number",
                        "description": "挂牌价格（CU）",
                    },
                },
                "required": ["artwork_id", "price"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buy_artwork",
            "description": "从市场购买一幅在售作品。价格从余额中扣除，购买后可用于学习和欣赏。",
            "parameters": {
                "type": "object",
                "properties": {
                    "artwork_id": {
                        "type": "string",
                        "description": "要购买的作品ID",
                    },
                },
                "required": ["artwork_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_status",
            "description": "查看自身当前状态：算力余额（CU）、拥有的画家Agent、每个Agent的技能和声誉等级、收支情况。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "learn_skill",
            "description": "为画家Agent购买/学习一项新的绘画技能。需要满足前置技能要求，并花费相应的CU。新技能解锁新的创作可能性。",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "要学习技能的Agent ID",
                    },
                    "skill_id": {
                        "type": "string",
                        "description": "要学习的技能ID。可选：oil_painting, watercolor, digital_art, sculpture_3d, pixel_art, calligraphy, style_fusion, narrative_art, generative_series, art_critique",
                    },
                },
                "required": ["agent_id", "skill_id"],
            },
        },
    },
]
