## TyranoScriptの基本構成例

以下は、ノベルゲームの章「駅での出会い」の導入部分をTyranoScriptを用いて記述したスクリプトの具体例です。このスクリプトは、前述の制作方針とフィードバックを元に構成されています。

```tyranoscript
[title name="駅での出会い"]

; 初期設定
[s]
[bg storage="station.jpg" time=1000]
[playbgm storage="ambient_station.mp3"]

; 主人公（ナレーション）
[cm]
[ct]
[chara_show name="主人公" storage="protagonist_normal.png" jname=""]
[playse storage="footsteps.mp3"]
「ここはいつもの駅。毎朝の通勤で訪れるけれど、今日は何か空気が違う気がする...」

; 女性キャラクター登場
[chara_show name="怒りやすい女性" storage="angry_woman_normal.png" jname="美咲"]
[playse storage="sudden_noise.mp3"]
[cm]
「すみません、ちょっとそこどいてもらえますか？」[p]
「あれ？ あなた、もしかして...」

; 選択肢
[select name="first_meeting" color="#FFFFFF" storage=""]
[option text="「はい、何かご用ですか？」" target="response_friendly"]
[option text="「えっ、と、あの...」" target="response_confused"]
[endselect]

*response_friendly
[cm]
「はい、何かご用ですか？」[p]
「いえ、その... ここにいたら邪魔だからどいてほしいの。」[p]
「そうですか、分かりました。」[p]
[cm]
[trans time=1000]
[bg storage="cafe.jpg"]
[playbgm storage="calm_breeze.mp3"]
[chara_hide name="怒りやすい女性"]
[chara_show name="怒りやすい女性" storage="angry_woman_calm.png"]
「ここはもっと静かね。ありがとう、あなたのおかげよ。」
[trans time=1000]

*response_confused
[cm]
「えっ、と、あの...」[p]
「ちょっと、あなた、どいてって言ってるのに！」[p]
[chara_hide name="怒りやすい女性"]
[chara_show name="怒りやすい女性" storage="angry_woman_angry.png"]
「もういい！ 私一人でどうにかするから！」
[bg storage="station_crowded.jpg" time=1000]
[playse storage="crowd_noise.mp3"]

; 章の終了と次のシナリオへのリンク
[cm]
[s]
[link storage="next_chapter.ks" target="*start" text="次の章へ"]

```

このスクリプトでは、以下の要素が実装されています：
- 背景画像とBGMの変更によるシーンの遷移
- キャラクターの登場と感情表現の変化
- 効果音の利用
- プレイヤーの選択による物語の分岐
- 次のシナリオへのリンク

このように各章をファイル分割し、`scenario.ks` から順番に呼び出すことで、シームレスなゲーム体験を提供します。
[return]