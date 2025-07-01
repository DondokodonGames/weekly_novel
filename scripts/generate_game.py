# ──────────────────────────────
# scripts/generate_game.py
# ──────────────────────────────

import os
import openai
from pathlib import Path
from datetime import datetime

# 日付ベースの企画ファイルと出力先を指定
today = datetime.today().strftime("%Y-%m-%d")
input_path = Path(f"plans/{today}.md")
output_path = Path(f"output/{today}")
output_path.mkdir(parents=True, exist_ok=True)

# APIキーの読み込み（.env または GitHub Secrets）
openai.api_key = os.getenv("OPENAI_API_KEY")

# 企画を読み込む
with open(input_path, "r", encoding="utf-8") as f:
    plan = f.read()

# ChatGPTにHTMLノベルとして出力するようプロンプト
prompt = f"""
以下のノベルゲーム企画に基づき、RenJSで動作するHTMLノベルゲームの構造を出力してください。
- スクリプトは60分相当で構成してください。
- プレイヤーの選択肢が3回登場し、結末が2種類あるようにしてください。
- HTMLとして実行可能な構成で出力してください。

# 企画:
{plan}
"""

response = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたはゲーム開発者であり、ノベルエンジン用のコードを生成します。"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)

html_code = response["choices"][0]["message"]["content"]

# 出力ファイルに保存
with open(output_path / "game.html", "w", encoding="utf-8") as f:
    f.write(html_code)

# 完了メッセージ
print(f"✅ {today} のノベルゲームを生成しました → {output_path / 'game.html'}")
