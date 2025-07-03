# scripts/generate_assets.py

import os
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI


def sanitize(name: str) -> str:
    """
    ファイルシステム上で安全な文字列に変換
    英数字・アンダースコア・ハイフン以外をアンダースコアに置換する
    """
    return re.sub(r'[^0-9A-Za-z_-]', '_', name)


def generate_dalle_image(prompt: str, output_path: Path):
    """
    DALL·E API で背景画像を生成し保存
    失敗時は placeholder を書き込む
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        url = response.data[0].url
        img_data = requests.get(url).content
        output_path.write_bytes(img_data)
        print(f"🖼️ Generated background: {output_path.name}")
    except Exception as e:
        print(f"⚠️ Background generation failed: {output_path.name} - {e}")
        output_path.write_text("[BG] placeholder", encoding="utf-8")


def main():
    # 日付(JST)設定
    tz = ZoneInfo("Asia/Tokyo")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    output_dir = Path("output") / today

    # メタ読み込み
    meta_path = output_dir / "chapter_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Meta file not found: {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    chapters = meta.get("chapters", [])
    character_map = meta.get("character_map", {})

    # ディレクトリ設定
    data_dir = output_dir / "data"
    bg_dir = data_dir / "bgimage"
    fg_root = data_dir / "fgimage" / "chara"
    bgm_dir = data_dir / "bgm"
    voice_dir = data_dir / "voice"
    for d in (bg_dir, fg_root, bgm_dir, voice_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 資産リストの抽出
    all_backgrounds = {bg for ch in chapters for bg in ch.get("backgrounds", [])}
    all_bgms = {ch.get("bgm") for ch in chapters if ch.get("bgm")}
    raw_chars = {raw for ch in chapters for raw in ch.get("characters", [])}
    voice_entries = []
    for ch in chapters:
        for line in ch.get("lines", []):
            vfile = line.get("voice_file")
            text = line.get("text", "")
            safe_id = line.get("safe_character") or sanitize(line.get("character", ""))
            if vfile:
                voice_entries.append({
                    "safe_id": safe_id,
                    "voice_file": vfile,
                    "text": text
                })

    # 背景画像生成
    for bg in all_backgrounds:
        out_path = bg_dir / bg
        if not out_path.exists():
            prompt = f"{Path(bg).stem.replace('_',' ')}, background for visual novel, no people"
            generate_dalle_image(prompt, out_path)

    # BGM プレースホルダー
    for bgm in all_bgms:
        safe_name = sanitize(bgm)
        out_path = bgm_dir / safe_name
        if not out_path.exists():
            out_path.write_text("[BGM] placeholder", encoding="utf-8")
            print(f"🎵 Created dummy BGM: {safe_name}")

    # キャラ立ち絵プレースホルダー
    for raw in raw_chars:
        safe = character_map.get(raw, sanitize(raw))
        char_dir = fg_root / safe
        char_dir.mkdir(parents=True, exist_ok=True)
        for expr in ("normal", "angry", "smile", "sad"):
            out_path = char_dir / f"{expr}.png"
            if not out_path.exists():
                out_path.write_text("[FG] placeholder", encoding="utf-8")
                print(f"🖼️ Created placeholder FG: {safe}/{expr}.png")

    # ボイスプレースホルダー
    for entry in voice_entries:
        out_path = voice_dir / entry["voice_file"]
        if not out_path.exists():
            out_path.write_text(entry["text"], encoding="utf-8")
            print(f"🎤 Created dummy voice: {entry['voice_file']}")

    print(f"✅ Asset generation complete: backgrounds={len(all_backgrounds)}, bgms={len(all_bgms)}, chars={len(raw_chars)}, voices={len(voice_entries)}")


if __name__ == "__main__":
    main()
