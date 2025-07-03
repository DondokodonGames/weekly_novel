# scripts/generate_game.py

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ============ 初期設定 ============
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")

meta_path = Path(f"output/{today}/chapter_meta.json")
policy_path = Path("config/generate_policy.md")
# TyranoScriptテンプレート本体が置かれたディレクトリ
template_tyrano = Path("templates/tyrano")

# 出力先フォルダ
tyrano_dir = Path(f"output/{today}/tyrano")
scenario_dir = tyrano_dir / "data" / "scenario"
system_dir = tyrano_dir / "data" / "system"

# フォルダ作成
scenario_dir.mkdir(parents=True, exist_ok=True)
system_dir.mkdir(parents=True, exist_ok=True)

# ============ 入力ファイルチェック ============
if not meta_path.exists():
    raise FileNotFoundError(f"メタファイルが見つかりません: {meta_path}")
if not policy_path.exists():
    raise FileNotFoundError(f"ポリシーファイルが見つかりません: {policy_path}")

# メタとポリシー読み込み
meta = json.loads(meta_path.read_text(encoding="utf-8"))
policy_text = policy_path.read_text(encoding="utf-8")
chapters = meta.get("chapters", [])

# ============ TyranoScript 本体コピー ============
# テンプレートから system フォルダを丸ごとコピー
if template_tyrano.exists():
    src_system = template_tyrano / "data" / "system"
    if src_system.exists():
        shutil.copytree(src_system, system_dir, dirs_exist_ok=True)

# ============ 各章の.ks 生成関数 ============
def generate_ks_script(chapter):
    prompt = f"""
{policy_text}

# 章タイトル: {chapter['title']}
# 概要: {chapter['summary']}
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

# ============ 章ごとのスクリプト出力 ============
chapter_files = []
for ch in chapters:
    idx = ch.get("chapter_index")
    title = ch.get("title")
    print(f"🎬 Generating Chapter {idx}: {title}")
    ks_code = generate_ks_script(ch)
    fname = f"chapter{idx}.ks"
    (scenario_dir / fname).write_text(ks_code + "\n[return]", encoding="utf-8")
    chapter_files.append(fname)

# ============ first.ks を生成 ============
first_ks = scenario_dir / "first.ks"
first_ks.write_text("[jump storage=\"chapter1.ks\"]\n", encoding="utf-8")

# ============ scenario.ks を生成 (線形呼び出し) ============
scenario_content = "\n".join([
    f'[call storage="{f}"]' for f in chapter_files
])
(scenario_dir / "scenario.ks").write_text(scenario_content, encoding="utf-8")

# ============ title.ks の生成 ============
title_ks = scenario_dir / "title.ks"
title_code = """
; タイトル画面
[layopt layer=0 visible=true]
[bg storage=\"bgtitle.jpg\"]
[cm]
[locate x=400 y=300]
[glink storage=\"first.ks\" target=*start text=\"▶ ゲームをはじめる\"]
[locate x=400 y=400]
[glink storage=\"load.ks\" target=*load text=\"📂 セーブから再開\"]
[locate x=400 y=500]
[glink storage=\"ending.ks\" target=*end text=\"✖ 終了\"]
[s]
*start
[jump storage=\"chapter1.ks\"]
[s]
"""
title_ks.write_text(title_code, encoding="utf-8")

# ============ ending.ks の生成 ============
ending_ks = scenario_dir / "ending.ks"
ending_code = """
; エンディング画面
[layopt layer=0 visible=true]
[bg storage=\"bg_ending.jpg\"]
[cm]
[glink storage=\"title.ks\" target=*t text=\"▶ タイトルへ戻る\"]
[s]
"""
ending_ks.write_text(ending_code, encoding="utf-8")

# ============ menu_button.ks の生成 ============
menu_ks = system_dir / "menu_button.ks"
menu_code = """
; メニュー画面カスタム
[link storage=\"save.ks\" text=\"📌 Save\"]
[link storage=\"load.ks\" text=\"📂 Load\"]
[link storage=\"backlog.ks\" text=\"📝 Log\"]
[link storage=\"title.ks\" text=\"🏠 Title\"]
"""
menu_ks.write_text(menu_code, encoding="utf-8")

# ============ 空ファイル / テンプレート不足補完 ============
# 空のsave.ks, load.ks, backlog.ksも system/scenario or system に配置
for fname in ["save.ks", "load.ks", "backlog.ks"]:
    path = scenario_dir / fname
    if not path.exists():
        path.write_text("; 自動生成ダミー\n", encoding="utf-8")

# ============ 完了メッセージ ============
print(f"✅ TyranoScript全体構成を生成しました → {tyrano_dir}")
