# scripts/extract_meta.py

from pathlib import Path
from datetime import datetime
import json

# 入力と出力のパス設定
today = datetime.today().strftime("%Y-%m-%d")
input_path = Path(f"output/{today}/structure.md")
output_path = Path(f"output/{today}/chapter_meta.json")

if not input_path.exists():
    raise FileNotFoundError(f"{input_path} が存在しません")

lines = input_path.read_text(encoding="utf-8").splitlines()
chapters = []

for i, line in enumerate(lines):
    if line.startswith("## "):
        title = line[3:].strip()
        summary = ""
        # 次の非空行を要約として拾う
        for j in range(i+1, len(lines)):
            if lines[j].strip():
                summary = lines[j].strip()
                break
        chapters.append({
            "chapter_index": len(chapters) + 1,
            "title": title,
            "summary": summary
        })

# 保存
output_path.write_text(json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ {output_path} を生成しました")
