#!/usr/bin/env python3
"""检查翻译输出是否为逐句翻译交付物，而非总结式改写。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SUSPICIOUS_PATTERNS = [
    r"方法概览",
    r"实验结论",
    r"根据论文实验结果",
    r"作者发现",
    r"这说明",
    r"可以看出",
    r"表明了?",
    r"说明了?",
    r"综上",
    r"总体来看",
    r"总的来说",
    r"归纳来看",
    r"说明其",
]


def canonical_stem(path: Path) -> str:
    stem = path.stem
    for suffix in [".translation.zh", ".analysis.zh", ".raw"]:
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem


def normalize_heading_text(line: str) -> str:
    text = line.strip()
    text = re.sub(r"^#+\s*", "", text)
    text = text.replace("*", "")
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_numbered_headings(text: str) -> list[str]:
    headings: list[str] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("#"):
            continue
        normalized = normalize_heading_text(line)
        if re.fullmatch(r"Page \d+", normalized, re.IGNORECASE):
            continue
        match = re.match(r"^(\d+(?:\.\d+)+|\d+)(?:[\s.:：\-]|$)", normalized)
        if not match:
            continue
        heading_id = match.group(1)
        if heading_id in seen:
            continue
        seen.add(heading_id)
        headings.append(heading_id)
    return headings


def compare_numbered_headings(source_text: str, translation_text: str) -> list[str]:
    issues: list[str] = []
    source_headings = extract_numbered_headings(source_text)
    translation_headings = extract_numbered_headings(translation_text)

    if not source_headings:
        return issues

    if not translation_headings:
        issues.append("源文档检测到了编号章节，但译文中没有检测到对应的编号章节。")
        return issues

    missing = [item for item in source_headings if item not in translation_headings]
    if missing:
        preview = ", ".join(missing[:8])
        issues.append(f"译文缺少这些编号章节或小节：{preview}")

    unexpected = [item for item in translation_headings if item not in source_headings]
    if unexpected:
        preview = ", ".join(unexpected[:8])
        issues.append(f"译文出现了源文档中不存在的编号章节：{preview}")

    common = [item for item in translation_headings if item in source_headings]
    expected_common = [item for item in source_headings if item in translation_headings]
    if common != expected_common:
        issues.append("译文中的编号章节顺序与源文档不一致，疑似存在跳段、漏段或重排。")

    return issues


def find_issues(text: str, source_text: str | None = None) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()

    if "模式：翻译" not in text and "模式：只翻译" not in text and "本文件为完整中文翻译" not in text:
        issues.append("缺少明确的翻译交付标识，建议在文件开头注明这是完整中文翻译。")

    bullet_lines = [line for line in lines if re.match(r"^\s*[-*]\s+", line)]
    if len(bullet_lines) >= 6:
        issues.append("检测到较多项目符号行，疑似把段落翻译写成了提炼后的要点列表。")

    short_paragraphs = 0
    for block in re.split(r"\n\s*\n", text):
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        line_count = len([line for line in stripped.splitlines() if line.strip()])
        if line_count == 1 and len(stripped) <= 80:
            short_paragraphs += 1
    if short_paragraphs >= 8:
        issues.append("检测到较多短小单行段落，疑似是总结式重述而不是逐句翻译。")

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text):
            issues.append(f"检测到可疑总结式表达：`{pattern}`")

    if re.search(r"^\s*##?\s*(方法概览|实验结论|结论概述|结果总结)\s*$", text, re.MULTILINE):
        issues.append('检测到疑似自造总结标题，翻译文件不应引入"方法概览/实验结论/结果总结"之类标题。')

    if source_text is not None:
        issues.extend(compare_numbered_headings(source_text, text))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="检查翻译输出是否存在总结式漂移。")
    parser.add_argument("files", nargs="+", help="待检查的翻译 Markdown 文件")
    parser.add_argument("--source", action="append", default=[], help="源文档 Markdown 文件，用于章节覆盖对比；可重复指定")
    args = parser.parse_args()

    source_map: dict[str, str] = {}
    for raw_source in args.source:
        source_path = Path(raw_source)
        if not source_path.exists():
            print(f"[FAIL] {source_path}: 源文件未找到")
            return 1
        source_map[canonical_stem(source_path)] = source_path.read_text()
    single_source_text = next(iter(source_map.values())) if len(source_map) == 1 else None

    failed = False
    for raw_path in args.files:
        path = Path(raw_path)
        if not path.exists():
            print(f"[FAIL] {path}: 文件未找到")
            failed = True
            continue
        text = path.read_text()
        source_text = source_map.get(canonical_stem(path))
        if source_text is None and single_source_text is not None:
            source_text = single_source_text
        issues = find_issues(text, source_text=source_text)
        if args.source and source_text is None:
            issues.append("提供了源抽取稿，但当前译文未能匹配到对应 source，无法完成章节覆盖检查。")
        if issues:
            failed = True
            print(f"[FAIL] {path}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[OK] {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
