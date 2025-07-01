# Weekly Novel Generator

このリポジトリは、毎週自動でノベルゲームを生成・投稿するシステムです。

## ディレクトリ構成
- 企画/: ゲームの元となる構想（Markdown）を記述
- scripts/: ゲーム生成・投稿用スクリプト
- output/: 自動生成されたゲームと素材

## 使い方
1. `企画/YYYY-MM-DD.md` を記述
2. GitHub Actions が毎週金曜に起動
3. `output/YYYY-MM-DD/` に成果物が出力

## 初期セットアップ
- `.env` を作成してAPIキーを記入
- 必要に応じて `post_to_twitter.py` に認証情報を設定
