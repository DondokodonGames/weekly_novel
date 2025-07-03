# scripts/generate_image.py

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI
from urllib.request import urlretrieve


def main():
    # APIキー取得
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)

    # 日付(JST)とパス設定
    tz = ZoneInfo("Asia/Tokyo")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    output_dir = Path("output") / today

    # メタファイルパス
    meta_path = output_dir / "chapter_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Meta file not found: {meta_path}")

    # 出力ディレクトリ
    fg_dir = output_dir / "data" / "fgimage"
    bg_dir = output_dir / "data" / "bgimage"
    fg_dir.mkdir(parents=True, exist_ok=True)
    bg_dir.mkdir(parents=True, exist_ok=True)

    # プレースホルダー
    placeholder_bg = Path("assets/bg/placeholder.jpg")
    placeholder_fg = Path("assets/fg/placeholder.png")

    # メタ読み込み
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    art_style = meta.get("art_style", "anime style")
    visual_theme = meta.get("visual_theme", "soft lighting")
    chapters = meta.get("chapters", [])

    # プロンプト生成関数
    def character_prompt(char_id, expression):
        base = char_id.rstrip("_fm")
        gender = "woman" if char_id.endswith("_f") else "man" if char_id.endswith("_m") else "person"
        return (f"portrait of {gender} character named '{base}', expression: {expression}, "
                f"{art_style}, transparent background, {visual_theme}")

    def background_prompt(bg_name):
        name = Path(bg_name).stem.replace("_", " ")
        return (f"{name}, background for visual novel, no people, "
                f"{art_style}, {visual_theme}")

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
            print(f"🖼️ Generated: {out_path.name}")
        except Exception as e:
            print(f"⚠ Error generating {out_path.name}: {e}\n→ Using placeholder")
            shutil.copy(placeholder, out_path)

    # 背景画像生成
    all_backgrounds = {bg for ch in chapters for bg in ch.get("backgrounds", [])}
    for bg_name in all_backgrounds:
        out_path = bg_dir / bg_name
        if not out_path.exists():
            prompt = background_prompt(bg_name)
            generate_image(prompt, out_path, placeholder_bg)

    # キャラ立ち絵生成
    char_expr_map = {}
    for ch in chapters:
        for line in ch.get("lines", []):
            char_id = line.get("character")
            voice = line.get("voice_file", "")
            if not char_id:
                continue
            expr = "normal"
            if voice and "_" in Path(voice).stem:
                parts = Path(voice).stem.split("_")
                if len(parts) >= 3:
                    expr = parts[2]
            char_expr_map.setdefault(char_id, set()).add(expr)

    for char_id, exprs in char_expr_map.items():
        for expr in exprs:
            fname = f"{char_id}_{expr}.png"
            out_path = fg_dir / fname
            if not out_path.exists():
                prompt = character_prompt(char_id, expr)
                generate_image(prompt, out_path, placeholder_fg)

    print(f"✅ Image generation complete: backgrounds={len(all_backgrounds)}, characters={len(char_expr_map)}")


if __name__ == "__main__":
    main()
