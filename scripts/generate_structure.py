# scripts/generate_structure.py

import os
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI


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

    # 企画ファイル格納ディレクトリ (plans/ またはプロジェクトルート)
    plans_dir = Path("plans")
    if plans_dir.exists():
        md_list = sorted(plans_dir.glob("*.md"), key=lambda p: p.name)
    else:
        md_list = sorted(Path(".").glob("*.md"), key=lambda p: p.name)
    if not md_list:
        raise FileNotFoundError("No markdown (.md) planning file found.")
    plan_path = md_list[-1]
    print(f"🎯 使用中の企画ファイル: {plan_path}")

    # 企画書テキスト読み込み
    plan_text = plan_path.read_text(encoding="utf-8")

    # ポリシーファイル読み込み
    policy_path = Path("config/generate_policy.md")
    policy_text = policy_path.read_text(encoding="utf-8") if policy_path.exists() else ""

    # プロンプト生成
    prompt = f"""
{policy_text}

以下はノベルゲームの企画書です。この内容から以下の構造を含むJSONを出力してください。

- art_style: アートスタイル（例: アニメ風、写実風、手書き風）
- sound_mood: サウンドの雰囲気（例: ローファイ、クラシック、緊張感）
- visual_theme: 表示の雰囲気・画面演出トーン

- chapters: 各章について下記をリストで出力
   - chapter_index: 数値
   - title: タイトル
   - summary: 要約
   - backgrounds: ["bg_station_day.jpg", …]
   - bgm: "bgm_tension.mp3"
   - characters: ["angry_f", …]
   - lines:
       - character: キャラID
       - voice_file: "angry_f_001.mp3"
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

    # Markdownフェンスの除去
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw)
        raw = re.sub(r"```$", "", raw).strip()

    # JSONパース
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            # 解析不能な場合は生データを保存
            (output_dir / "latest_raw.txt").write_text(raw, encoding="utf-8")
            raise
        data = json.loads(m.group(0))

    # JSON保存
    meta_path = output_dir / "chapter_meta.json"
    meta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ chapter_meta.json を保存しました → {meta_path}")


if __name__ == "__main__":
    main()
