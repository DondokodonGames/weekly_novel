import os
import json
from pathlib import Path
from datetime import datetime
from pydub import AudioSegment

today = datetime.today().strftime("%Y-%m-%d")
meta_path = Path(f"output/{today}/chapter_meta.json")
bgm_dir = Path(f"output/{today}/tyrano/data/bgm")
bgm_dir.mkdir(parents=True, exist_ok=True)

# 雰囲気テンプレート → BGM名マップ（必要なら差替）
bgm_templates = {
    "bgm_tension.mp3": "dark_loop.mp3",
    "bgm_cafe_lofi.mp3": "lofi_loop.mp3",
    "bgm_silence.mp3": "silence.mp3"
}

# ダミーのBGM生成（1秒の無音）
def create_dummy_bgm(path: Path):
    silent = AudioSegment.silent(duration=1000)  # 1秒
    silent.export(path, format="mp3")
    print(f"🎵 ダミー生成: {path.name}")

# chapter_meta を解析
if not meta_path.exists():
    raise FileNotFoundError(f"メタファイルが見つかりません: {meta_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))
used_bgm = set(ch["bgm"] for ch in meta if "bgm" in ch)

for bgm_name in used_bgm:
    out_path = bgm_dir / bgm_name
    if not out_path.exists():
        # 今はダミーで作成（将来Suno等と連携可）
        create_dummy_bgm(out_path)

print(f"✅ BGM素材を生成しました: {len(used_bgm)}ファイル")
