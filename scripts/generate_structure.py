# scripts/generate_structure.py

import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# OpenAIクライアント初期化
today = datetime.today().strftime("%Y-%m-%d")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# plansフォルダから最新の企画ファイルを選択
plans_dir = Path("plans")
if not plans_dir.exists():
    raise FileNotFoundError(f"企画フォルダが存在しません: {plans_dir}")

# .md ファイルを取得し、ソートして最新を選択
doc_files = sorted(plans_dir.glob("*.md"), key=lambda p: p.name)
if not doc_files:
    raise FileNotFoundError(f"企画ファイルが見つかりません: {plans_dir} に .md ファイルがありません")
plan_path = doc_files[-1]
print(f"🎯 使用中の企画ファイル: {plan_path.name}")

# 出力先ディレクトリ
today_output = Path(f"output/{today}")
today_output.mkdir(parents=True, exist_ok=True)

# 企画本文読み込み
plan_text = plan_path.read_text(encoding="utf-8")

# プロンプト定義（素材情報・演出方針含む）
prompt = f"""
以下はノベルゲームの企画書です。この内容から以下の構造を含むJSONを出力してください：

- art_style: アートスタイル（例: アニメ風、写実風、手書き風）
- sound_mood: サウンドの雰囲気（例: ローファイ、クラシック、緊張感）
- visual_theme: 表示の雰囲気・画面演出トーン（例: 明るい、落ち着いた、陰鬱）

- chapters: 各章について以下の情報をリスト形式で記述してください：
  - chapter_index: 数値で順番
  - title: 各章のタイトル
  - summary: 内容の要約（日本語）
  - backgrounds: 使用される背景画像ファイル名（例: "bg_station_day.jpg"）
  - bgm: 使用されるBGMファイル名（例: "bgm_tension.mp3"）
  - characters: 登場キャラクターID（例: "angry_f", "player_m", "narration_x"）
  - lines: セリフリスト（構造下記）
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

# OpenAI API呼び出し
res = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたはプロのゲームディレクターです。JSON構造でノベルゲームの章構成と演出方針を出力してください。"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.6
)

# JSON部分抽出
data = res.choices[0].message.content.strip()
# 必要に応じて ```json``` タグ除去などの整形を行う

# 保存
today_output.joinpath("chapter_meta.json").write_text(data, encoding="utf-8")
print(f"✅ chapter_meta.json を保存しました → {today_output/'chapter_meta.json'}")
