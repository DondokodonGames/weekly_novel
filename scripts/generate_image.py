import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from urllib.request import urlretrieve

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")

meta_path = Path(f"output/{today}/chapter_meta.json")
fg_dir = Path(f"output/{today}/tyrano/data/fgimage")
bg_dir = Path(f"output/{today}/tyrano/data/bgimage")
placeholder_bg = Path("assets/bg/placeholder.jpg")
placeholder_fg = Path("assets/fg/placeholder.png")

fg_dir.mkdir(parents=True, exist_ok=True)
bg_dir.mkdir(parents=True, exist_ok=True)

if not meta_path.exists():
    raise FileNotFoundError(f"メタファイルが見つかりません: {meta_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))

# === 修正点：metaの形式をdictとして扱う ===
art_style = meta.get("art_style", "anime style")
visual_theme = meta.get("visual_theme", "soft lighting")
chapters = meta.get("chapters", [])

# キャラID + 表情 -> prompt生成
def character_prompt(char_id, expression):
    base = char_id.replace("_f", "").replace("_m", "")
    gender = "a woman" if "_f" in char_id else "a man" if "_m" in char_id else "person"
    return f"portrait of {gender} character named '{base}', expression: {expression}, {art_style}, transparent background, {visual_theme}"

# 背景名からprompt生成
def background_prompt(bg_name):
    parts = bg_name.replace(".jpg", "").split("_")
    place = parts[1] if len(parts) > 1 else "scene"
    time = parts[2] if len(parts) > 2 else "day"
    return f"{place} in the {time}, background for visual novel, no people, {art_style}, {visual_theme}"

# DALL-E APIで画像生成
def generate_image(prompt, out_path, placeholder):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1
        )
        url = response.data[0].url
        urlretrieve(url, out_path)
        print(f"🖼️ 生成: {out_path.name}")
    except Exception as e:
        print(f"⚠ エラー: {out_path.name} - {e}\n→ 代替画像を使用します")
        shutil.copy(placeholder, out_path)

# 背景画像を生成
all_backgrounds = set()
for ch in chapters:
    all_backgrounds.update(ch.get("backgrounds", []))

for bg_name in all_backgrounds:
    out_path = bg_dir / bg_name
    if not out_path.exists():
        prompt = background_prompt(bg_name)
        generate_image(prompt, out_path, placeholder_bg)

# キャラID + 表情パターンを抽出
detected_expressions = set()
char_expression_map = {}

for ch in chapters:
    for line in ch.get("lines", []):
        char_id = line.get("character")
        voice_file = line.get("voice_file", "")
        if not char_id or char_id.endswith("_x"):
            continue
        if "_" in voice_file:
            parts = voice_file.replace(".mp3", "").split("_")
            expression = parts[2] if len(parts) >= 3 else "normal"
        else:
            expression = "normal"
        detected_expressions.add(expression)
        char_expression_map.setdefault(char_id, set()).add(expression)

# 立ち絵生成
for char_id, expressions in char_expression_map.items():
    for expr in expressions:
        fname = f"{char_id}_{expr}.png"
        out_path = fg_dir / fname
        if not out_path.exists():
            prompt = character_prompt(char_id, expr)
            generate_image(prompt, out_path, placeholder_fg)

print(f"✅ 画像素材生成完了（背景: {len(all_backgrounds)}枚 / キャラ: {len(char_expression_map)}人 / 表情: {len(detected_expressions)}種）")
