# scripts/generate_image.py

import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI
from urllib.request import urlretrieve


def sanitize(name: str) -> str:
    # 英数字・アンダースコア・ハイフン以外をアンダースコアに置換
    return re.sub(r'[^0-9A-Za-z_-]', '_', name)


def main():
    # APIキー取得
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)

    # 日付(JST)と出力ディレクトリ設定
    tz = ZoneInfo("Asia/Tokyo")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    output_dir = Path("output") / today

    # メタJSON読み込み
    meta_path = output_dir / "chapter_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"メタファイルが見つかりません: {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    art_style = meta.get("art_style", "anime style")
    visual_theme = meta.get("visual_theme", "soft lighting")
    chapters = meta.get("chapters", [])
    character_map = meta.get("character_map", {})

    # ディレクトリ設定
    data_dir = output_dir / "data"
    bg_dir = data_dir / "bgimage"
    fg_root = data_dir / "fgimage" / "chara"
    bg_dir.mkdir(parents=True, exist_ok=True)
    fg_root.mkdir(parents=True, exist_ok=True)

    placeholder_bg = Path("assets/bg/placeholder.jpg")
    placeholder_fg = Path("assets/fg/placeholder.png")

    # プロンプト生成
    def background_prompt(bg_name):
        name = Path(bg_name).stem.replace("_", " ")
        return f"{name}, background for visual novel, no people, {art_style}, {visual_theme}"

    def character_prompt(raw_id, expression):
        # プロンプトには元の名前と表情を使い、生成後はsafe_idで保存
        base = raw_id.replace("_f", "").replace("_m", "")
        gender = "a woman" if raw_id.endswith("_f") else "a man" if raw_id.endswith("_m") else "person"
        return (
            f"portrait of {gender} character named '{base}', expression: {expression}, "
            f"{art_style}, transparent background, {visual_theme}"
        )

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
            print(f"🖼️ Generated: {out_path}")
        except Exception as e:
            print(f"⚠ Error generating {out_path.name}: {e} → using placeholder")
            shutil.copy(placeholder, out_path)

    # 背景画像生成
    all_backgrounds = {bg for ch in chapters for bg in ch.get("backgrounds", [])}
    for bg_name in all_backgrounds:
        out_path = bg_dir / bg_name
        if not out_path.exists():
            prompt = background_prompt(bg_name)
            generate_image(prompt, out_path, placeholder_bg)

    # キャラ立ち絵生成: raw_id→表情セットのマッピング
    char_expr_map = {}
    for ch in chapters:
        for line in ch.get("lines", []):
            raw_id = line.get("character")
            if not raw_id:
                continue
            # expression は voice_file 名から推測、ない場合は "normal"
            voice = line.get("voice_file", "")
            if voice and "_" in Path(voice).stem:
                parts = Path(voice).stem.split("_")
                expr = parts[2] if len(parts) >= 3 else "normal"
            else:
                expr = "normal"
            char_expr_map.setdefault(raw_id, set()).add(expr)

    # 各キャラごとに safe_id フォルダを作り、表情ごとに画像出力
    for raw_id, exprs in char_expr_map.items():
        safe_id = character_map.get(raw_id, sanitize(raw_id))
        chara_dir = fg_root / safe_id
        chara_dir.mkdir(parents=True, exist_ok=True)
        for expr in exprs:
            out_path = chara_dir / f"{expr}.png"
            if not out_path.exists():
                prompt = character_prompt(raw_id, expr)
                generate_image(prompt, out_path, placeholder_fg)

    print(f"✅ 画像素材生成完了: 背景={len(all_backgrounds)}枚, キャラ={len(char_expr_map)}名")


if __name__ == "__main__":
    main()
