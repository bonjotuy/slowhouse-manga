# 週刊スローハウス 制作システム

実体験 → 少年漫画エピソード → nanobananaプロンプト を自動生成するワークフロー。

## セットアップ

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-api-key"
```

## 使い方

### 1. 実体験を書く
```
episodes/ep001/input.md に実体験メモを書く
```

### 2. 全自動生成（推奨）
```bash
python scripts/generate.py ep001
```

以下が自動生成される：
- `concept.md` - 少年漫画風コンセプト（伏線・熱い展開）
- `name.md` - ネーム構成案（コマ割り・演出）
- `script.md` - 台本（セリフ全文）
- `prompts.md` - nanobanana用プロンプト

### 3. ステップごとに生成
```bash
python scripts/generate.py ep001 concept   # コンセプトだけ
python scripts/generate.py ep001 name      # ネームだけ
python scripts/generate.py ep001 script    # 台本だけ
python scripts/generate.py ep001 prompts   # プロンプトだけ
```

### 4. 新しいエピソードを作る
```bash
cp -r episodes/ep001 episodes/ep002
# episodes/ep002/input.md を書き換えて generate.py を実行
```

## ディレクトリ構成

```
├── characters/      キャラクターシート（.md）
├── episodes/
│   └── ep001/
│       ├── input.md     ← 実体験を書く（ここだけ手動）
│       ├── concept.md   ← 自動生成
│       ├── name.md      ← 自動生成
│       ├── script.md    ← 自動生成
│       └── prompts.md   ← 自動生成（nanobanana用）
├── world/           世界観設定
└── scripts/         生成スクリプト
```

## キャラクターを追加する

`characters/template.md` をコピーして記入：
```bash
cp characters/template.md characters/主人公.md
```
