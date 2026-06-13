#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
project_doctor.py

NovelKit / writerskill 项目的结构体检脚本。

用法：
    python scripts/project_doctor.py
    python scripts/project_doctor.py --project-root /path/to/project
"""

import os
import re
import argparse
from typing import List, Tuple, Dict


# ========== 工具函数 ==========

class Colors:
    OK = "\033[92m"      # 绿色
    WARN = "\033[93m"    # 黄色
    FAIL = "\033[91m"    # 红色
    INFO = "\033[94m"    # 蓝色
    RESET = "\033[0m"


def ok(msg: str):
    print(f"{Colors.OK}[OK]{Colors.RESET}   {msg}")


def warn(msg: str):
    print(f"{Colors.WARN}[WARN]{Colors.RESET} {msg}")


def fail(msg: str):
    print(f"{Colors.FAIL}[MISS]{Colors.RESET} {msg}")


def info(msg: str):
    print(f"{Colors.INFO}[INFO]{Colors.RESET} {msg}")


def rel(path: str, root: str) -> str:
    """把绝对路径转换成相对 project_root 的显示形式。"""
    try:
        return os.path.relpath(path, root)
    except Exception:
        return path


# ========== 体检项定义 ==========

REQUIRED_DIRS = [
    "1-边界",
    "2-设定",
    "3-大纲",
    "4-正文",
    ".novelkit",
    ".novelkit/constitution",
    ".novelkit/memory",
    ".novelkit/story",
    ".novelkit/story/commits",
]

REQUIRED_FILES = [
    "docs/MASTER.md",
    "docs/SOLOENT.md",
    "docs/expectation_template.md",
    "docs/character_state.md",
    "docs/foreshadowing.md",
    ".novelkit/constitution/MASTER.md",
    ".novelkit/memory/character_state.md",
    ".novelkit/memory/foreshadowing.md",
]

# 有些是推荐存在（比如梗概），缺了不算致命
RECOMMENDED_FILES = [
    "1-边界/1.1_全书故事梗概.md",
    "1-边界/1.2_文风.md",
    "2-设定/2.2_新书设定案.md",
    "2-设定/2.3_金手指设定.md",
    "2-设定/2.4_主要角色设定表.md",
    "3-大纲/3.1_全书结构总纲.md",
]


# ========== 检查函数 ==========

def check_dirs(project_root: str) -> None:
    info("检查必需目录...")
    for d in REQUIRED_DIRS:
        path = os.path.join(project_root, d)
        if os.path.isdir(path):
            ok(f"目录存在：{d}")
        else:
            fail(f"目录缺失：{d}")


def check_files(project_root: str) -> None:
    info("检查必需文件...")
    for fpath in REQUIRED_FILES:
        path = os.path.join(project_root, fpath)
        if os.path.isfile(path):
            ok(f"文件存在：{fpath}")
        else:
            fail(f"文件缺失：{fpath}")

    info("检查推荐文件（建议尽量补上）...")
    for fpath in RECOMMENDED_FILES:
        path = os.path.join(project_root, fpath)
        if os.path.isfile(path):
            ok(f"推荐文件已存在：{fpath}")
        else:
            warn(f"推荐文件尚未创建：{fpath}")


def parse_paths_from_soloent(sole_path: str) -> List[str]:
    """
    从 docs/SOLOENT.md 里解析出所有 markdown 代码块中的路径，例如 `3-大纲/3.1_全书结构总纲.md`。
    """
    paths: List[str] = []
    if not os.path.isfile(sole_path):
        return paths

    try:
        with open(sole_path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(sole_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    # 简单粗暴：抓取所有 `xxx/xxx.md` 风格的 code span
    code_spans = re.findall(r"`([^`]+)`", text)
    for span in code_spans:
        span = span.strip()
        # 只保留看起来像路径的
        if ("/" in span or span.endswith(".md")) and not span.startswith("http"):
            paths.append(span)
    return sorted(set(paths))


def check_soloent_links(project_root: str) -> None:
    info("检查 SOLOENT.md 中的文件指针...")
    sole_path = os.path.join(project_root, "docs", "SOLOENT.md")
    if not os.path.isfile(sole_path):
        fail("未找到 docs/SOLOENT.md，无法检查指针。")
        return

    paths = parse_paths_from_soloent(sole_path)
    if not paths:
        warn("在 docs/SOLOENT.md 中未解析到任何路径指针（可能模板未按约定写 `路径`）。")
        return

    for p in paths:
        abs_path = os.path.join(project_root, p)
        if os.path.exists(abs_path):
            ok(f"SOLOENT 指针有效：{p}")
        else:
            fail(f"SOLOENT 指向的文件/目录不存在：{p}")


def scan_commits(project_root: str) -> Tuple[List[int], List[str]]:
    """
    扫描 .novelkit/story/commits 下的 chapter_XXXX.commit.json，
    返回（章节号列表, 文件名列表）。
    """
    commits_dir = os.path.join(project_root, ".novelkit", "story", "commits")
    chapter_numbers: List[int] = []
    filenames: List[str] = []

    if not os.path.isdir(commits_dir):
        return chapter_numbers, filenames

    for name in os.listdir(commits_dir):
        if not name.startswith("chapter_") or not name.endswith(".commit.json"):
            continue
        # 例如 chapter_0001.commit.json -> 0001
        middle = name[len("chapter_"):-len(".commit.json")]
        try:
            num = int(middle)
            chapter_numbers.append(num)
            filenames.append(name)
        except ValueError:
            # 忽略不符合整数的
            continue

    chapter_numbers.sort()
    filenames.sort()
    return chapter_numbers, filenames


def check_commits(project_root: str) -> None:
    info("检查章节提交（Story System commits）...")
    nums, files = scan_commits(project_root)
    if not nums:
        warn("尚未发现任何章节提交文件（.novelkit/story/commits/ 目录为空或不存在标准命名）。")
        return

    first, last = nums[0], nums[-1]
    ok(f"已发现 {len(nums)} 个章节提交文件，范围：chapter_{first:04d} ~ chapter_{last:04d}")

    # 计算缺失章节
    missing = [i for i in range(first, last + 1) if i not in nums]
    if missing:
        warn(f"章节提交存在缺口：{', '.join(str(i) for i in missing)}")
    else:
        ok("章节提交没有明显缺口。")


def check_memory_non_empty(project_root: str) -> None:
    info("检查 memory 文件是否存在且非空...")
    paths = [
        ".novelkit/memory/character_state.md",
        ".novelkit/memory/foreshadowing.md",
    ]
    for p in paths:
        abs_path = os.path.join(project_root, p)
        if not os.path.isfile(abs_path):
            fail(f"记忆文件缺失：{p}")
            continue
        size = os.path.getsize(abs_path)
        if size == 0:
            warn(f"记忆文件存在但为空：{p}")
        else:
            ok(f"记忆文件存在且非空：{p}（{size} 字节）")


# ========== 主入口 ==========

def main():
    parser = argparse.ArgumentParser(description="NovelKit / writerskill 项目体检脚本")
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="项目根目录（默认：当前工作目录）",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    info(f"项目根目录：{project_root}")

    # 1. 目录 & 文件
    check_dirs(project_root)
    check_files(project_root)

    # 2. SOLOENT 指针一致性
    check_soloent_links(project_root)

    # 3. Story System 提交情况
    check_commits(project_root)

    # 4. memory 文件简单健康检查
    check_memory_non_empty(project_root)

    print()
    info("体检完成。如果有 [MISS] 或 [WARN]，建议优先处理这些问题。")


if __name__ == "__main__":
    main()
