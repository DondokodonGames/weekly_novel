# scripts/generate_game.py

import os
import json
import shutil
import subprocess
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

    # 日付(JST)と出力ディレクトリ設定
    tz = ZoneInfo("Asia/Tokyo")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    output_base = Path("output")
    output_dir = output_base / today
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1) テンプレート丸ごとコピー
    template_root = Path("engine_template")
    if not template_root.exists():
        raise FileNotFoundError(f"Template directory not found: {template_root}")
    shutil.copytree(template_root, output_dir, dirs_exist_ok=True)
    print(f"✅ Copied template to {output_dir}")

    # パス定義
    tyra_dir = output_dir / "tyrano"
    data_dir = output_dir / "data"
    scenario_dir = data_dir / "scenario"
    system_dir = data_dir / "system"

    # 2) scenario/system をクリアして再作成
    for d in (scenario_dir, system_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    print("✅ Initialized scenario/system directories")

    # 3) メタJSONの読み込み
    subdirs = [d for d in output_base.iterdir() if d.is_dir() and d.name != today]
    subdirs.sort(key=lambda p: p.name)
    if not subdirs:
        raise FileNotFoundError(f"No previous output directory found in {output_base}")
    latest_meta_dir = subdirs[-1]
    meta_path = latest_meta_dir / "chapter_meta.json"
    if not meta_path.exists():
        print(f"⚠ Meta file not found: {meta_path}. Running generate_structure.py")
        subprocess.run(["python", "scripts/generate_structure.py"], check=True)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    chapters = meta.get("chapters", [])

    # 4) ポリシー読み込み
    policy_file = Path("config/generate_policy.md")
    policy_text = policy_file.read_text(encoding="utf-8") if policy_file.exists() else ""

    # 生成関数
    def generate_script(ch):
        prompt = f"{policy_text}\n\n# 章タイトル: {ch['title']}\n# 概要: {ch['summary']}\n"
        res = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたはノベルゲーム制作者です。TyranoScriptを正確に生成してください。"},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.8
        )
        return res.choices[0].message.content

    # 5) 章ファイル生成
    chapter_files = []
    for ch in chapters:
        idx = ch.get("chapter_index")
        print(f"🎬 Generating Chapter {idx}: {ch.get('title')}")
        ks_code = generate_script(ch)
        fname = f"chapter{idx}.ks"
        (scenario_dir / fname).write_text(ks_code + "\n[return]", encoding="utf-8")
        chapter_files.append(fname)

    # first.ks
    (scenario_dir / "first.ks").write_text('[jump storage="title.ks"]\n', encoding="utf-8")
    # scenario.ks
    calls = "\n".join(f'[call storage="{f}"]' for f in chapter_files)
    (scenario_dir / "scenario.ks").write_text(calls, encoding="utf-8")

    # title.ks
    title_code = """
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
"""
    (scenario_dir / "title.ks").write_text(title_code, encoding="utf-8")

    # ending.ks
    ending_code = """
; エンディング画面
[layopt layer=0 visible=true]
[bg storage="bg_ending.jpg"]
[cm]
[locate x=400 y=300]
[glink storage="title.ks" text="▶ タイトルへ戻る"]
[s]
"""
    (scenario_dir / "ending.ks").write_text(ending_code, encoding="utf-8")

    # menu_button.ks
    menu_code = """
; メニュー画面カスタム
[link storage="save.ks"    text="📌 Save"]
[link storage="load.ks"    text="📂 Load"]
[link storage="backlog.ks" text="📝 Log"]
[link storage="title.ks"   text="🏠 Title"]
"""
    (system_dir / "menu_button.ks").write_text(menu_code, encoding="utf-8")

    # plugin.kst
    (system_dir / "plugin.kst").write_text("; プラグイン定義用ファイル（自動生成）\n", encoding="utf-8")

    # ダミー save/load/backlog
    for fname in ["save.ks", "load.ks", "backlog.ks"]:
        p = scenario_dir / fname
        if not p.exists():
            p.write_text("; 自動生成ダミー\n", encoding="utf-8")

    print(f"✅ TyranoScript 全体構成を生成しました → {output_dir}")


if __name__ == "__main__":
    main()
