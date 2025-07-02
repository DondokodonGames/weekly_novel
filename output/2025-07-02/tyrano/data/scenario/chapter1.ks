# 📜 TyranoScriptの生成例：「駅での出会い」

以下はTyranoScriptを使用したノベルゲーム章「駅での出会い」のスクリプトの一部です。このスクリプトは指定されたフィードバックと制作ルールに基づいて設計されています。

```tyrano
[title name="駅での出会い"]

; 背景設定
[bg storage="station.jpg" time=1000]

; 音楽開始
[playbgm storage="busy_station.mp3"]

; 主人公の登場
[char name="主人公" face="protagonist_normal.png" storage="protagonist.png" jname="シュン"]
「ここが新しい街か…ちょっと慌ただしいな。」

; 怒っている女性の登場
[char name="怒る女性" face="angry_woman_angry.png" storage="angry_woman.png" jname="アイコ"]
「何よ！道を塞がないでよ！」

; 音声再生
[voice storage="angry_001.mp3"]

; 主人公のリアクション
[char name="主人公" face="protagonist_surprised.png"]
「え、あ、すみません…」

; 分岐の選択肢
[select name="choice1" color="#FFB6C1"]
[choice storage="apology.ks" target=*apology label="謝る"]
[choice storage="ignore.ks" target=*ignore label="無視する"]
[endselect]

*apology
[char name="主人公" face="protagonist_apology.png"]
「本当に申し訳なかったです。気をつけます。」

; 音声再生
[voice storage="apology_001.mp3"]

; BGMの変更
[playbgm storage="calm_moment.mp3"]

; 女性の反応
[char name="怒る女性" face="angry_woman_calm.png"]
「…まあ、いいわ。気をつけて。」

; バックグラウンド変更
[bg storage="station_night.jpg" time=1000]

; エンドシーンへ
[trans time=1500]
[jump storage="next_chapter.ks"]

*ignore
[char name="主人公" face="protagonist_angry.png"]
「（無視して進む…）」

; 音声再生
[voice storage="ignore_001.mp3"]

; 環境音の変更
[playse storage="crowd_murmur.mp3"]

[char name="怒る女性" face="angry_woman_furious.png"]
「信じられない！ちゃんと謝りなさいよ！」

; シーンの変更
[bg storage="station_crowded.jpg" time=1000]

; エンドシーンへ
[trans time=1500]
[jump storage="next_chapter.ks"]
```

このスクリプトは、ユーザー選択によって異なる結果が発生する分岐点を含んでおり、感情の変化が反映された対話とシーンの変更が含まれています。また、各段階で適切な音声や音楽が割り当てられています。