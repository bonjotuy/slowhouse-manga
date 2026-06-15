#!/usr/bin/env python3
"""
週刊スローハウス エピソード自動生成スクリプト

使い方:
  python scripts/generate.py ep001              # 全ステップ生成
  python scripts/generate.py ep001 concept      # コンセプトのみ
  python scripts/generate.py ep001 name         # ネーム構成案のみ
  python scripts/generate.py ep001 script       # 台本のみ
  python scripts/generate.py ep001 prompts      # nanobananaプロンプトのみ
  python scripts/generate.py character [名前]   # キャラクターシート作成
  python scripts/generate.py location [場所名]  # 場所シート作成
"""

import sys
import os
import anthropic
from pathlib import Path

MODEL = "claude-sonnet-4-6"

STEPS = ["concept", "name", "script", "prompts"]

# ページ仕様（日本漫画形式）
PAGE_SPEC = """
【ページ仕様】
- サイズ：縦長長方形 4:5（スマホ縦読み最適）
- 読み方向：右上→左下（日本漫画形式）
- 見開きページ：使用しない（1ページ単位）
- コマの流れ：右→左、上→下
- 画風：日本の少年漫画（集英社・ジャンプ）
- 白黒（スクリーントーン使用可）
"""


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def read_all_characters(base: Path) -> str:
    chars_dir = base / "characters"
    texts = []
    for f in sorted(chars_dir.glob("*.md")):
        if f.name != "template.md":
            texts.append(f"### {f.stem}\n" + f.read_text(encoding="utf-8"))
    return "\n\n".join(texts) if texts else "（キャラクターシートなし）"


def read_all_locations(base: Path) -> str:
    locs_dir = base / "locations"
    texts = []
    for f in sorted(locs_dir.glob("*.md")):
        if f.name != "template.md":
            texts.append(f"### {f.stem}\n" + f.read_text(encoding="utf-8"))
    return "\n\n".join(texts) if texts else "（場所シートなし）"


def read_world(base: Path) -> str:
    world_file = base / "world" / "slowhouse.md"
    return read_file(world_file) or "（世界観設定なし）"


def read_previous_episodes(base: Path, current_ep: str) -> str:
    eps_dir = base / "episodes"
    summaries = []
    for ep_dir in sorted(eps_dir.iterdir()):
        if ep_dir.is_dir() and ep_dir.name < current_ep:
            script = read_file(ep_dir / "script.md")
            concept = read_file(ep_dir / "concept.md")
            if script or concept:
                summaries.append(
                    f"### {ep_dir.name}\n"
                    + (concept[:500] + "...\n" if concept else "")
                    + (script[:300] + "...\n" if script else "")
                )
    return "\n\n".join(summaries) if summaries else "（前話なし・第1話）"


def generate_concept(client, ep_dir: Path, base: Path) -> str:
    input_text = read_file(ep_dir / "input.md")
    characters = read_all_characters(base)
    locations = read_all_locations(base)
    world = read_world(base)
    prev_eps = read_previous_episodes(base, ep_dir.name)

    prompt = f"""あなたは少年漫画（ジャンプ系）の敏腕編集者です。
以下の実体験エピソードを、週刊少年漫画風のエピソードコンセプトに変換してください。

## 世界観設定
{world}

## キャラクターシート
{characters}

## 場所シート
{locations}

## 前話までのあらすじ・絵柄
{prev_eps}

## 実体験元ネタ
{input_text}

{PAGE_SPEC}

## 出力形式（Markdownで）

# エピソードコンセプト

## タイトル案（3つ）
1.
2.
3.

## 採用タイトル
（上記3つから1つ選んで理由を）

## 一行あらすじ
（読者を引き込む一文。雑誌の目次に載るレベルで）

## このエピソードのテーマ
（少年漫画的に何を伝えるか）

## 実体験 → 漫画への昇華ポイント
（実体験のどの部分をどう少年漫画風に変えるか。具体的に）

## 伏線設計
- 今回張る伏線：
- 前話からの回収（あれば）：
- 次話への引き：

## 感情の山場（クライマックス）
（最も熱い瞬間の描写アイデア）

## このエピソードの「名言」（1〜2つ）
（ジャンプのキャラが言いそうな、心に刺さる台詞）

## 登場キャラクター
（今回登場するキャラと役割）

## 使用場所
（今回登場する場所）

## 読後感
（読み終わった後に読者がどう感じるか）
"""

    print("💭 コンセプト生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_name(client, ep_dir: Path, base: Path) -> str:
    concept = read_file(ep_dir / "concept.md")
    input_text = read_file(ep_dir / "input.md")
    characters = read_all_characters(base)
    locations = read_all_locations(base)
    prev_eps = read_previous_episodes(base, ep_dir.name)

    prompt = f"""あなたは少年漫画（ジャンプ）のネームを作るプロです。
以下のコンセプトをもとに、スマホ縦読み漫画のネーム構成案を作成してください。

## キャラクターシート
{characters}

## 場所シート
{locations}

## 前話の絵柄・構成（参考）
{prev_eps}

## 実体験元ネタ
{input_text}

## エピソードコンセプト
{concept}

{PAGE_SPEC}

## ネーム構成の条件
- 台本の長さに応じてページ数を決める（目安：8〜16ページ）
- 各ページは4:5縦長（スマホ1画面で完結するイメージ）
- コマ割りは右上→左下（日本漫画の読み順）
- 各ページのコマ数：1〜4コマ（演出に応じて）
- 1話完結だが、続きを読みたくなる引きで終わる
- ジャンプ風の大ゴマ・集中線・効果音を積極的に使う

## 【重要】AI作画のためのキャラ混同防止ルール
AI画像生成ツールで作画するため、以下のルールを必ず守ること：

1. **1コマのメインキャラは原則1〜2人まで**
   - 3人以上が同じコマに登場する場合は「引き構図（全体シルエット）」か「後ろ姿」にする
   - 顔のアップや表情を見せたい場合は必ず1人ずつ別コマに分ける

2. **複数人シーンの分割パターン（必ず使うこと）**
   - 会話シーン：「Aのアップ→Bのアップ→2人の引き」の3コマ構成
   - 集合シーン：「引きで全員のシルエット」→「メインキャラのアップ」
   - 見送り・別れ：「後ろ姿・引き構図」で顔を描かない

3. **各コマに「メインキャラ」タグを必ず付ける**
   - 「メインキャラ：ぼんちゃんのみ」「メインキャラ：ぼんちゃん（左）とゆま（右）」など

4. **キャラ識別のための視覚的差別化を明記する**
   - 各コマで「ぼんちゃん＝黒アームカバー」など見分けポイントを書く

## 出力形式（Markdownで）

# ネーム構成案

## 全体構成
- 総ページ数：
- 起（P1〜P?）：
- 承（P?〜P?）：
- 転（P?〜P?）：
- 結（P?〜P?）：

---

## P1（扉ページ）
**レイアウト**：（例：1コマ大ゴマ）
**コマ1**
- **メインキャラ**：（例：ぼんちゃんのみ／背景人物はシルエット）
- 場面・構図：（右上→左下読み順を意識した説明）
- カメラ：（例：バストアップ・正面／引き・斜め45度）
- 顔の描写：あり（アップ）／なし（後ろ姿・シルエット）
- キャラ識別ポイント：（例：ぼんちゃん＝黒アームカバー）
- セリフ/ナレーション：「　」
- 演出（効果線・トーン等）：

---

（P2〜最終ページまで同じ形式で出力）

---

## ページ演出メモ
- クライマックスページ（P?）：（なぜここが山場か）
- 効果音一覧：
- 最終ページの引き方：
- キャラ混同リスクが高いコマ：（特に注意が必要なコマを列挙）
"""

    print("📋 ネーム構成案生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_script(client, ep_dir: Path, base: Path) -> str:
    name = read_file(ep_dir / "name.md")
    concept = read_file(ep_dir / "concept.md")
    characters = read_all_characters(base)

    prompt = f"""あなたは少年漫画の台本作家です。
ネーム構成案をもとに、完全な台本（セリフ・ナレーション・ト書き全文）を作成してください。

## キャラクターシート（喋り方・口癖を守ること）
{characters}

## エピソードコンセプト
{concept}

## ネーム構成案
{name}

{PAGE_SPEC}

## 台本の条件
- セリフはキャラクターシートの喋り方に忠実に
- ナレーション（モノローグ）は読者の心に刺さる文体
- 感情の流れが伝わるト書き（表情・動作・心理）
- 効果音（擬音語）も具体的に
- 「名言」になりうるセリフを意識する
- 読み方向（右上→左下）を意識したセリフ配置の指示も入れる

## 出力形式（Markdownで）

# 台本

## P1
**[ト書き]** （場面・雰囲気）

**コマ1**（右上）
- [ナレーション]「　」
- [キャラ名]「　」
- [ト書き] （表情・動作）
- [効果音]：

**コマ2**（左上）
...

---

（全ページ・全コマを同じ形式で）

---

## セリフ一覧（nanobanana吹き出し入力用）
| ページ | コマ | キャラ | セリフ |
|--------|------|--------|--------|
| P1 | コマ1 | | |
...
"""

    print("✍️  台本生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_prompts(client, ep_dir: Path, base: Path) -> str:
    name = read_file(ep_dir / "name.md")
    script = read_file(ep_dir / "script.md")
    characters = read_all_characters(base)
    locations = read_all_locations(base)

    prompt = f"""あなたはAI漫画生成ツール「nanobanana」のプロンプトエンジニアです。
以下の情報をもとに、各ページ・各コマのnanobananaプロンプトを作成してください。

## キャラクター固定プロンプト
{characters}

## 場所固定プロンプト
{locations}

## ネーム構成案
{name}

## 台本
{script}

{PAGE_SPEC}

## nanobananaプロンプトの条件
- 画風：日本の少年漫画（ジャンプ系）、白黒、スクリーントーン
- 読み方向：右上→左下
- ページ比率：4:5縦長
- キャラクター外見はシートの固定プロンプトを必ず使い回す

## 【最重要】キャラ混同を防ぐプロンプトルール

**ルール1：メインキャラを1〜2人に絞って明示する**
- 「1 character only:」または「2 characters:（左）〇〇（右）〇〇」を必ず冒頭に書く
- 背景の人物はシルエット扱い：「other characters as silhouettes in background」

**ルール2：キャラクターごとの識別プロンプトを毎回フルで書く**
- キャラシートの固定プロンプトを省略せずそのままコピーする
- 「See character sheet」などの省略は絶対にしない

**ルール3：複数人コマの指示パターン**
- 引き構図：「wide shot, multiple characters as small figures, no face detail」
- 後ろ姿：「from behind, back view, no face visible」
- 2人会話：「2 characters, [キャラA] on right side, [キャラB] on left side, both clearly separated」

**ルール4：ネガティブプロンプトに「キャラ混同防止」を追加**
- 「wrong character design, mixed up characters, inconsistent appearance」を必ず入れる

## 出力形式（Markdownで）

# nanobanana プロンプト集

## ページ共通設定
```
japanese shonen manga style, black and white, screentone, jump magazine style, 4:5 portrait ratio, right-to-left reading order, detailed linework
```

---

## P1（扉ページ）

### コマ1
**シーン（日本語）**：何を描くか
**メインキャラ**：（例：ぼんちゃんのみ）
**キャラ混同リスク**：低／中／高（高の場合は対策も記載）

**プロンプト**：
```
1 character only: [キャラ固定プロンプトをフルで], [表情プロンプト], [カメラアングル], [背景], [演出効果], manga panel composition, japanese shonen manga, black and white
```

**ネガティブプロンプト**：
```
color, realistic, western comic, low quality, bad anatomy, wrong character design, mixed up characters, inconsistent appearance, multiple main characters
```

**吹き出し**：位置（右上/左上/右下/左下）／セリフ「　」

---

（全ページ・全コマ同じ形式で出力）

---

## キャラクター別 固定プロンプト（コピペ用）
（毎回ここからコピーして使う）

## 場所別 背景プロンプト（コピペ用）

## このエピソードのキャラ混同注意コマ一覧
（複数人が登場するコマと、その対策をまとめる）
"""

    print("🎨 nanobananaプロンプト生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_character_sheet(client, name: str, info: str, base: Path) -> str:
    template = read_file(base / "characters" / "template.md")

    prompt = f"""あなたは少年漫画のキャラクターデザイナーです。
以下の情報をもとに、漫画制作用のキャラクターシートを作成してください。

## テンプレート
{template}

## 入力情報
キャラクター名：{name}
{info}

## 出力条件
- テンプレートの全項目を埋める
- 「喋り方」は実際のセリフ例を3つ以上含める
- nanobanana固定プロンプトは英語で具体的に
- 少年漫画（ジャンプ）的な魅力ポイントを意識する
- 不明な情報は「未設定（要確認）」と記載し、後から追加できるようにする
"""

    print(f"👤 {name}のキャラクターシート生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_location_sheet(client, name: str, info: str, base: Path) -> str:
    template = read_file(base / "locations" / "template.md")

    prompt = f"""あなたは漫画の背景デザイナーです。
以下の情報をもとに、漫画制作用の場所シートを作成してください。

## テンプレート
{template}

## 入力情報
場所名：{name}
{info}

## 出力条件
- テンプレートの全項目を埋める
- 間取り図はテキストアート（ASCII）で表現する
- nanobanana固定プロンプトは英語で具体的に
- 漫画的に映える「見せ場アングル」を3つ以上提案する
- 不明な情報は「未設定（要確認）」と記載
"""

    print(f"🏠 {name}の場所シート生成中...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 環境変数が設定されていません")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    base = Path(__file__).parent.parent

    # キャラクターシート生成モード
    if args[0] == "character":
        char_name = args[1] if len(args) > 1 else input("キャラクター名: ")
        print("キャラクター情報を入力してください（空行2つで終了）:")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
            lines.append(line)
        info = "\n".join(lines)
        result = generate_character_sheet(client, char_name, info, base)
        output_path = base / "characters" / f"{char_name}.md"
        output_path.write_text(result, encoding="utf-8")
        print(f"✅ {output_path} を生成しました")
        return

    # 場所シート生成モード
    if args[0] == "location":
        loc_name = args[1] if len(args) > 1 else input("場所名: ")
        print("場所情報を入力してください（空行2つで終了）:")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
            lines.append(line)
        info = "\n".join(lines)
        result = generate_location_sheet(client, loc_name, info, base)
        output_path = base / "locations" / f"{loc_name}.md"
        output_path.write_text(result, encoding="utf-8")
        print(f"✅ {output_path} を生成しました")
        return

    # エピソード生成モード
    ep_name = args[0]
    target_step = args[1] if len(args) > 1 else "all"

    ep_dir = base / "episodes" / ep_name

    if not ep_dir.exists():
        ep_dir.mkdir(parents=True)
        template = f"""# エピソード {ep_name} 元ネタ（実体験）

## 実体験メモ
（ここに実際にあった話を書く）

## 登場人物（実際）
-

## 何があった？
1.
2.
3.

## 印象に残った言葉・場面
-

## 自分がどう感じたか
-

## テーマ（一言）
-
"""
        (ep_dir / "input.md").write_text(template, encoding="utf-8")
        print(f"📁 {ep_dir} を作成しました。input.md を書いてから再実行してください。")
        return

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
        result = gen_func(client, ep_dir, base)
        output_path = ep_dir / output_file
        output_path.write_text(result, encoding="utf-8")
        print(f"✅ {output_file} を生成しました")

    print(f"\n🎉 完了！ {ep_dir} を確認してください")


if __name__ == "__main__":
    main()
