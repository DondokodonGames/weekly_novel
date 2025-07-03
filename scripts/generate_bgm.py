# scripts/generate_bgm.py

import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


def sanitize(name: str) -> str:
    """
    ファイル名として安全な文字列に変換
    英数字・アンダースコア・ハイフン以外をアンダースコアに置換する
    """
    import re
    return re.sub(r'[^0-9A-Za-z_-]', '_', name)


def create_dummy_bgm(path: Path):
    """
    ダミーのBGMプレースホルダーを生成
    --ffmpeg不要でテキストファイルとして置換。
    将来的にSuno API等と連携して本番生成可能
    """
    path.write_text("[BGM] placeholder", encoding="utf-8")
    print(f"🎵 Created dummy BGM placeholder: {path.name}")


def main():
    # 日付(JST)取得
    tz = ZoneInfo("Asia/Tokyo")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    output_dir = Path("output") / today

    # メタJSON読み込み
    meta_path = output_dir / "chapter_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Meta file not found: {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    # BGM 出力先ディレクトリ
    bgm_dir = output_dir / "data" / "bgm"
    bgm_dir.mkdir(parents=True, exist_ok=True)

    # 使われているBGMファイル名の取得
    chapters = meta.get("chapters", [])
    used_bgm = {ch.get("bgm") for ch in chapters if ch.get("bgm")}

    # BGM生成／ダミー出力
    for bgm_name in used_bgm:
        safe_name = sanitize(bgm_name)
        out_path = bgm_dir / safe_name
        if not out_path.exists():
            create_dummy_bgm(out_path)

    print(f"✅ BGM素材生成完了: {len(used_bgm)} ファイル")


if __name__ == "__main__":
    main()
