以下は、TyranoScriptを使用したノベルゲームの章「駅での出会い」のスクリプト例です。この章では、プレイヤーが怒りっぽい女性キャラクターとの初めての出会いを経験します。プレイヤーの選択によって物語の進行が変わる分岐点も設けています。

```tyranoscript
[title name="駅での出会い"]

; 背景画像とBGMの設定
[bg storage="station.jpg" time=1000]
[playbgm storage="ambient_station.mp3" loop=true]

; 怒りっぽい女性キャラクターの登場
[char name="カナ" storage="kana_angry.png" time=500]
[ptext page=false]
「何よ、その顔！邪魔なんだけど！」
[endptext]

; ボイスファイルの再生
[voice storage="kana_angry_001.mp3"]

[ptext]
彼女は、駅のホームで小さなバッグを地に叩きつけながら、怒りを露わにしています。
[endptext]

; プレイヤーの選択肢を提供
[select color="#FFFFFF" bg="menu_bg.png"]
「すみません、気を悪くさせるつもりはありませんでした」[jump target="apologize"]
「なぜそんなに怒っているんですか？」[jump target="ask_reason"]
[endselect]

*apologize
[ptext page=false]
「あなたがそう言うなら、仕方ないわね。でも、気をつけてよね！」
[endptext]
[voice storage="kana_relief_001.mp3"]
[jump target="continue_story"]

*ask_reason
[ptext page=false]
「それが知りたいの？ 私の日はもう最悪なの！ 今にも泣きそうよ！」
[endptext]
[voice storage="kana_angry_002.mp3"]
[jump target="continue_story"]

*continue_story
[ptext]
どうやら彼女は、今日一日の出来事によって精神的に不安定な様子です。
[endptext]

[ptext]
私は彼女を落ち着かせるために、近くのカフェへ誘うことにしました。
[endptext]

; シーンの遷移
[trans time=2000]
[bg storage="cafe.jpg" time=1000]
[playbgm storage="cafe_bgm.mp3" loop=true]
[ptext]
カフェに着くと、彼女は少し落ち着きを取り戻したようです。
[endptext]

[ptext]
「ごめんなさい、さっきはちょっと…」と彼女が静かに謝ると、私は笑って「気にしないで」と返しました。
[endptext]

; エピローグへの準備
[wait time=3000]
[end]
```

このスクリプトは、各セリフにボイスファイルを割り当て、キャラクターの感情を効果的に伝える音楽と背景画像の切り替えを含みます。また、選択肢による分岐を設けており、プレイヤーの選択が物語の展開に直接的な影響を及ぼします。
[return]