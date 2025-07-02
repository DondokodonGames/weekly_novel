# scripts/generate_assets.py

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")
meta_path = Path(f"output/{today}/chapter_meta.json")
project_dir = Path(f"output/{today}/tyrano/data")

bg_dir = project_dir / "bgimage"
fg_dir = project_dir / "fgimage"
bgm_dir = project_dir / "bgm"
voice_dir = project_dir / "voice"

for d in [bg_dir, fg_dir, bgm_dir, voice_dir]:
    d.mkdir(parents=True, exist_ok=True)

# ========= ヘルパー関数 ============

def generate_dalle_image(prompt: str, output_path: Path):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        img_url = response.data[0].url
        img_data = requests.get(img_url).content
        output_path.write_bytes(img_data)
        print(f"🖼 背景生成: {output_path.name}")
    except Exception as e:
        print(f"⚠ 背景生成失敗: {output_path.name} - {e}")
        output_path.write_text("dummy", encoding="utf-8")

def create_placeholder(path: Path, kind: str):
    if not path.exists():
        path.write_text(f"[{kind}] placeholder", encoding="utf-8")

# ============ データ読み込み ============

if not meta_path.exists():
    raise FileNotFoundError(f"章メタ情報が見つかりません: {meta_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))

# ============ 各種素材生成 ============

all_bgs = set()
all_bgms = set()
all_chars = set()
all_voices = []

for ch in meta:
    all_bgs.update(ch.get("backgrounds", []))
    all_bgms.update(ch.get("bgm", []))
    all_chars.update(ch.get("characters", []))
    all_voices.extend(ch.get("lines", []))

# 背景画像（DALL·E）
for bg_name in all_bgs:
    output_path = bg_dir / bg_name
    prompt = f"背景画像: {bg_name.replace('bg_', '').replace('.jpg','').replace('_',' ')}、アニメ風、明るい色調"
    generate_dalle_image(prompt, output_path)

# BGM（仮置き）
for bgm in all_bgms:
    create_placeholder(bgm_dir / bgm, "BGM")

# 立ち絵（仮配置: 感情4パターン）
for char in all_chars:
    for emotion in ["normal", "angry", "smile", "sad"]:
        fname = f"{char}_{emotion}.png"
        create_placeholder(fg_dir / fname, "FG")

# ボイス（仮：テキストを保存するだけ。TTS自動化は別スクリプトへ）
for line in all_voices:
    vfile = line["voice_file"]
    text = line["text"]
    vpath = voice_dir / vfile
    if not vpath.exists():
        vpath.write_text(text, encoding="utf-8")

# ============ 完了 ============

print(f"✅ 素材生成完了：背景{len(all_bgs)}件 / キャラ{len(all_chars)} / BGM{len(all_bgms)} / ボイス{len(all_voices)}件")
