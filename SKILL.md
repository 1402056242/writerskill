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

---

## 🚀 执行顺序

0. **项目初始化（在流程内完成，不依赖插件）**  
   - 若当前项目根目录尚未初始化，则先执行以下动作，再进入第 1 步；若已存在 `SOLOENT.md` 及标准目录结构，可跳过。
   - 在项目根创建目录：`1-边界`、`2-设定`、`3-大纲`、`4-正文`、`5-审查`、`.novelkit/constitution`、`.novelkit/memory`。
   - 从本技能包 `docs/` 读取并写入项目：
     - `SOLOENT.md` → 项目根目录
     - `MASTER.md` → `.novelkit/constitution/MASTER.md`
     - `character_state.md` → `.novelkit/memory/character_state.md`
     - `foreshadowing.md` → `.novelkit/memory/foreshadowing.md`
     - `expectation_template.md` → `1-边界/预期.md`
   - 将 `docs/武行-长篇小说技能说明书.md` 复制到项目根，供用户查阅。
   - 完成后提示用户「项目已初始化」，再进入第 1 步。

1. **启动阶段**
   - 读取并执行 `wuhang-boundary.md`，完成样板书拆解。
   - **⚠️ 严格约束**：必须严格遵守该文件内定义的「产出白名单」，禁止擅自新增任何未要求的文件。

2. **创意与设定阶段**
   - 读取并执行 `wuhang-ideation.md`：创意脑暴、新书设定案、金手指与角色表、宪法交互、在 `SOLOENT.md` 中登记索引指针。
   - **⚠️ 严格约束**：必须严格遵守该文件内定义的「产出白名单」，禁止擅自新增任何未要求的文件。

3. **设定审查（可选，可跳过）**
   - 询问用户是否需要审查设定。若需要，读取并执行 `wuhang-review.md`；若不需要，直接进入第 4 步。

4. **大纲规划阶段**
   - 读取并执行 `wuhang-outline.md`：全书总纲、单卷卷纲或标准化章纲细化。 
   - **⚠️ 严格约束**：必须严格遵守该文件内定义的「产出白名单」，禁止擅自新增任何未要求的文件。

5. **大纲审查（可选，可跳过）**
   - 询问用户是否需要审查大纲。若需要，读取并执行 `wuhang-review.md`；若不需要，直接进入第 6 步。

6. **写作阶段**
   - 读取并执行 `wuhang-write.md`：按章纲写作，本卷完成或剧情偏离时回到阶段 4 修订或开写下一卷。
   - **⚠️ 严格约束**：必须严格遵守该文件内定义的「产出白名单」，禁止擅自新增任何未要求的文件。

7. **正文审查（可选，可跳过）**
   - 每章或每卷后，询问用户是否需要审查正文。若需要，读取并执行 `wuhang-review.md`；若不需要，继续写作循环。

---

> 若用户只明确说了某个阶段（如「我只要写大纲」），请停止执行本全流程，提示用户直接加载 `wuhang-outline.md`。
