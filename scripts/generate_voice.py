# scripts/generate_voice.py

import os
import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from pydub.generators import Sine
from pydub import AudioSegment


def sanitize(name: str) -> str:
    """
    ファイル名として安全な文字列に変換
    英数字・アンダースコア・ハイフン以外をアンダースコアに置換する
    """
    return re.sub(r'[^0-9A-Za-z_-]', '_', name)


def create_dummy_voice(path: Path):
    """
    ダミーのボイス生成（300msのビープ音）
    将来的にTTS連携を実装可能
    """
    tone = Sine(880).to_audio_segment(duration=300)
    tone.export(path, format="mp3")
    print(f"🎤 Created dummy voice: {path.name}")


def generate_tts_voice(text: str, path: Path, speaker: str = "default"):
    """
    TTS音声合成フック
    現在はダミー実装、後でTTS API連携を追加
    """
    # TODO: integrate real TTS service (e.g., OpenAI, VoiceVox)
    create_dummy_voice(path)


def main():
    # APIキー／Tゾーン準備
    tz = ZoneInfo("Asia/Tokyo")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    output_dir = Path("output") / today

    # メタJSON読み込み
    meta_path = output_dir / "chapter_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Meta file not found: {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    # 出力先ディレクトリ
    voice_dir = output_dir / "data" / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    # キャラ safe_id マッピング
    character_map = meta.get("character_map", {})

    generated = set()
    # 各章のセリフごとに音声ファイル生成
    for ch in meta.get("chapters", []):
        for line in ch.get("lines", []):
            raw_id = line.get("character")
            safe_id = character_map.get(raw_id, sanitize(raw_id)) if raw_id else sanitize("unknown")
            vfile = line.get("voice_file")
            if not vfile:
                continue
            # 安全なファイル名
            safe_vfile = sanitize(vfile)
            out_path = voice_dir / safe_vfile

            if safe_vfile not in generated:
                text = line.get("text", "")
                generate_tts_voice(text, out_path, speaker=safe_id)
                generated.add(safe_vfile)

    print(f"✅ Voice generation complete: {len(generated)} files")


if __name__ == "__main__":
    main()
