# ✅ ノベルゲーム自動生成パイプライン：制作方針とフィードバックまとめ

## 🎯 制作の目的

単なるスクリプトの生成ではなく、「**1時間程度プレイ可能な、面白さを実現したゲーム成果物**」を生成すること。

- TyranoScript形式での出力を採用（HTML5対応）
- 素材（画像・音声・BGM・ボイス）は**ダミーではなく本番品質**
- プレイヤーの選択によって**感情の波・分岐・再接続**が発生し、体験が変化する構成を重視

---

## ✅ フィードバックと制作ルール（自動生成の品質制約）

| 項目 | 内容 | 自動生成への反映ルール |
|------|------|-------------------------|
| 📏 1. 各章の長さ | 短すぎる構成は不可。**100〜150行／15分程度**を目安に構成。 | セリフ数・分岐数・感情起伏を計測し、規定行数を超えるまで自動追加。 |
| 🎭 2. キャラクター描写 | **セリフで性格や背景**を表現。説明的モノローグは禁止。 | キャラの性格は「**行動・口調・リアクション**」で伝える。 |
| 🔀 3. 分岐と変化 | 各章に**最低1回の選択肢と感情変化**を含む。 | 「分岐ごとの感情フラグ」を保持し、各ルートで違いを明示。 |
| 🎧 4. 音声・音楽設計 | 各セリフにボイスファイル、**状況に応じたBGM・環境音**を付ける。 | 自動命名（例：`angry_004.mp3`）＋シーン対応型で割り当て。 |
| 💬 5. ダイアログ構成 | 感情の起伏・間（ま）を重視した**自然な掛け合い**にする。 | 説明的・一方的なセリフを避け、対話で展開する構成に。 |
| ⏹ 6. シーン遷移 | シーンの視覚的・聴覚的な変化（駅→道→カフェ）を盛り込む。 | 各章に**最低1回のBGM・背景切替**を設定。 |
| 🌱 7. エンディング設計 | 関係性の変化・成長・余韻が伝わるように**複数エンディングを設計**。 | 明確な「完結」よりも、「続きを感じさせる構成」を優先。 |

---

## 🔄 その他ルール

- `.ks` ファイル出力時は TyranoScript 構文を厳密に守る
- 各 `.ks` には `title`、`bg`、`playbgm`、`char show`、`voice` を含む
- 章ごとにファイル分割し、`scenario.ks` から順番に呼び出す

---

