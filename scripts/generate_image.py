import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")

meta_path = Path(f"output/{today}/chapter_meta.json")
fg_dir = Path(f"output/{today}/tyrano/data/fgimage")
bg_dir = Path(f"output/{today}/tyrano/data/bgimage")
fg_dir.mkdir(parents=True, exist_ok=True)
bg_dir.mkdir(parents=True, exist_ok=True)

# キャラIDを解析してprompt生成
def character_prompt(char_id, expression):
    base = char_id.replace("_f", "").replace("_m", "")
    gender = "a woman" if "_f" in char_id else "a man" if "_m" in char_id else "person"
    return f"portrait of {gender} character with expression: {expression}, anime style, transparent background"

# 背景名からprompt生成
def background_prompt(bg_name):
    parts = bg_name.replace(".jpg", "").split("_")
    place = parts[1] if len(parts) > 1 else "scene"
    time = parts[2] if len(parts) > 2 else "day"
    return f"{place} in the {time}, background for visual novel, no people"

# DALL·E画像生成
def generate_image(prompt, out_path):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1
        )
        url = response.data[0].url
        from urllib.request import urlretrieve
        urlretrieve(url, out_path)
        print(f"🖼️ 生成: {out_path.name}")
    except Exception as e:
        print(f"⚠ エラー: {out_path.name} - {e}")

# chapter_meta を解析
if not meta_path.exists():
    raise FileNotFoundError(f"メタファイルが見つかりません: {meta_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))

# ===== 背景画像の生成 =====
all_backgrounds = set()
for ch in meta:
    all_backgrounds.update(ch.get("backgrounds", []))

for bg_name in all_backgrounds:
    out_path = bg_dir / bg_name
    if not out_path.exists():
        prompt = background_prompt(bg_name)
        generate_image(prompt, out_path)

# ===== 立ち絵画像の生成 =====
all_chars = set()
for ch in meta:
    for char in ch.get("characters", []):
        all_chars.add(char)

# 仮：1キャラ1表情固定で生成（後で表情ごとに展開可）
for char_id in all_chars:
    out_path = fg_dir / f"{char_id}_normal.png"
    if not out_path.exists():
        prompt = character_prompt(char_id, "neutral")
        generate_image(prompt, out_path)

print(f"✅ 画像素材の生成完了（背景: {len(all_backgrounds)} / キャラ: {len(all_chars)}）")
