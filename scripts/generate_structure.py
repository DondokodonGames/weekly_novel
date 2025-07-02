import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# OpenAIクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 今日の日付を取得
today = datetime.today().strftime("%Y-%m-%d")

# 入力・出力パスの設定
input_path = Path(f"plans/{today}.md")
output_path = Path(f"output/{today}")
output_path.mkdir(parents=True, exist_ok=True)

# 入力ファイルの読み込み
if not input_path.exists():
    raise FileNotFoundError(f"企画ファイルが存在しません: {input_path}")

with input_path.open("r", encoding="utf-8") as f:
    plan_text = f.read()

# プロンプト構築
prompt = f"""
以下は、ノベルゲームの初期企画です。この企画をもとに：

1. 面白さ・テーマ性・構造的魅力を分析してください。
2. 分岐・選択肢・キャラクター感情変化などを含んだ、1時間相当の構成（5章＋エピローグ）を設計してください。
3. 各章は章タイトル・状況・選択肢の概要を含み、後でスクリプト化できる粒度で出力してください。

# 企画原文:
{plan_text}
"""

# 新しいAPI形式で呼び出し
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたはゲームデザイナーであり、ノベルゲームの設計と構造を分析・構築する役割です。"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)

# 出力をファイルに保存
result_text = response.choices[0].message.content
(output_path / "structure.md").write_text(result_text, encoding="utf-8")

print(f"構造設計ファイルを保存しました: {output_path / 'structure.md'}")
