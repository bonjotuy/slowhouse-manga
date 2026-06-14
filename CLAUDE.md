# 週刊スローハウス 漫画制作プロジェクト

## プロジェクト概要
全国展開の宿「スローハウス」を舞台にした週刊連載漫画。
実体験をベースに、少年漫画風の伏線・熱い展開に昇華させる。

## ディレクトリ構成
```
slowhouse-manga/
├── characters/          # キャラクターシート（テキスト）
├── episodes/            # 各エピソード
│   ├── ep001/
│   │   ├── input.md     # 実体験の元ネタ
│   │   ├── concept.md   # 少年漫画風コンセプト（伏線・熱い展開）
│   │   ├── name.md      # ネーム構成案（コマ割り）
│   │   ├── script.md    # 台本（セリフ全文）
│   │   └── prompts.md   # nanobanana用プロンプト
│   └── ...
├── world/               # 世界観・設定
│   └── slowhouse.md     # スローハウスの世界観
└── scripts/             # 自動生成スクリプト
    └── generate.py      # エピソード生成スクリプト
```

## 制作フロー
1. `episodes/epXXX/input.md` に実体験を書く
2. `python scripts/generate.py epXXX` を実行
3. concept.md → name.md → script.md → prompts.md が自動生成される
4. nanobananaで各コマの画像を生成
5. Instagramに投稿

## スタイルガイド（少年漫画風）
- 伏線は必ず3エピソード以内に回収
- 各話に「熱い台詞」を1つ以上
- 主人公は常に成長している
- ゲスト登場人物の「人生の転機」を描く
