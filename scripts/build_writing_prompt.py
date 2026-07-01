#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import glob

def read_file_if_exists(filepath, title):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if content:
                return f"### 【{title}】\n{content}\n\n"
        except Exception as e:
            print(f"⚠️ 读取 {filepath} 失败: {e}")
    return ""

def extract_chapter_outline(chapter_num):
    outline_files = glob.glob(os.path.join("3-大纲", "*_章纲.md"))
    if not outline_files:
        return f"⚠️ 未找到任何章纲文件 (3-大纲/*_章纲.md)"

    # 匹配 "第X章" 或 "第 X 章"
    pattern_current = re.compile(rf"^(### |## |# )?第\s*{chapter_num}\s*章[：\s]", re.MULTILINE)
    pattern_next = re.compile(rf"^(### |## |# )?第\s*\d+\s*章[：\s]", re.MULTILINE)

    for file in outline_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        match = pattern_current.search(content)
        if match:
            start_idx = match.start()
            # 寻找下一章的开头作为结束
            rest_content = content[start_idx + len(match.group()):]
            next_match = pattern_next.search(rest_content)

            if next_match:
                end_idx = start_idx + len(match.group()) + next_match.start()
                return content[start_idx:end_idx].strip()
            else:
                return content[start_idx:].strip()

    return f"⚠️ 在所有章纲文件中均未找到【第{chapter_num}章】的专属章纲，请检查 3-大纲/ 目录。"

def get_previous_chapters(current_chap, count=3):
    result = ""
    for i in range(max(1, current_chap - count), current_chap):
        # 精确匹配「第N章_正文.md」，再兼容「第N章_标题_正文.md」
        # 避免通配符「第*N*章」在两位数章号时误命中其他章节
        target_files = glob.glob(os.path.join("4-正文", f"第{i}章_正文.md"))
        if not target_files:
            target_files = glob.glob(os.path.join("4-正文", f"第{i}章_*_正文.md"))
        if not target_files:
            target_files = glob.glob(os.path.join("4-正文", f"第{i}章_草稿.md"))
        if not target_files:
            target_files = glob.glob(os.path.join("4-正文", f"第{i}章_*_草稿.md"))

        if target_files:
            filepath = target_files[0]
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                # 限制单章参考字数，防止上下文爆炸
                if len(text) > 4000:
                    text = text[-4000:] + "\n...(前文较长，截取后半部分)"
                result += f"#### 第{i}章回顾\n{text}\n\n"
            except Exception:
                pass
    if not result:
        return "无前文参考（可能是开局或未找到前文文件）。"
    return result

def build_prompt(chapter_num):
    print(f"正在为【第{chapter_num}章】组装写作提示词...")

    # 确保输出目录存在
    os.makedirs("4-正文/prompts", exist_ok=True)

    prompt = f"# 第{chapter_num}章 写作提示词 (Writing Prompt)\n\n"
    prompt += "> **AI 角色设定**：你是一位网文大神，请严格按照以下提供的所有上下文、设定、文风和章纲，撰写本章正文。\n\n"

    prompt += "## 一、本章核心指令（最重要）\n\n"
    prompt += extract_chapter_outline(chapter_num) + "\n\n"

    prompt += "---\n\n## 二、近期前文参考（接续剧情与情绪）\n\n"
    prompt += get_previous_chapters(chapter_num, 3) + "\n\n"

    prompt += "---\n\n## 三、当前动态状态（必须符合现状）\n\n"
    prompt += read_file_if_exists(os.path.join(".novelkit", "memory", "character_state.md"), "角色当前状态")
    prompt += read_file_if_exists(os.path.join(".novelkit", "memory", "foreshadowing.md"), "伏笔与线索追踪")

    prompt += "---\n\n## 四、核心设定参考\n\n"
    prompt += read_file_if_exists(os.path.join("2-设定", "2.2_新书设定案.md"), "新书设定案")
    prompt += read_file_if_exists(os.path.join("2-设定", "2.3_金手指设定.md"), "金手指设定")
    prompt += read_file_if_exists(os.path.join("2-设定", "2.4_主要角色设定表.md"), "主要角色设定表")

    prompt += "---\n\n## 五、文风与红线（严格遵守）\n\n"
    prompt += read_file_if_exists(os.path.join("1-边界", "1.2_文风.md"), "基础文风要求")
    prompt += read_file_if_exists(os.path.join("1-边界", "1.5_微观节奏拆解.md"), "微观节奏与镜头语言")
    prompt += read_file_if_exists(os.path.join(".novelkit", "constitution", "MASTER.md"), "项目宪法与避坑红线")

    prompt += """---

## 六、写作输出要求

1. **分场景生成**：严格按照本章章纲拆解的场景顺序，**逐个场景**进行撰写，不要遗漏。
2. **字数要求**：单章总字数建议在 **1800-3000 字** 之间，细节要丰满。
3. **文风执行**：注重「展示而非讲述」(Show, Don't Tell)，强化感官描写，**绝对禁止**出现AI味浓重的总结性排比句。
4. **去AI味负向清单**（写前必读，出现即删）：
- ❌ 神态微动作：嘴角勾起/眼中闪过/深吸一口气/捏紧拳头/瞳孔收缩/指节发白
- ❌ 滥用比喻：全章「像/宛如/仿佛/犹如」引导的比喻句 **≤3 个**
- ❌ 逻辑废话：他知道/心中一动/这意味着/不得不说/电光火石之间
- ❌ 结尾升华旁白：章末总结感慨、「这一刻他明白了……」
- ❌ 上帝解释腔：「这意味着……」「他不知道的是……」「之所以…是因为」
- ✅ 替代方案：用具体动作/身体反应/对话展示情绪，不用形容词直接告诉
5. **结尾钩子**：确保章节末尾包含章纲中设计的悬念或钩子，吸引读者阅读下一章。
6. **创作范围**：严格遵守章纲剧情范围，不得超前剧透或越权推进下一章剧情。

**请直接输出正文内容，不需要任何开场白或解释。**
"""

    output_file = os.path.join("4-正文", "prompts", f"第{chapter_num}章_写作提示词.md")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"✅ 成功生成提示词文件：{output_file}")
    except Exception as e:
        print(f"❌ 生成提示词失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 build_writing_prompt.py <章号>")
        print("示例: python3 build_writing_prompt.py 15")
        sys.exit(1)

    try:
        chap_num = int(sys.argv[1])
        build_prompt(chap_num)
    except ValueError:
        print("❌ 错误：章号必须是数字。")
        sys.exit(1)
