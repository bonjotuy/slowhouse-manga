# 週刊スローハウス 制作システム

実体験 → 少年漫画エピソード → nanobananaプロンプト を自動生成するワークフロー。

## ページ仕様
- サイズ：縦長長方形 4:5（スマホ縦読み）
- 読み方向：右上→左下（日本漫画形式）
- 見開き：なし
- 画風：少年漫画（集英社・ジャンプ）、白黒

## セットアップ

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-api-key"
```

## 使い方

### キャラクターシートを作る
```bash
python scripts/generate.py character 主人公の名前
# → 名前・性格・外見・喋り方・nanobananaプロンプトを対話形式で入力
# → characters/名前.md に保存
```

### 場所シートを作る
```bash
python scripts/generate.py location スローハウス本店
# → 場所名・住所・雰囲気などを対話形式で入力
# → locations/場所名.md に保存
```

### エピソードを作る

**1. 実体験メモを書く**
```bash
python scripts/generate.py ep001
# → episodes/ep001/ を作成、input.md テンプレートを生成
# → input.md に実体験を書く
```

**2. 全自動生成**
```bash
python scripts/generate.py ep001
```

生成されるファイル：
| ファイル | 内容 |
|---------|------|
| `concept.md` | 少年漫画風コンセプト（伏線・名言・テーマ） |
| `name.md` | ネーム構成案（ページ数・コマ割り・演出） |
| `script.md` | 台本（セリフ全文・ト書き・効果音） |
| `prompts.md` | nanobanana用プロンプト（コマごと） |

**3. ステップだけ再生成**
```bash
python scripts/generate.py ep001 concept   # コンセプトのみ
python scripts/generate.py ep001 name      # ネームのみ
python scripts/generate.py ep001 script    # 台本のみ
python scripts/generate.py ep001 prompts   # プロンプトのみ
```

### 新しいエピソードを追加
```bash
python scripts/generate.py ep002   # ep002ディレクトリを作成
# input.md を書いて再実行
```

## ディレクトリ構成

```
├── characters/          キャラクターシート（.md）
│   └── template.md      テンプレート
├── locations/           場所シート（.md）
│   └── template.md      テンプレート
├── episodes/
│   └── ep001/
│       ├── input.md     ← 実体験を書く（ここだけ手動）
│       ├── concept.md   ← 自動生成
│       ├── name.md      ← 自動生成
│       ├── script.md    ← 自動生成
│       └── prompts.md   ← 自動生成（nanobanana用）
├── world/
│   └── slowhouse.md     世界観設定
└── scripts/
    └── generate.py      生成スクリプト
```

## 制作フロー

```
①実体験メモ（input.md）
      ↓
②コンセプト生成（concept.md）
  ※ 伏線設計・名言・テーマ・前話との連続性
      ↓
③ネーム構成案（name.md）
  ※ ページ数・コマ割り・右→左読み順・演出
      ↓
④台本（script.md）
  ※ セリフ全文・ト書き・効果音・吹き出し位置
      ↓
⑤nanobananaプロンプト（prompts.md）
  ※ コマごとの英語プロンプト・キャラ固定パーツ
      ↓
⑥nanobananaで作画
      ↓
⑦Instagram投稿
```
