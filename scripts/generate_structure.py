# scripts/generate_structure.py

import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")

plan_path = Path(f"plans/{today}.md")
output_path = Path(f"output/{today}")
output_path.mkdir(parents=True, exist_ok=True)

if not plan_path.exists():
    raise FileNotFoundError(f"企画ファイルが存在しません: {plan_path}")

plan_text = plan_path.read_text(encoding="utf-8")

# プロンプトで構造抽出を依頼（素材情報含む）
prompt = f"""
以下はノベルゲームの企画書です。この内容から以下の構造を含むJSONを出力してください：

- chapter_index: 数値で順番
- title: 各章のタイトル
- summary: 内容の要約（日本語）
- backgrounds: 章で使用される背景画像ファイル名リスト（例: "bg_station_day.jpg"）
- bgm: 使用されるBGMファイル名（例: "bgm_tension.mp3"）
- characters: 登場するキャラクターID（例: "angry_f", "player_m", "narration_x"）※性別サフィックスを含めてください
- lines: 以下の構造のセリフリスト
    - character: キャラID（narration_x なども可）
    - voice_file: 自動命名された音声ファイル名（例: "angry_f_001.mp3"）
    - text: セリフ本文（20〜50文字）

【命名ルール】
- 背景画像: bg_場所_時間帯.jpg
- BGM: bgm_雰囲気.mp3
- 立ち絵: キャラID_表情.png（例: angry_f_smile.png）
- ボイス: キャラID_連番3桁.mp3（例: angry_f_001.mp3）
- キャラIDには必ず性別サフィックスを含めてください：
  - 女性: `_f` / 男性: `_m` / 不定・地の文: `_x`

以下が企画本文です：

---
{plan_text}
---
"""

res = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたはプロのゲームディレクターです。JSON構造でノベルゲームの章構成と素材指定を出力してください。"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.6
)

structured_json = res.choices[0].message.content.strip()

# 保存
(output_path / "chapter_meta.json").write_text(structured_json, encoding="utf-8")
print(f"✅ chapter_meta.json を保存しました → {output_path/'chapter_meta.json'}")
