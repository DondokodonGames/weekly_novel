
; タイトル画面
[layopt layer=0 visible=true]
[bg storage="bgtitle.jpg"]
[call storage="../system/menu_button.ks"]
[cm]
[locate x=400 y=300]
[glink storage="first.ks" text="▶ ゲームをはじめる"]
[locate x=400 y=400]
[glink storage="load.ks" text="📂 セーブから再開"]
[locate x=400 y=500]
[glink storage="ending.ks" text="✖ 終了"]
[s]
*start
[jump storage="chapter1.ks"]
[s]
