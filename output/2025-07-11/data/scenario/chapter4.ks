### TyranoScript シナリオファイル: last_conversation.ks

```tyranoscript
[title name="最後の会話"]

; 初期設定
[s]
[bg storage="room_background.jpg" time=1000]
[playbgm storage="calm_scene.mp3"]

; キャラクターの登場
[chara_show id="angry_woman" storage="angry_woman_normal.png" time=600]
[chara_show id="protagonist" storage="protagonist_smile.png" time=600]

; プロタゴニストのセリフ
[say name="protagonist"]
「最後にもう一度だけ、話をしよう。」

; 女性の反応
[chara_mod id="angry_woman" storage="angry_woman_serious.png" time=500]
[say name="angry_woman"]
「…わかった。話すことはもう何もないと思っていたけれど。」

; 分岐の選択肢
[select link="理解を示す" target=*understanding]
[select link="問いただす" target=*questioning]

*understanding
[say name="protagonist"]
「君の気持ちも理解しているつもりだ。辛かったよね。」

[chara_mod id="angry_woman" storage="angry_woman_softened.png" time=500]
[say name="angry_woman"]
「ええ、でも、あなたと話して少し楽になったわ。ありがとう。」

[jump target="final_reaction"]

*questioning
[say name="protagonist"]
「でも、本当にそれだけ？何か隠していることはないの？」

[chara_mod id="angry_woman" storage="angry_woman_angry.png" time=500]
[say name="angry_woman"]
「！…あなたには関係ないわ。」

[jump target="final_reaction"]

; 最終リアクション
*final_reaction
[chara_mod id="angry_woman" storage="angry_woman_smiling.png" time=500]
[say name="angry_woman"]
「でも、あなたとのこの時間は大事だった。ありがとう。」

; エンディングへの移行
[say name="protagonist"]
「どういたしまして。また、いつでも話しに来てください。」

[bgm_stop time=1500]
[chara_hide id="angry_woman" time=1000]
[chara_hide id="protagonist" time=1000]
[end]
```

このスクリプトは、指定されたルールとキャラクターIDマッピングに基づいています。シナリオは感情の起伏、分岐の選択、キャラクターの進化を示し、視聴覚的な要素も同時に扱っています。それぞれのセクション（分岐、リアクション）は、読者に異なる感情を与えるよう設計されています。
[return]