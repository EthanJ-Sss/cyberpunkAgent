# Trumen Legos — 技术结构路径

> 基于 Project Trumen 概念框架的模块化技术路径规划
> 整理日期：2026-03-04

---

## 架构总览

Trumen Legos 将整个系统拆分为三大核心模块：**World Engine（世界引擎）**、**World Creation（世界创建）** 和 **Agent（智能体）**。每个模块下包含若干技术条目，条目前的数字为该条目的优先级（数字越小优先级越高）。

```
                        ┌── Customizable World Architecture ·········· P1
                        │
                        ├── World Simulation ························· P1
          World Engine ─┤
                        │                  ┌─ Animatable 3D Generation ··· P2
                        │  Visualization   ├─ Animatable 2D Generation ··· P2
                        │  and Expression  └─ Scene/Layout Generation ···· P2
                        │
                        └── World Evolution
                            └─ Rule/Logic Generation ················· P2

                        ┌── Agentic Workflow ························· P2
         World Creation ┤
                        └── Generation Capabilities (Offline) ······· P2

                        ┌── Unified Multi-Agent Framework ··········· P1
                        ├── Memory ·································· P1
              Agent ────┤
                        ├── Personality ····························· P2
                        └── Digital Identity ························ P2
```

---

## 一、World Engine（世界引擎）

世界引擎是整个 Trumen 系统的运行基座，负责世界的架构定义、仿真运行和内容演化。

### 1.1 Customizable World Architecture（可定制世界架构）

| 属性 | 内容 |
|------|------|
| **优先级** | P1 |
| **目标** | 设计一个模块化、可扩展的世界架构，使规则（rules）、实体（entities）、环境（environments）和交互模式（interaction patterns）能够被配置、组合和演化，而无需修改核心系统 |
| **核心价值** | 作为所有世界变体的底层骨架，决定系统的扩展上限 |

### 1.2 World Simulation（世界仿真）

| 属性 | 内容 |
|------|------|
| **优先级** | P1 |
| **目标** | 构建一个稳定且连贯的仿真环境，使多个 Agent 和世界实体在既定规则下进行交互，支持随时间推移的连续状态转换 |
| **核心价值** | 世界引擎的运行时核心，保障仿真的稳定性与一致性 |

### 1.3 World Evolution（世界演化）

World Evolution 包含两大子方向：**可视化与表达（Visualization and Expression）** 和 **规则/逻辑生成（Rule/Logic Generation）**。

#### 1.3.1 Visualization and Expression（可视化与表达）

##### Animatable 3D Generation（可动画化 3D 生成）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 开发一条可扩展的 3D 资产生成管线，产出结构一致、可绑定骨骼（riggable）、可驱动动画（animation-ready）的模型，适用于动态世界仿真 |

##### Animatable 2D Generation（可动画化 2D 生成）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 开发一条可扩展的 2D 资产生成管线，产出结构分层、可驱动动画的角色和物件，适用于动态世界交互 |

##### Scene/Layout Generation（场景/布局生成）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 开发一套场景和布局生成系统，产出连贯、可导航、支持交互的空间环境，适用于动态世界仿真 |

#### 1.3.2 Rule/Logic Generation（规则/逻辑生成）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 开发一个灵活的规则和逻辑生成框架，支持世界规则的动态创建、修改和组合，同时保持逻辑一致性和系统稳定性 |
| **核心价值** | 使世界能够自我演化，而非仅依赖人工预设规则 |

---

## 二、World Creation（世界创建）

世界创建模块为用户提供构建和配置世界的工具与工作流。

### 2.1 Agentic Workflow（Agent 驱动的创建工作流）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 设计一套由 Agent 驱动的创建工作流，通过迭代式交互（而非纯手动构建）协助用户生成、配置和精炼世界 |
| **核心价值** | 降低世界创建门槛，让非技术用户也能参与世界构建 |

### 2.2 Generation Capabilities in Offline Mode（离线生成能力）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 在离线模式下提供世界内容的生成能力 |
| **关联** | 链接至 **World Evolution**，复用演化模块中的生成管线 |

---

## 三、Agent（智能体）

Agent 模块定义了在 Trumen 世界中运行的智能体的核心架构与能力。

### 3.1 Unified Multi-Agent Framework（统一多智能体框架）

| 属性 | 内容 |
|------|------|
| **优先级** | P1 |
| **目标** | 建立一个统一架构，使多个 Agent 能够在共享世界中感知（perceive）、推理（reason）、行动（act）和交互（interact），并遵循一致的协调框架 |
| **核心价值** | Agent 能力的基座，决定多智能体协作与竞争的上限 |

### 3.2 Memory（记忆系统）

| 属性 | 内容 |
|------|------|
| **优先级** | P1 |
| **目标** | 设计一套结构化的记忆系统，使 Agent 能够保留（retain）、检索（retrieve）和利用（utilize）过往经验，以影响未来的决策和交互 |
| **核心价值** | 记忆是 Agent 从「反应式」走向「反思式」的关键分水岭 |

### 3.3 Personality（人格系统）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 开发一套可控的人格生成工作流，产出多样化且行为一致的人格档案，具备类人的性格特质、情感倾向和决策模式 |
| **核心价值** | 赋予 Agent 差异化的个体特征，是涌现行为多样性的基础 |

### 3.4 Digital Identity（数字身份）

| 属性 | 内容 |
|------|------|
| **优先级** | P2 |
| **目标** | 建立一个持久的数字身份框架，将每个玩家表征为世界中一致、可演化的存在，支持长期连续性、交互和个性化 |
| **核心价值** | 连接玩家与 Agent 世界的持久化桥梁 |

---

## 四、优先级总览

按优先级排列所有技术条目：

| 优先级 | 模块 | 条目 | 战略意义 |
|--------|------|------|----------|
| **P1** | World Engine | Customizable World Architecture | 系统基座，扩展性根基 |
| **P1** | World Engine | World Simulation | 运行时核心，仿真稳定性保障 |
| **P1** | Agent | Unified Multi-Agent Framework | 多智能体协调基座 |
| **P1** | Agent | Memory | Agent 记忆与经验系统 |
| **P2** | World Engine | Animatable 3D Generation | 3D 内容管线，世界视觉呈现 |
| **P2** | World Engine | Animatable 2D Generation | 2D 内容管线，轻量级视觉方案 |
| **P2** | World Engine | Scene/Layout Generation | 空间环境生成 |
| **P2** | World Engine | Rule/Logic Generation | 世界自演化核心能力 |
| **P2** | World Creation | Agentic Workflow | Agent 驱动的世界构建工具 |
| **P2** | World Creation | Generation Capabilities (Offline) | 离线内容生成 |
| **P2** | Agent | Personality | Agent 个体差异化基础 |
| **P2** | Agent | Digital Identity | 玩家持久化身份 |

---

## 五、模块依赖关系

```
World Engine
  ├── Customizable World Architecture (P1)
  │     └──→ 为 World Simulation 提供可配置的世界定义
  ├── World Simulation (P1)
  │     └──→ 为 Agent 提供运行环境，为 World Evolution 提供演化基底
  └── World Evolution
        ├── Visualization and Expression
        │     ├── 3D Generation (P2) ─────→ 为仿真世界提供 3D 资产
        │     ├── 2D Generation (P2) ─────→ 为仿真世界提供 2D 资产
        │     └── Scene/Layout (P2) ──────→ 为仿真世界提供空间布局
        └── Rule/Logic Generation (P2) ───→ 为世界演化提供规则动态生成能力

World Creation
  ├── Agentic Workflow (P2) ──→ 调用 World Engine 能力构建世界
  └── Offline Generation (P2) ─→ 复用 World Evolution 的生成管线

Agent
  ├── Unified Multi-Agent Framework (P1) ──→ 运行于 World Simulation 之上
  ├── Memory (P1) ─────────────────────────→ 存储 Agent 在世界中的经验
  ├── Personality (P2) ────────────────────→ 定义 Agent 行为特征
  └── Digital Identity (P2) ───────────────→ 连接玩家与 Agent 世界
```

---

*本文档基于 Trumen Legos 思维导图整理，作为项目技术结构路径的参考。*
