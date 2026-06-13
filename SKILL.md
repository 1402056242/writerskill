---
name: wuhang-long-all-pro
description: Run Wuhang's full long-form web novel pipeline—project init, boundary analysis, ideation, outline, writing, and optional review checkpoints. Use when the user asks for 武行全流程, 武行长篇全流程, long web novel workflow, loading the Wuhang novel kit, or initializing a new long-novel project.
---

# wuhang-long-all-pro

## 触发词

用户说以下内容时，可加载本 SKILL 进入全流程模式：
- **加载武行技能** / **武行长篇全流程skill**
- **我想写一本长篇网络小说** / **我想写长篇**
- **我想写一本小说**（并确认为长篇）
- **加载武行小说技能包** / **项目初始化**（从零开始写长篇时）

**只做某一阶段？**  
用户若只明确某一阶段（如「我只要写大纲」），不要走全流程，提示其直接加载对应技能文件（本包根目录下的 `wuhang-*.md`）。

---

## 🧩 Story System 简版约定（全流程共享约束）

本技能包假定存在一条简化的「章节提交主链」，用于记录每一章的事实与健康状态，并驱动各种只读视图（memory、进度、将来可能的 Dashboard）。

- **章节提交目录**：`.novelkit/story/commits/`
- **文件命名**：`chapter_{X}.commit.json`（例如 `chapter_15.commit.json`）
- **事实源头**：每个章节提交文件视为本章事实的唯一权威来源，后续记忆、统计与可视化只能从这里派生，不得直接从正文 Markdown 推导。
- **派生视图**：
  - `.novelkit/memory/character_state.md` → 角色状态的聚合视图
  - `.novelkit/memory/foreshadowing.md` → 伏笔状态的聚合视图
  - `SOLOENT.md §8` → 进度与下一步任务
- **增量更新原则**：
  - commits 记录增量（本章发生了什么），memory 记录当前最新状态；
  - 更新 memory 时只允许增量添加或修订已发生变化的信息，禁止删除或隐性修改与本章无关的既有内容。

> 技术细节：章节提交与投影流程在 `wuhang-write.md` 中详细定义。全流程的所有阶段都必须默认为「commit 是事实源头，memory/进度是投影视图」。

---

## 🔗 与 SOLOENT.md 的集成

本技能包与 **SOLOENT.md**（中央控制台）紧密集成，SOLOENT.md 中各章节通过指针链接到以下文件：

| SOLOENT 章节 | 说明 | 链接文件 |
| :--- | :--- | :--- |
| **§5** | 文风指南 | `1-边界/1.2_文风.md` |
| **§6** | 创作红线（宪法） | `.novelkit/constitution/MASTER.md` |
| **§7.2** | 角色快照（写作前读、写后更新） | `.novelkit/memory/character_state.md` |
| **§7.4** | 伏笔追踪（待收回/已收回/线索链/情感线） | `.novelkit/memory/foreshadowing.md` |
| **§8** | 项目进度与路线图 | 写在 SOLOENT.md 正文 §8，无单独文件 |

各技能会自动更新 SOLOENT.md 的相应章节及上述链接文件，保持项目状态同步。

> 注意：SOLOENT 只存索引与概览，不直接存放长篇设定正文；设定正文必须写回 1–4 号目录及 `.novelkit/` 下的专用文件。

---

## 🩺 项目体检（可选但推荐）

在进入全流程主步骤前，可先运行项目体检脚本（如已实现）：

```bash
python3 .soloent/skills/wuhang-long-all/scripts/project_doctor.py
```

建议检查内容：

- 项目根目录结构是否完整（`1-边界/`、`2-设定/`、`3-大纲/`、`4-正文/`、`5-审查/`、`.novelkit/constitution`、`.novelkit/memory`、`.novelkit/story/commits` 等）。
- `SOLOENT.md` 是否存在且基础结构无明显破坏。
- 核心脚本（extract / summarize / build_writing_prompt / build_calibration_prompt 等）是否存在。
- 上一阶段是否留有明显未完成的中间状态（如部分生成的大纲文件）。

如体检发现问题，应先根据脚本输出的提示修复后再继续全流程。

---

## 🚀 执行顺序（全流程 orchestrator）

> 总体原则：
> - 每一阶段结束时，都输出一个「阶段报告」，标明状态、产物和下一步建议；
> - 如用户中途改主意，只想做某一段（如只写大纲），应立刻退出全流程，引导加载对应的 `wuhang-*.md`。

### 0. 项目初始化（在流程内完成，不依赖插件）

- 触发条件：当前项目根目录尚未初始化（无 `SOLOENT.md` 或标准目录结构）。
- 动作：
  - 在项目根创建目录：
    - `1-边界`、`2-设定`、`3-大纲`、`4-正文`、`5-审查`
    - `.novelkit/constitution`、`.novelkit/memory`、`.novelkit/story/commits`
  - 从本技能包 `docs/` 读取并写入项目：
    - `SOLOENT.md` → 项目根目录
    - `MASTER.md` → `.novelkit/constitution/MASTER.md`
    - `character_state.md` → `.novelkit/memory/character_state.md`
    - `foreshadowing.md` → `.novelkit/memory/foreshadowing.md`
    - `expectation_template.md` → `1-边界/预期.md`
  - 将 `docs/武行-长篇小说技能说明书.md` 复制到项目根，供用户查阅。
- 完成后提示用户「项目已初始化」，再进入第 1 步。

> 如项目根已存在上述结构及 SOLOENT，则跳过此步，仅进行后续阶段。

---

### 1. 启动阶段：样板书拆解 / 边界确定

- 读取并执行 `wuhang-boundary.md`，完成样板书拆解（故事梗概、文风、套路方向、全书框架、微观节奏等）。
- **⚠️ 严格约束**：必须严格遵守 `wuhang-boundary.md` 内定义的「产出白名单」，禁止擅自新增任何未要求的文件。
- 按步骤中的「强制暂停」点执行，每个关键节点都等待用户「继续」确认。

**本阶段产物（参考）：**

- `1-边界/预期.md`
- `1-边界/1.1_全书故事梗概.md`
- `1-边界/1.2_文风.md`
- `1-边界/1.3_套路方向.md`
- `1-边界/1.4_全书框架.md`
- `1-边界/1.5_微观节奏拆解.md`

**阶段报告（建议格式）：**

- 状态：已完成 / 部分完成 / 需要你处理 / 未完成
- 主要产物：列出实际生成或更新的文件路径
- 下一步建议：如无异常，建议加载 `wuhang-ideation` 进入创意与设定阶段；如对样板书仍有疑虑，可先在 `1-边界/` 中追加自定义拆解。

---

### 2. 创意与设定阶段

- 读取并执行 `wuhang-ideation.md`：
  - 创意脑暴与核心梗确立 (`2.1_创意脑暴.md`)
  - 新书设定案 (`2.2_新书设定案.md`)
  - 金手指深度设计 (`2.3_金手指设定.md`)
  - 角色人设细化 (`2.4_主要角色设定表.md`)
  - 宪法阅读与更新提示 (`.novelkit/constitution/MASTER.md`)
  - 资产注册（更新 `SOLOENT.md` 各索引区）
- **⚠️ 严格约束**：必须严格遵守 `wuhang-ideation.md` 内定义的「产出白名单」，禁止擅自新增任何未要求的设定类 Markdown。

**本阶段重点集成点：**

- 所有设定文件必须注册到 `SOLOENT.md` 对应章节（世界观索引、角色索引、文风、宪法指针），否则后续写作阶段无法完整读取设定资产。
- 为章节提交文件（chapter commits）提供稳定的设定背景，避免 commit 中的事件描述与世界观/人设矛盾。

**阶段报告（建议格式）：**

- 状态：已完成 / 部分完成 / 需要你处理 / 未完成
- 主要产物：`2.1_创意脑暴.md`、`2.2_新书设定案.md`、`2.3_金手指设定.md`、`2.4_主要角色设定表.md`、`.novelkit/constitution/MASTER.md` 更新、`SOLOENT.md` 索引更新。
- 下一步建议：
  - 如需质检设定，可加载 `wuhang-review` 的设定检查模块；
  - 如准备进入结构规划，加载 `wuhang-outline`。

---

### 3. 设定审查（可选）

- 询问用户是否需要审查设定：
  - 若需要，读取并执行 `wuhang-review.md` 中的设定审查流程；
  - 若不需要，直接进入第 4 步。
- 审查结果可能要求回写 `2-设定/` 下的若干文件，需先完成修订再进入大纲阶段。

**阶段报告**：以「需要你处理 / 已完成」结构简要说明审查发现的问题、已修正内容和遗留风险。

---

### 4. 大纲规划阶段

- 读取并执行 `wuhang-outline.md`：
  - 全书总纲 (`3.1_全书结构总纲.md`)
  - 单卷完整卷纲 (`3-大纲/XX卷_完整卷纲.md`)
  - 标准化章纲 (`3-大纲/XX卷_章纲.md`)
  - 动态修订入口（正文跑偏或总纲调整时的修订流程）

- **⚠️ 严格约束**：必须严格遵守 `wuhang-outline.md` 内定义的「产出白名单」，禁止擅自新增其他大纲类 Markdown。
- 大纲阶段必须与设定文件双向对齐：总纲/卷纲/章纲 的重大变更需回写 `2.2_新书设定案.md` / `2.3_金手指设定.md` / `2.4_主要角色设定表.md`，保持「设定 ←→ 大纲」一致。

**与章节提交的关系：**

- 章纲中的「场景拆解」「伏笔与线索」「结尾钩子」等信息，将直接指导 `wuhang-write` 中的写作提示词与章节提交文件中的 `events` 和 `foreshadowing_diff` 的结构。

**阶段报告（建议格式）：**

- 状态：本轮完成了哪些层级（总纲/某几卷卷纲/某卷章纲）
- 主要产物：对应的 `3-大纲/` 文件路径列表
- 下一步建议：
  - 如至少完成一卷的卷纲 + 前若干章章纲 → 推荐加载 `wuhang-write` 开始写作；
  - 如作者希望「先把全书结构定死」→ 继续在 `wuhang-outline` 内完成更多卷再写。

---

### 5. 大纲审查（可选）

- 询问用户是否需要审查大纲：
  - 若需要，读取并执行 `wuhang-review.md` 中的大纲质检模块；
  - 若不需要，直接进入第 6 步。
- 大纲审查通过后，可视为「施工图版本 1.0」，进入正文阶段。

**阶段报告**：说明哪些结构通过了审查，哪些地方存在风险（如中后期乏力、重复套路等），并给出是否建议先修订再写的意见。

---

### 6. 写作阶段

- 读取并执行 `wuhang-write.md`：
  - 步骤 0：一次性初始化（角色初始状态写入、SOLOENT 指针确认）
  - 步骤 1：生成写作提示词 (`build_writing_prompt.py`)
  - 步骤 2：执行正文撰写（草稿落入 `第X章_草稿.md`）
  - 步骤 3：完稿后校准 (`build_calibration_prompt.py` + 完稿自检卡)
  - 步骤 4：伏笔、状态与进度更新（更新 `.novelkit/memory/` 与 `SOLOENT.md §8`）
  - 步骤 4.5：章节提交与投影（生成 `.novelkit/story/commits/chapter_{X}.commit.json` ）
  - Loop control：根据章纲/卷纲状态决定是否继续下一章或返回大纲修订

- **⚠️ 严格约束**：必须严格遵守 `wuhang-write.md` 中的「白名单输出」「增量更新铁律」「commit 为事实源头」等约束。

**阶段报告（按批次或卷）**：

- 状态：例如「本卷第 1–20 章已完稿并提交」「黄金三章已校准」等。
- 主要产物：
  - `4-正文/第X章_正文.md`（或批次范围）
  - `.novelkit/story/commits/chapter_{X}.commit.json`（本卷或本批次的章节提交列表）
  - memory / SOLOENT 更新情况（角色成长、伏笔整体情况）
- 下一步建议：
  - 如本卷完 → 推荐加载 `wuhang-outline` 做下一卷卷纲 / 章纲；
  - 如发现剧情明显偏离章纲 → 推荐启用 `wuhang-outline` 的「大纲动态修订」模块。

---

### 7. 正文审查（可选）

- 在每章、每批次（如每 10 章）、每卷完结时，询问用户是否需要审查正文：
  - 若需要，读取并执行 `wuhang-review.md` 中的正文质检模块（代入感、爽点密度、OOC、节奏等）。
  - 审查结果可回写：
    - `.novelkit/story/commits/chapter_{X}.commit.json` 的 `health_flags`
    - `3-大纲/XX卷_章纲.md`（若需调整后续走向）
    - `2-设定/`（若需调整金手指或人设）
  - 若不需要，继续写作循环或进入大纲修订/下一卷规划。
  
**阶段报告**：总结审查发现的系统性问题（如持续水文、套路疲劳），并建议是否进行「结构级」修订，而不仅仅是微调单章文笔。

---

> 若用户只明确说了某个阶段（如「我只要写大纲」），请停止执行本全流程，提示用户直接加载对应的 `wuhang-outline.md` / `wuhang-ideation.md` / `wuhang-write.md` 等单独技能文件。
