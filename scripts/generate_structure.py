# scripts/generate_structure.py

import os
import json
import re
from pathlib import Path
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
plans_dir = Path("plans")
if not plans_dir.exists():
    raise FileNotFoundError(f"企画フォルダが存在しません: {plans_dir}")

# pick the latest .md in plans/
mds = sorted(plans_dir.glob("*.md"), key=lambda p: p.name)
if not mds:
    raise FileNotFoundError(f"plans/ に .md ファイルがありません")
plan_path = mds[-1]
print(f"🎯 使用中の企画ファイル: {plan_path.name}")

today = datetime.today().strftime("%Y-%m-%d")
output_dir = Path("output") / today
output_dir.mkdir(parents=True, exist_ok=True)

plan_text = plan_path.read_text(encoding="utf-8")

prompt = f"""
以下はノベルゲームの企画書です。この内容から以下の構造を含むJSONを出力してください：

- art_style: アートスタイル（例: アニメ風、写実風、手書き風）
- sound_mood: サウンドの雰囲気（例: ローファイ、クラシック、緊張感）
- visual_theme: 表示の雰囲気・画面演出トーン

- chapters: 各章について下記をリストで出力
   - chapter_index: 数値
   - title: タイトル
   - summary: 要約
   - backgrounds: [\"bg_station_day.jpg\", …]
   - bgm: \"bgm_tension.mp3\"
   - characters: [\"angry_f\", …]
   - lines: 
       - character: キャラID
       - voice_file: \"angry_f_001.mp3\"
       - text: セリフ本文

以下が企画本文です：

---
{plan_text}
---
"""

res = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたはプロのゲームディレクターです。JSONだけを返してください。"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.6
)

raw = res.choices[0].message.content.strip()

# Strip markdown fences if present
if raw.startswith("```"):
    # remove ```json ... ``` or ```
    raw = re.sub(r"^```(?:json)?", "", raw)
    raw = re.sub(r"```$", "", raw).strip()

# Try to parse, or fallback to extracting first {…} block
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        print("⚠️ JSONが見つかりませんでした。生の応答を output/latest_raw.txt に保存します。")
        (output_dir / "latest_raw.txt").write_text(raw, encoding="utf-8")
        raise
    data = json.loads(m.group(0))

# Finally write a clean JSON file
with open(output_dir / "chapter_meta.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ chapter_meta.json を保存しました → {output_dir/'chapter_meta.json'}")
