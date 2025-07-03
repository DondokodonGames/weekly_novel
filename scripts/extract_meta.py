# scripts/extract_meta.py

import os
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI


def sanitize(name: str) -> str:
    """
    ファイルシステム上で安全な文字列に変換
    英数字・アンダースコア・ハイフン以外はアンダースコアに置換する
    """
    return re.sub(r'[^0-9A-Za-z_-]', '_', name)


def main():
    # APIキー取得
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)

    # 日付 (JST) と出力ディレクトリ
    tz = ZoneInfo("Asia/Tokyo")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    output_dir = Path("output") / today
    output_dir.mkdir(parents=True, exist_ok=True)

    # 企画ファイル取得
    plans_dir = Path("plans")
    if plans_dir.exists():
        md_files = sorted(plans_dir.glob("*.md"))
    else:
        md_files = sorted(Path(".").glob("*.md"))
    if not md_files:
        raise FileNotFoundError("No markdown (.md) planning file found.")
    plan_path = md_files[-1]
    print(f"🎯 使用中の企画ファイル: {plan_path}")

    plan_text = plan_path.read_text(encoding="utf-8")

    # ポリシーファイル読み込み
    policy_path = Path("config/generate_policy.md")
    policy_text = policy_path.read_text(encoding="utf-8") if policy_path.exists() else ""

    # プロンプト生成
    prompt = f"""
{policy_text}

以下はノベルゲームの企画書です。この内容から以下の構造を含むJSONを出力してください。

- art_style: アートスタイル
- sound_mood: サウンドの雰囲気
- visual_theme: 表示の雰囲気・画面演出トーン
- chapters: リスト
    - chapter_index: 数値
    - title: 章タイトル
    - summary: 要約
    - backgrounds: 画像リスト
    - bgm: BGMファイル名
    - characters: キャラクターIDリスト
    - lines: セリフリスト
        - character: キャラクターID
        - voice_file: ボイスファイル名
        - text: セリフ本文
---
{plan_text}
---
"""

    # GPT呼び出し
    res = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "あなたはプロのゲームディレクターです。JSONだけを返してください。"},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.6
    )
    raw = res.choices[0].message.content.strip()

    # Markdownフェンス除去
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw)
        raw = re.sub(r"```$", "", raw).strip()

    # JSONパース
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            (output_dir / "latest_raw.txt").write_text(raw, encoding="utf-8")
            raise
        data = json.loads(m.group(0))

    # キャラクター名のサニタイズとマッピング
    character_map = {}
    for ch in data.get("chapters", []):
        for line in ch.get("lines", []):
            char_id = line.get("character")
            if not char_id:
                continue
            safe = sanitize(char_id)
            character_map[char_id] = safe
            line["safe_character"] = safe
        raw_chars = ch.get("characters", [])
        ch["safe_characters"] = [character_map.get(c, sanitize(c)) for c in raw_chars]

    data["character_map"] = character_map

    # JSON保存
    meta_path = output_dir / "chapter_meta.json"
    meta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ chapter_meta.json を保存しました → {meta_path}")


if __name__ == "__main__":
    main()
