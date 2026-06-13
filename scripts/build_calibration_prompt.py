#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import glob

def count_chinese_words(text):
    """统计中文字数（包含标点符号），排除空格、换行、英文字母、数字和 markdown 标记"""
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'[a-zA-Z0-9]+', '', text)
    text = re.sub(r'[#*_`\[\]\(\)]+', '', text)
    return len(text)

def build_calibration_prompt(chapter_num):
    print(f"正在为【第{chapter_num}章】组装完稿校准提示词...")
    
    # 1. 读取本章草稿并统计字数
    draft_file = os.path.join("4-正文", f"第{chapter_num}章_草稿.md")
    if not os.path.exists(draft_file):
        print(f"❌ 错误：未找到草稿文件 {draft_file}")
        sys.exit(1)
        
    with open(draft_file, 'r', encoding='utf-8') as f:
        draft_content = f.read().strip()
        
    word_count = count_chinese_words(draft_content)
    
    # 2. 读取写作提示词（里面已经包含了章纲、文风、宪法等所有约束）
    prompt_file = os.path.join("4-正文", "prompts", f"第{chapter_num}章_写作提示词.md")
    if not os.path.exists(prompt_file):
        print(f"❌ 错误：未找到写作提示词文件 {prompt_file}，无法进行对照检查。")
        sys.exit(1)
        
    with open(prompt_file, 'r', encoding='utf-8') as f:
        writing_prompt_content = f.read().strip()

    # 3. 组装校准 Prompt
    prompt = f"# 第{chapter_num}章 完稿校准指令 (Calibration Prompt)\n\n"
    prompt += "> **任务目标**：你现在是一位极其严苛的网文主编，请根据之前的【写作提示词】要求，对刚刚生成的【本章草稿】进行五项严格审查，并输出【完稿自检卡】。\n\n"
    
    prompt += "## 一、审查材料\n\n"
    prompt += f"### 1. 本章草稿内容（当前中文字数：{word_count} 字）\n"
    prompt += "```markdown\n" + draft_content + "\n```\n\n"
    
    prompt += "### 2. 原始写作约束（作为评判标准）\n"
    prompt += "```markdown\n" + writing_prompt_content + "\n```\n\n"
    
    prompt += """---

## 二、五项严格审查标准

请逐一核对以下五项标准：

1. **字数检查**：当前中文字数为 {word_count} 字。是否达到最低 1800 字的要求？（若未达到，必须判定为不通过，并要求扩写细节）。
2. **大纲符合性检查**：对照原始约束中的【本章核心指令】，检查本章核心事件、场景和结尾钩子是否完全按计划执行？是否有遗漏场景？
3. **文风与红线检查**：对照原始约束中的【文风与红线】，检查是否存在浓重的AI翻译腔、总结性排比句？是否违反了项目宪法的避坑红线？
4. **接续检查**：对照原始约束中的【近期前文参考】，检查剧情、时间、地点是否无缝接续？是否存在逻辑断层？
5. **金手指合规性**：（若本章涉及）检查表现形式是否符合原始约束中的设定？

---

## 三、输出要求

请直接输出一份**【完稿自检卡】**，格式如下：

### 📝 第X章 完稿自检卡

- **字数达标**：[通过/不通过]（当前字数：{word_count}）
- **大纲符合度**：[通过/不通过]（简述理由）
- **文风与红线**：[通过/不通过]（简述理由）
- **剧情接续**：[通过/不通过]（简述理由）
- **金手指合规**：[通过/不通过/不涉及]（简述理由）

**最终结论**：
- 如果五项全部通过：请回复「**✅ 审查通过。请将草稿重命名为正文，并进入下一步。**」
- 如果有任何一项不通过：请明确列出**必须修改的段落和具体修改建议**，并回复「**❌ 审查未通过。请根据以上建议对草稿进行修订。**」
"""

    os.makedirs("4-正文/prompts", exist_ok=True)
    output_file = os.path.join("4-正文", "prompts", f"第{chapter_num}章_校准提示词.md")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"✅ 成功生成校准提示词文件：{output_file}")
        print(f"📊 本章当前中文字数：{word_count} 字")
    except Exception as e:
        print(f"❌ 生成校准提示词失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 build_calibration_prompt.py <章号>")
        print("示例: python3 build_calibration_prompt.py 15")
        sys.exit(1)
        
    try:
        chap_num = int(sys.argv[1])
        build_calibration_prompt(chap_num)
    except ValueError:
        print("❌ 错误：章号必须是数字。")
        sys.exit(1)
