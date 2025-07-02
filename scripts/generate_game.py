# scripts/generate_game.py

import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ============ 環境とパスの設定 ============

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")

meta_path = Path(f"output/{today}/chapter_meta.json")
policy_path = Path("config/generate_policy.md")
output_dir = Path(f"output/{today}/tyrano/")
script_dir = output_dir / "data/scenario"
script_dir.mkdir(parents=True, exist_ok=True)

# ============ 入力ファイルの確認 ============

if not meta_path.exists():
    raise FileNotFoundError(f"章メタ情報が存在しません: {meta_path}")
if not policy_path.exists():
    raise FileNotFoundError(f"生成ポリシーファイルが存在しません: {policy_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))
policy_text = policy_path.read_text(encoding="utf-8")

# ============ スクリプト生成関数 ============

def generate_ks_script(chapter):
    prompt = f"""
{policy_text}

# 章タイトル: {chapter["title"]}
# 概要: {chapter["summary"]}
"""
    res = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "あなたはノベルゲーム制作者です。TyranoScriptを正確に生成してください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    return res.choices[0].message.content

# ============ 各章の.ksファイルを生成 ============

chapter_files = []

for ch in meta:
    print(f"🎬 Generating Chapter {ch['chapter_index']}: {ch['title']}")
    ks_code = generate_ks_script(ch)
    fname = f"chapter{ch['chapter_index']}.ks"
    (script_dir / fname).write_text(ks_code, encoding="utf-8")
    chapter_files.append(fname)

# ============ scenario.ks と config.ks を作成 ============

# config.ks（必要最低限）
(script_dir / "config.ks").write_text("; TyranoScript config\n", encoding="utf-8")

# scenario.ks（呼び出し順）
scenario_content = "\n".join([f'[call storage="{f}"]' for f in chapter_files])
(script_dir / "scenario.ks").write_text(scenario_content, encoding="utf-8")

print(f"✅ TyranoScriptデータを生成しました → {script_dir}")
