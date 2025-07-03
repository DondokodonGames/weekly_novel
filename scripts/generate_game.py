# scripts/generate_game.py

import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ============ 初期設定 ============
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")

# 出力ベースおよび最新ディレクトリ検出
output_base = Path("output")
if not output_base.exists():
    raise FileNotFoundError(f"output ディレクトリが存在しません: {output_base}")
subdirs = [d for d in output_base.iterdir() if d.is_dir()]
if not subdirs:
    raise FileNotFoundError(f"output 内にサブディレクトリがありません: {output_base}")
subdirs.sort(key=lambda p: p.name)
latest_dir = subdirs[-1]
meta_path = latest_dir / "chapter_meta.json"

# chapter_meta.json がないか不正な場合、自動で generate_structure.py を実行
if not meta_path.exists():
    print(f"⚠ メタファイルが存在しません: {meta_path} → generate_structure.py を実行します")
    subprocess.run(["python", "scripts/generate_structure.py"], check=True)

try:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
except json.JSONDecodeError:
    print(f"⚠ メタファイル読み込みエラー: {meta_path} → 再生成を試みます")
    subprocess.run(["python", "scripts/generate_structure.py"], check=True)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

print(f"🎯 使用中のメタファイル: {meta_path}")

policy_path = Path("config/generate_policy.md")
if not policy_path.exists():
    raise FileNotFoundError(f"ポリシーファイルが見つかりません: {policy_path}")
policy_text = policy_path.read_text(encoding="utf-8")
chapters = meta.get("chapters", [])

# ============ 出力先ディレクトリ ============
output_dir   = output_base / today
tyra_dir     = output_dir / "tyrano"
data_dir     = output_dir / "data"
scenario_dir = data_dir / "scenario"
system_dir   = data_dir / "system"

# ディレクトリ作成
for d in (output_dir, tyra_dir, data_dir, scenario_dir, system_dir):
    d.mkdir(parents=True, exist_ok=True)

# ============ テンプレートコピー ============
template_root = Path("engine_template")
if not template_root.exists():
    raise FileNotFoundError(f"テンプレートディレクトリが見つかりません: {template_root}")

# 1. TyranoScript 本体をコピー
shutil.copytree(
    template_root / "tyrano",
    tyra_dir,
    dirs_exist_ok=True
)

# 2. data フォルダ（シナリオ・画像・BGM）をコピー
shutil.copytree(
    template_root / "data",
    data_dir,
    dirs_exist_ok=True
)

# 3. ルートの index.html をコピー
shutil.copy(
    template_root / "index.html",
    output_dir / "index.html"
)

# ============ スクリプト生成関数 ============
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
            {"role": "user",   "content": prompt}
        ],
        temperature=0.8
    )
    return res.choices[0].message.content

# ============ 章ファイルの生成 ============
chapter_files = []
for ch in chapters:
    idx   = ch.get("chapter_index")
    title = ch.get("title")
    print(f"🎬 Generating Chapter {idx}: {title}")
    ks_code = generate_ks_script(ch)
    fname   = f"chapter{idx}.ks"
    path    = scenario_dir / fname
    path.write_text(ks_code + "\n[return]", encoding="utf-8")
    chapter_files.append(fname)

# ============ first.ks の生成 ============
(first:= scenario_dir / "first.ks").write_text(
    "[jump storage=\"title.ks\"]\n", encoding="utf-8"
)

# ============ scenario.ks の生成 ============
(scenario_dir / "scenario.ks").write_text(
    "\n".join(f'[call storage="{f}"]' for f in chapter_files),
    encoding="utf-8"
)

# ============ title.ks の生成 ============
(title_ks:= scenario_dir / "title.ks").write_text("""
; タイトル画面
[layopt layer=0 visible=true]
[bg storage="bgtitle.jpg"]
[call storage="../system/menu_button.ks"]
[cm]
[locate x=400 y=300]
[glink storage="first.ks" text="▶ ゲームをはじめる"]
[locate x=400 y=400]
[glink storage="load.ks" text="📂 セーブから再開"]
[locate x=400 y=500]
[glink storage="ending.ks" text="✖ 終了"]
[s]
*start
[jump storage="chapter1.ks"]
[s]
""", encoding="utf-8")

# ============ ending.ks の生成 ============
(ending_ks:= scenario_dir / "ending.ks").write_text("""
; エンディング画面
[layopt layer=0 visible=true]
[bg storage="bg_ending.jpg"]
[cm]
[locate x=400 y=300]
[glink storage="title.ks" text="▶ タイトルへ戻る"]
[s]
""", encoding="utf-8")

# ============ menu_button.ks の生成 ============
(menu_ks:= system_dir / "menu_button.ks").write_text("""
; メニュー画面カスタム
[link storage="save.ks"    text="📌 Save"]
[link storage="load.ks"    text="📂 Load"]
[link storage="backlog.ks" text="📝 Log"]
[link storage="title.ks"   text="🏠 Title"]
""", encoding="utf-8")

# ============ plugin.kst の生成 ============
(system_dir / "plugin.kst").write_text(
    "; プラグイン定義用ファイル（自動生成）\n", encoding="utf-8"
)

# ============ 空ファイル補完 ============
for fname in ["save.ks", "load.ks", "backlog.ks"]:
    path = scenario_dir / fname
    if not path.exists():
        path.write_text("; 自動生成ダミー\n", encoding="utf-8")

print(f"✅ TyranoScript 全体構成を生成しました → {output_dir}")
