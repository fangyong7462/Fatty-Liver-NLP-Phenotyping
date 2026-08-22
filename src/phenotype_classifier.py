#!/usr/bin/env python3
"""Source-derived implementation of the fixed five-category rule set.

This module intentionally preserves the original frozen rule priority and
pattern behavior. It is not a clinical diagnostic system and has no
Unclassified or abstention output.
"""
import argparse
import json
import math
import re

STAGES = ["Normal", "Trend", "Mild", "Moderate", "Severe"]

RE_SEVERE = re.compile(r"重度脂肪肝|severe\s*fatty\s*liver", re.I)
RE_MODERATE = re.compile(r"中度脂肪肝|moderate\s*fatty\s*liver", re.I)
RE_TREND = re.compile(
    r"脂肪肝趋势|前脂肪肝|脂肪肝倾向|"
    r"(脂肪肝).*(不除外|不能排除|可能|疑似|考虑|倾向|建议随访|待排|\?)|"
    r"(不除外|不能排除|可能|疑似|考虑|倾向|建议随访|待排).*(脂肪肝)|"
    r"(possible|likely|borderline|suspected)\s*fatty\s*liver",
    re.I,
)
RE_MILD = re.compile(
    r"轻度脂肪肝|(?<!未见)(?<!无)(?<!排除)(脂肪肝)(?!趋势)", re.I
)
RE_NEG = re.compile(
    r"未见明显脂肪肝|未见明确脂肪肝|未见脂肪肝征象|无脂肪肝|"
    r"no\s*fatty\s*liver|no\s*evidence\s*of\s*fatty\s*liver",
    re.I,
)


def clean_text(text):
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return ""
    text = str(text).replace(" ", "")
    for ch in ["，", "。", "：", "；", ",", ".", "、", "\t", "\r"]:
        text = text.replace(ch, "")
    return text


def classify_stage(text):
    text = clean_text(text)
    if RE_SEVERE.search(text):
        return "Severe"
    if RE_MODERATE.search(text):
        return "Moderate"
    if RE_TREND.search(text):
        return "Trend"
    if RE_MILD.search(text):
        return "Mild"
    if RE_NEG.search(text):
        return "Normal"
    return "Normal"


def frozen_rule_as_used(text):
    """Apply the exact frozen rule used for the reported analysis."""
    return classify_stage(text)


def classify_records(texts):
    return [classify_stage(text) for text in texts]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text")
    parser.add_argument("--json")
    args = parser.parse_args()
    if args.text is not None:
        print(json.dumps({"stage": classify_stage(args.text)}, ensure_ascii=False))
    elif args.json:
        print(json.dumps([{"stage": x} for x in classify_records(json.loads(args.json))], ensure_ascii=False))
    else:
        parser.error("provide --text or --json")
