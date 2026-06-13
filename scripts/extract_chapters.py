import sys
import re
import os

def extract_chapters(filepath, start_chap, end_chap):
    if not os.path.exists(filepath):
        print(f"❌ 错误：找不到文件 {filepath}")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return

    # 匹配章节标题，例如：第1章，第一百二十三章，第001节 等
    pattern = r'(第[零一二三四五六七八九十百千万0-9]+[章卷节回折][ \t]*[^\n]*)'
    parts = re.split(pattern, content)

    if len(parts) == 1:
        print("⚠️ 未检测到标准的章节划分（如“第X章”）。请检查文件格式。")
        return

    chapters = []
    # parts[0] 是第一章之前的引言/前言
    for i in range(1, len(parts), 2):
        title = parts[i]
        body = parts[i+1] if i+1 < len(parts) else ""
        chapters.append(title + "\n" + body)

    start_idx = max(0, start_chap - 1)
    end_idx = min(len(chapters), end_chap)

    if start_idx >= len(chapters):
        print(f"⚠️ 起始章节 {start_chap} 超出总章节数 {len(chapters)}。")
        return

    extracted = chapters[start_idx:end_idx]
    text_out = "\n\n".join(extracted)
    
    # 限制输出字数，防止终端爆炸 (最大 30000 字)
    if len(text_out) > 30000:
        text_out = text_out[:30000] + "\n\n...[内容过长已截断]..."
        
    print(text_out)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python3 extract_chapters.py <小说文件路径> <起始章号> <结束章号>")
        print("示例: python3 extract_chapters.py 1-边界/book.txt 1 10")
        sys.exit(1)
    
    filepath = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    extract_chapters(filepath, start, end)
