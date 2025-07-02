import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
today = datetime.today().strftime("%Y-%m-%d")

meta_path = Path(f"output/{today}/chapter_meta.json")
voice_dir = Path(f"output/{today}/tyrano/data/voice")
voice_dir.mkdir(parents=True, exist_ok=True)

# 話者を性別サフィックスから自動推定
def get_voice_speaker(char_id):
    if char_id.endswith("_f"):
        return "nova"
    elif char_id.endswith("_m"):
        return "shimmer"
    else:
        return "echo"  # narration_x など

# 音声生成
def generate_voice(text, out_path, speaker="nova"):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=speaker,
            input=text
        )
        response.stream_to_file(out_path)
        print(f"🔊 生成: {out_path.name}")
    except Exception as e:
        print(f"⚠ エラー: {out_path.name} - {e}")

# chapter_meta.json を読み込み
if not meta_path.exists():
    raise FileNotFoundError(f"メタファイルが見つかりません: {meta_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))
generated = 0

# 各セリフごとに音声ファイルを生成
for chapter in meta:
    for line in chapter.get("lines", []):
        char_id = line.get("character", "narration_x")
        text = line["text"]
        vfile = line["voice_file"]
        out_path = voice_dir / vfile

        if not out_path.exists():
            speaker = get_voice_speaker(char_id)
            generate_voice(text, out_path, speaker)
            generated += 1

print(f"✅ 音声生成完了: {generated}ファイル")
