TyranoScriptの例として、「カフェでの誤解」という章のスクリプトを以下に示します。このスクリプトでは、プレイヤーがカフェでの一連の誤解を解決することを通じて、登場人物との関係を深めていくシナリオを展開します。

```tyranoscript
[title name="カフェでの誤解"]

; 背景設定
[bg storage="cafe.jpg" time=1000]

; BGM開始
[playbgm storage="cafe_theme.mp3" loop=true]

; キャラクター登場
[char name="ヒロ" storage="hiro_normal.png" time=500]

; 導入の会話
[ptext]
「ここいつものカフェ、落ち着くよね。」
[char name="ヒロ" storage="hiro_smile.png" time=300]
[voice storage="hiro_line_001.mp3"]

[char name="マナ" storage="mana_normal.png" time=500]
「うん、だけど、今日はちょっと...」
[voice storage="mana_line_001.mp3"]

; 分岐1: マナの様子を尋ねる
[select name="マナの心配" color="#FFFFFF" background_color="#000000"]
「どうしたの？顔色が悪いけど。」[jump target="concern"]
「気になることがあるの？」[jump target="curiosity"]
[endselect]

*concern
[char name="マナ" storage="mana_worried.png" time=300]
「実はね、今朝、ちょっとしたことで誤解が...」
[voice storage="mana_line_002.mp3"]
[jump target="resolve"]

*curiosity
[char name="マナ" storage="mana_sad.png" time=300]
「うん、誤解されてしまって...」
[voice storage="mana_line_003.mp3"]
[jump target="resolve"]

*resolve
[ptext]
「そんなことがあったんだね。一緒に解決しよう！」
[char name="ヒロ" storage="hiro_concerned.png" time=300]
[voice storage="hiro_line_002.mp3"]

; エピローグ
[char name="マナ" storage="mana_happy.png" time=500]
「ありがとう、ヒロ。すっきりしたよ！」
[voice storage="mana_line_004.mp3"]

; シーン転換
[bg storage="cafe_evening.jpg" time=1000]
[playbgm storage="cafe_night_theme.mp3" loop=true]

; 終了
[end]

```

このスクリプトでは、キャラクターの表情が変化することで感情の変動を表現し、プレイヤーの選択によって展開が変わる点が特徴です。また、背景音楽と声の演出も含めて、没入感を高める工夫がされています。
[return]