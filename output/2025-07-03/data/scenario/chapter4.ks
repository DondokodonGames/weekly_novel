## 最後の会話シナリオ - TyranoScript形式

```ks
[module name="system"]
[s]
[title time="2000" layer="0" text="最後の会話"]

; 背景設定
[bg storage="last_conversation_bg.jpg" time="2000"]
[playbgm storage="sombre_mood_bgm.mp3"]

; キャラクター登場
[chara_show name="heroine" storage="heroine_normal.png" time="1000" wait="true"]
[chara_show name="hero" storage="hero_normal.png" time="1000" wait="true" x="300"]

; シナリオ開始
[cm]
[ct]

[voice storage="heroine_calm_001.mp3"]
[print font_color="black" wait="true"]
「最後の会話だね。」
[wt]

[voice storage="hero_response_001.mp3"]
[print font_color="black" wait="true"]
「うん、でも何かが終わるわけじゃないさ。」
[wt]

[bg storage="last_conversation_tearful_bg.jpg" time="2000"]
[playse storage="ambient_change.mp3"]
[chara_mod name="heroine" storage="heroine_tearful.png" time="1000" wait="true"]

[voice storage="heroine_tearful_002.mp3"]
[print font_color="black" wait="true"]
「ありがとう、本当に。だけど、笑っていたいの。」
[wt]

[chara_mod name="hero" storage="hero_serious.png" time="1000" wait="true"]
[voice storage="hero_serious_002.mp3"]
[print font_color="black" wait="true"]
「わかった。一緒に笑おう。」
[wt]

[select name="hero_choice"]
「泣かないで」
[wt]
[case text="抱きしめる"]
    [chara_mod name="heroine" storage="heroine_happy.png" time="1000" wait="true"]
    [voice storage="heroine_happy_003.mp3"]
    [print font_color="black" wait="true"]
    「こんなに優しいのね。ありがとう。」
    [wt]
    [jump target="happy_ending.ks"]
[case text="手を握る"]
    [chara_mod name="heroine" storage="heroine_calm.png" time="1000" wait="true"]
    [voice storage="heroine_calm_003.mp3"]
    [print font_color="black" wait="true"]
    「支えてくれてありがとう。これからもずっと…」
    [wt]
    [jump target="continuation_ending.ks"]
[endselect]

[es]
```
- このスクリプトは、キャラクターの感情とシーンの変化に焦点を当てています。
- 選択肢による分岐で異なるエンディングに導かれます。
- 各セリフには対応するボイスファイルがあり、シーンに合ったBGMや環境音が設定されています。

このスクリプトは、上記のルールとフィードバックに従いながら、プレイヤーに感情移入と選択の影響を体験させることを目指しています。
[return]