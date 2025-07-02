# scripts/generate_voice.py

import os
import json
from pathlib import Path
from datetime import datetime
from pydub.generators import Sine
from pydub import AudioSegment

# ============ 初期設定 ============

today = datetime.today().strftime("%Y-%m-%d")
meta_path = Path(f"output/{today}/chapter_meta.json")
voice_dir = Path(f"output/{today}/tyrano/data/voice")
voice_dir.mkdir(parents=True, exist_ok=True)

# ============ 音声生成関数 ============

# ダミーのボイス生成（300msのBeep）
def create_dummy_voice(path: Path):
    tone = Sine(880).to_audio_segment(duration=300)  # 880Hz, 300ms
    tone.export(path, format="mp3")
    print(f"🎤 ダミー生成: {path.name}")

# 将来対応：TTS音声合成（例：OpenAI, VoiceVox 連携）
def generate_tts_voice(text: str, path: Path, speaker="default"):
    # ここにTTS連携処理を組み込む予定（現在は仮）
    create_dummy_voice(path)

# ============ 音声ファイル生成処理 ============

if not meta_path.exists():
    raise FileNotFoundError(f"メタファイルが見つかりません: {meta_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))

generated = set()

for ch in meta:
    for line in ch.get("lines", []):
        vfile = line["voice_file"]
        text = line["text"]
        out_path = voice_dir / vfile

        if not out_path.exists() and vfile not in generated:
            generate_tts_voice(text, out_path)
            generated.add(vfile)

print(f"✅ ボイスファイル生成完了（{len(generated)} ファイル）")
