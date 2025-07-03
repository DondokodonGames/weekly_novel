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

# 最新の output フォルダから chapter_meta.json を取得
output_base = Path("output")
if not output_base.exists():
    raise FileNotFoundError(f"output ディレクトリが存在しません: {output_base}")
subdirs = [d for d in output_base.iterdir() if d.is_dir()]
if not subdirs:
    raise FileNotFoundError(f"output 内にサブディレクトリがありません: {output_base}")
subdirs.sort(key=lambda p: p.name)
latest_dir = subdirs[-1]
meta_path = latest_dir / "chapter_meta.json"
if not meta_path.exists():
    raise FileNotFoundError(f"メタファイルが存在しません: {meta_path}")
print(f"🎯 使用中のメタファイル: {meta_path}")

# ポリシーファイル
policy_path = Path("config/generate_policy.md")
if not policy_path.exists():
    raise FileNotFoundError(f"ポリシーファイルが見つかりません: {policy_path}")

# 生成先
tyrano_dir = Path(f"output/{today}/tyrano")
scenario_dir = tyrano_dir / "data" / "scenario"
system_dir = tyrano_dir / "data" / "system"
scenario_dir.mkdir(parents=True, exist_ok=True)
system_dir.mkdir(parents=True, exist_ok=True)

# テンプレート準拠のエンジン・システムファイルコピー
template_base = Path("templates/tyrano")
if template_base.exists():
    src_engine = template_base / "tyrano"
    if src_engine.exists():
        shutil.copytree(src_engine, tyrano_dir, dirs_exist_ok=True)
    src_system = template_base / "data" / "system"
    if src_system.exists():
        shutil.copytree(src_system, system_dir, dirs_exist_ok=True)

# JSON読み込み
with open(meta_path, encoding="utf-8") as f:
    meta = json.load(f)
policy_text = policy_path.read_text(encoding="utf-8")
chapters = meta.get("chapters", [])

# スクリプト生成関数
def generate_ks_script(chapter):
    prompt = f"""
{policy_text}

# 章タイトル: {chapter['title']}
# 概要: {chapter['summary']}
"""
    res = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role":"system","content":"あなたはノベルゲーム制作者です。TyranoScriptを正確に生成してください。"},
            {"role":"user","content":prompt}
        ],
        temperature=0.8
    )
    return res.choices[0].message.content

# 各章の.ks作成
chapter_files = []
for ch in chapters:
    idx = ch.get("chapter_index")
    title = ch.get("title")
    print(f"🎬 Generating Chapter {idx}: {title}")
    ks_code = generate_ks_script(ch)
    fname = f"chapter{idx}.ks"
    (scenario_dir / fname).write_text(ks_code + "\n[return]", encoding="utf-8")
    chapter_files.append(fname)

# first.ks
first_ks = scenario_dir / "first.ks"
first_ks.write_text("[jump storage=\"title.ks\"]\n", encoding="utf-8")

# scenario.ks
scenario_content = "\n".join(f'[call storage="{f}"]' for f in chapter_files)
(scenario_dir / "scenario.ks").write_text(scenario_content, encoding="utf-8")

# title.ks
title_ks = scenario_dir / "title.ks"
title_code = """
; タイトル画面
[layopt layer=0 visible=true]
[bg storage=\"bgtitle.jpg\"]
[call storage=\"../system/menu_button.ks\"]
[cm]
[locate x=400 y=300]
[glink storage=\"first.ks\" text=\"▶ ゲームをはじめる\"]
[locate x=400 y=400]
[glink storage=\"load.ks\" text=\"📂 セーブから再開\"]
[locate x=400 y=500]
[glink storage=\"ending.ks\" text=\"✖ 終了\"]
[s]
*start
[jump storage=\"chapter1.ks\"]
[s]
"""
title_ks.write_text(title_code, encoding="utf-8")

# ending.ks
ending_ks = scenario_dir / "ending.ks"
ending_code = """
; エンディング画面
[layopt layer=0 visible=true]
[bg storage=\"bg_ending.jpg\"]
[cm]
[locate x=400 y=300]
[glink storage=\"title.ks\" text=\"▶ タイトルへ戻る\"]
[s]
"""
ending_ks.write_text(ending_code, encoding="utf-8")

# system/menu_button.ks
menu_ks = system_dir / "menu_button.ks"
menu_code = """
; メニュー画面カスタム
[link storage=\"save.ks\" text=\"📌 Save\"]
[link storage=\"load.ks\" text=\"📂 Load\"]
[link storage=\"backlog.ks\" text=\"📝 Log\"]
[link storage=\"title.ks\" text=\"🏠 Title\"]
"""
menu_ks.write_text(menu_code, encoding="utf-8")

# system/plugin.kst
plugin_kst = system_dir / "plugin.kst"
plugin_kst.write_text("; プラグイン定義用ファイル（自動生成）\n", encoding="utf-8")

# 空ファイル補完
for fname in ["save.ks","load.ks","backlog.ks"]:
    path = scenario_dir / fname
    if not path.exists():
        path.write_text("; 自動生成ダミー\n", encoding="utf-8")

print(f"✅ TyranoScript全体構成を生成しました → {tyrano_dir}")
