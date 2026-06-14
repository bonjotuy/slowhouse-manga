#!/usr/bin/env python3
"""
週刊スローハウス エピソード自動生成スクリプト

使い方:
  python scripts/generate.py ep001          # 全ステップ生成
  python scripts/generate.py ep001 concept  # conceptだけ生成
  python scripts/generate.py ep001 name     # nameだけ生成
  python scripts/generate.py ep001 script   # scriptだけ生成
  python scripts/generate.py ep001 prompts  # promptsだけ生成
"""

import sys
import os
import anthropic
from pathlib import Path

MODEL = "claude-sonnet-4-6"

STEPS = ["concept", "name", "script", "prompts"]


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def read_characters(base: Path) -> str:
    chars_dir = base / "characters"
    texts = []
    for f in sorted(chars_dir.glob("*.md")):
        if f.name != "template.md":
            texts.append(f"### {f.stem}\n" + f.read_text(encoding="utf-8"))
    return "\n\n".join(texts) if texts else "（キャラクターシートなし）"


def read_world(base: Path) -> str:
    world_file = base / "world" / "slowhouse.md"
    return read_file(world_file) or "（世界観設定なし）"


def generate_concept(client, ep_dir: Path, base: Path) -> str:
    input_text = read_file(ep_dir / "input.md")
    characters = read_characters(base)
    world = read_world(base)

    prompt = f"""あなたは少年漫画の敏腕編集者です。
以下の実体験エピソードを、週刊少年漫画風のエピソードコンセプトに変換してください。

## 世界観設定
{world}

## キャラクターシート
{characters}

## 実体験元ネタ
{input_text}

## 出力形式（Markdownで）

# エピソードコンセプト

## タイトル案（3つ）
1.
2.
3.

## 一行あらすじ
（読者を引き込む一文）

## 少年漫画的テーマ
（このエピソードが伝えること）

## 熱い展開ポイント
（実体験のどの部分をどう少年漫画風に昇華させるか）

## 伏線
- 今回張る伏線：
- 前エピソードからの回収（あれば）：
- 次エピソードへの引き：

## 感情の山場（クライマックス）
（最も熱い瞬間・セリフのアイデア）

## 名言候補（このエピソードの「熱い台詞」）
1.
2.

## 読者への問いかけ
（このエピソードを読んだ後、読者に考えてほしいこと）
"""

    print("💭 コンセプト生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_name(client, ep_dir: Path, base: Path) -> str:
    concept = read_file(ep_dir / "concept.md")
    input_text = read_file(ep_dir / "input.md")
    characters = read_characters(base)

    prompt = f"""あなたは少年漫画のネームを作るプロです。
以下のコンセプトと元ネタをもとに、Instagram縦読み漫画（8〜12ページ）のネーム構成案を作ってください。

## キャラクターシート
{characters}

## 実体験元ネタ
{input_text}

## エピソードコンセプト
{concept}

## ネーム構成案の条件
- Instagram縦読み形式：1ページ = 正方形 or 縦長1枚
- 全8〜12ページ
- 各ページのコマ数：1〜4コマ
- 1話完結だが、続きを読みたくなる引きで終わる

## 出力形式（Markdownで）

# ネーム構成案

## 全体構成
- ページ数：
- 起承転結：起（P1-P?）承（P?-P?）転（P?-P?）結（P?-P?）

---

## P1（表紙/扉ページ）
**コマ数**：1
**コマ1**：
- 場面：
- キャラクター：
- セリフ/ナレーション：
- 絵の指示：（カメラアングル、表情、雰囲気）
- ページの印象：

---

（P2〜最終ページまで同じ形式で）

## クライマックスページ（最重要ページ）
**演出メモ**：（なぜここが山場なのか）

## 最終ページ（引き）
**次回への引き方**：
"""

    print("📋 ネーム構成案生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_script(client, ep_dir: Path, base: Path) -> str:
    name = read_file(ep_dir / "name.md")
    concept = read_file(ep_dir / "concept.md")
    characters = read_characters(base)

    prompt = f"""あなたは漫画の台本作家です。
以下のネーム構成案をもとに、完全な台本（セリフ・ナレーション全文）を書いてください。

## キャラクターシート
{characters}

## エピソードコンセプト
{concept}

## ネーム構成案
{name}

## 台本の条件
- セリフは自然な日本語（でも少年漫画らしい熱さも）
- ナレーション（モノローグ）は読者の心に刺さる文体
- 感情の流れが伝わるト書きを入れる
- 「名言」になりうるセリフを意識する

## 出力形式（Markdownで）

# 台本

## P1
**[ト書き]** （場面・雰囲気の説明）

**コマ1**
- [キャラ名]「セリフ」
- [ナレーション]「ナレーション文」
- [ト書き] （表情・動作の指示）

---

（各ページ・各コマを同じ形式で）

## 全セリフ一覧（nanobanana入力用）
（全ページのセリフをシンプルにリスト）
"""

    print("✍️  台本生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_prompts(client, ep_dir: Path, base: Path) -> str:
    name = read_file(ep_dir / "name.md")
    script = read_file(ep_dir / "script.md")
    characters = read_characters(base)

    prompt = f"""あなたはAI画像生成のプロンプトエンジニアです。
漫画制作AIツール「nanobanana」用の画像生成プロンプトを各コマ分作成してください。

## キャラクターシート（外見情報）
{characters}

## ネーム構成案
{name}

## 台本
{script}

## nanobananaプロンプトの条件
- 漫画スタイル（manga style, black and white）
- 各コマごとに1プロンプト
- キャラクターの一貫性を保つための外見描写を必ず含める
- カメラアングル・構図を明示する
- 感情・雰囲気を英語で表現

## 出力形式（Markdownで）

# nanobanana プロンプト集

## P1 コマ1
**シーン説明**：（日本語で何を描くか）
**プロンプト（英語）**：
```
manga style, black and white, [キャラ外見], [アングル], [シーン], [感情/雰囲気], detailed linework, screentone
```
**ネガティブプロンプト**：
```
color, realistic, western comic, low quality
```

---

（全コマ分同じ形式で）

## 共通キャラクタープロンプト（各コマに使い回す）
（キャラクターごとの外見を固定するプロンプトパーツ）
"""

    print("🎨 nanobananaプロンプト生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def main():
    args = sys.argv[1:]
    if not args:
        print("使い方: python scripts/generate.py ep001 [step]")
        print("  step: concept / name / script / prompts （省略で全ステップ）")
        sys.exit(1)

    ep_name = args[0]
    target_step = args[1] if len(args) > 1 else "all"

    base = Path(__file__).parent.parent
    ep_dir = base / "episodes" / ep_name

    if not ep_dir.exists():
        print(f"❌ エピソードディレクトリが見つかりません: {ep_dir}")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 環境変数が設定されていません")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    steps_to_run = STEPS if target_step == "all" else [target_step]

    generators = {
        "concept": (generate_concept, "concept.md"),
        "name": (generate_name, "name.md"),
        "script": (generate_script, "script.md"),
        "prompts": (generate_prompts, "prompts.md"),
    }

    for step in steps_to_run:
        if step not in generators:
            print(f"❌ 不明なステップ: {step}")
            continue

        gen_func, output_file = generators[step]
        output_path = ep_dir / output_file

        result = gen_func(client, ep_dir, base)
        output_path.write_text(result, encoding="utf-8")
        print(f"✅ {output_file} を生成しました")

    print(f"\n🎉 完了！ {ep_dir} を確認してください")


if __name__ == "__main__":
    main()
