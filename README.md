# AIモデルを活用したPDFMathTranslate

このプロジェクトは、PDFMathTranslateと様々なAIモデル（OpenAI/ChatGPT、Google/Gemini、Anthropic/Claude）を組み合わせて、数式、図表、レイアウトを保持したままPDF文書を翻訳します。

## 特徴

- 複数のAIエンジンを使用したPDF翻訳：
  - **OpenAI/ChatGPT**（GPT-4、GPT-3.5など）
  - **Google/Gemini**（Gemini Pro、Gemini Ultraなど）
  - **Anthropic/Claude**（Claude 3 Opusなど）
  - **デフォルトのPDFMathTranslateエンジン**（APIキーが提供されていない場合）
- Dockerベースのワークフロー（ローカル環境を汚さない）
- 数式、図表、文書レイアウトを保持
- 使いやすいコマンドラインインターフェース
- 複数言語間の翻訳をサポート
- **大量のページを持つPDFを自動分割処理**（ページごとの分割、処理、結合が可能）
- **チャンク分割されたPDFファイルの結合ツール**（別々に処理されたファイルの後処理に便利）

## 前提条件

- システムにDockerがインストールされていること
- 使用したいAIサービスのAPIキー：
  - ChatGPT用のOpenAI APIキー
  - Gemini用のGoogle APIキー
  - Claude用のAnthropic APIキー

## セットアップ

1. このリポジトリをクローンまたはダウンロード
2. PDFファイルを`data`ディレクトリに配置
3. `.env`ファイルを編集してAPIキーを追加：

```
# 必要に応じてAPIキーのコメントを解除して追加
OPENAI_API_KEY=あなたのOpenAI-APIキー
GOOGLE_API_KEY=あなたのGoogle-APIキー
ANTHROPIC_API_KEY=あなたのAnthropic-APIキー
```

4. 実行スクリプトに実行権限を付与：

```bash
chmod +x run.sh
```

5. Dockerイメージをビルド：

```bash
./run.sh --build
```

## 使い方

### 基本的な翻訳

デフォルト設定でPDFを翻訳する（PDFMathTranslateのデフォルトエンジンを使用して英語から日本語へ）：

```bash
./run.sh data/input.pdf
```

翻訳されたPDFは`data`ディレクトリに`input_japanese.pdf`のような名前で保存されます。

### 高度な翻訳オプション

異なる翻訳エンジンやパラメータを指定できます：

```bash
# OpenAI/ChatGPTを使用して英語から中国語へ翻訳
./run.sh data/input.pdf --source-lang english --target-lang chinese --engine openai

# 特定のモデルを指定してGoogleのGemini APIを使用
./run.sh data/input.pdf -s english -t japanese -e gemini -m gemini-1.5-pro

# Claudeを使用して翻訳
./run.sh data/input.pdf -s english -t french -e claude
```

### コマンドラインオプション

```
使用法: ./run.sh [オプション] [入力ファイル] [翻訳オプション]

ビルドオプション:
  -h, --help             ヘルプメッセージを表示
  -b, --build            Dockerイメージをビルド/再ビルド
  -i, --input DIR        入力ディレクトリを設定（デフォルト: ./data）
  -o, --output DIR       出力ディレクトリを設定（デフォルト: ./data）

翻訳オプション:
  input_file             翻訳するPDFファイルへのパス
  --output, -o           翻訳されたPDFを保存するパス
  --source-lang, -s      ソース言語（デフォルト: english）
  --target-lang, -t      ターゲット言語（デフォルト: japanese）
  --engine, -e           翻訳エンジン: openai, gemini, claude, またはdefault
  --model, -m            選択したエンジンの特定のモデル
  --pages-per-chunk, -p  大きなPDFを分割する際のページ数（デフォルト: 20）
  --large, -l            PDFサイズに関わらず分割処理を強制実行
```

## サポートされている言語

- 英語（`english`または`en`）
- 日本語（`japanese`または`ja`）
- 中国語（`chinese`または`zh`）
- 韓国語（`korean`または`ko`）
- フランス語（`french`または`fr`）
- ドイツ語（`german`または`de`）
- スペイン語（`spanish`または`es`）
- イタリア語（`italian`または`it`）
- ポルトガル語（`portuguese`または`pt`）
- ロシア語（`russian`または`ru`）

言語コードを直接使用することもできます（例：`en`、`ja`、`zh`）。

## 使用例

### 大きなPDFの翻訳（自動分割処理）

大きなPDFファイル（30ページ以上または10MB以上）は自動的に分割して処理され、結合されます：

```bash
# 大きなPDFファイルを翻訳（自動的に分割処理されます）
./run.sh data/large_document.pdf -s english -t japanese -e gemini -m gemini-2.0-flash
```

### 分割処理の制御

PDFの分割処理を制御するオプションを指定できます：

```bash
# サイズに関わらず分割処理を強制実行
./run.sh data/document.pdf -l

# 30ページごとに分割（デフォルトは20ページ）
./run.sh data/large_document.pdf -p 30 -l

# OpenAIを使用して50ページごとに分割
./run.sh data/large_document.pdf -e openai -m gpt-4o -p 50
```

**注意**: カスタムエンジン（OpenAI、Gemini、Claude）を使用する場合、サイズに関係なく自動的に分割処理が適用されます。

### 学術論文の翻訳

**using chatGPT**
```bash
./run.sh data/research_paper.pdf -s english -t japanese -e openai -m gpt-4o
```

**using gemini**
- モデル一覧: https://ai.google.dev/gemini-api/docs/models?hl=ja

```bash
./run.sh data/research_paper.pdf -s english -t japanese -e gemini -m gemini-2.5-pro-exp-03-25
```

### 数学の教科書の翻訳

```bash
./run.sh data/math_textbook.pdf -s english -t chinese -e claude -m claude-3-opus-20240229
```

### 科学記事の翻訳

```bash
./run.sh data/scientific_article.pdf -s german -t english -e gemini -m gemini-1.5-pro
```

### PDF結合ツールの使用

翻訳処理後に生成されたチャンクPDFを手動で結合するには、`merge_pdfs.sh`スクリプトを使用できます：

```bash
# 日本語翻訳ディレクトリのすべてのチャンク翻訳を結合
./merge_pdfs.sh

# 特定のプロジェクトのみ結合
./merge_pdfs.sh -p hernanrobins_WhatIf_2jan25

# 翻訳PDFのみ結合（バイリンガルPDFは除外）
./merge_pdfs.sh -t translated

# バイリンガルPDFのみ結合
./merge_pdfs.sh -t bilingual

# 元のチャンクファイルを保持（デフォルトでは結合成功後に削除）
./merge_pdfs.sh -k
```

結合されたPDFファイルは、入力ディレクトリに`[プロジェクト名]_[タイプ]_merged.pdf`の形式で保存されます。

### PDF結合ツールのコマンドラインオプション

```
使用法: ./merge_pdfs.sh [オプション] [ディレクトリ]

オプション:
  -h, --help                ヘルプメッセージを表示
  -o, --output-dir DIR      結合されたPDFの出力先ディレクトリを指定
  -k, --keep-originals      元のPDFファイルを削除せずに保持
  -p, --project NAME        特定のプロジェクトのみを処理
  -t, --type TYPE           処理するファイルタイプ (translated/bilingual/both)
```

## 仕組み

1. スクリプトはPDFMathTranslateを実行してPDFを処理しコンテンツを抽出します
2. AIエンジンを使用する場合、抽出されたコンテンツは適切なAPIに送信されます
3. 数式やレイアウトを保持したまま翻訳が適用されます
4. 翻訳されたコンテンツは元のフォーマットを保持したままPDFにレンダリングされます

### 大きなPDFファイルの処理の仕組み

大きなPDFファイルの処理は以下の手順で行われます：

1. **分析**: PDFのページ数とファイルサイズを分析し、分割が必要かどうかを判断します
2. **分割**: 指定したページ数（デフォルト20ページ）ごとにPDFを小さなチャンクに分割します
3. **段階的処理**: 各チャンクを個別に翻訳し、それぞれの翻訳結果を保存します
4. **結合**: すべてのチャンクの処理が完了したら、翻訳されたPDFファイルを1つのファイルに結合します

この方法では、大きなPDFファイルでもメモリを効率的に使用でき、翻訳プロセスがより安定します。また、各チャンクの翻訳結果は個別に保存されるため、途中でエラーが発生しても、再開が容易になります。

### PDF結合ツールの仕組み

PDF結合ツール（`merge_pdfs.sh`）は以下の手順で動作します：

1. **ファイル検出**: 指定されたディレクトリ内のチャンクファイルを自動的に検出し、プロジェクトとファイルタイプ（翻訳/バイリンガル）ごとにグループ化します
2. **ファイルソート**: 各グループ内のファイルをチャンク番号順に正しくソートします
3. **結合処理**: PyPDF2を使用して各グループのPDFファイルを1つのファイルに結合します
4. **後処理**: 結合が成功した場合、元のチャンクファイルを削除します（-kオプションで保持可能）

このツールは、大きなPDFの翻訳が複数のチャンクに分かれて処理された後、それらを簡単に結合するために役立ちます。また、処理が失敗したチャンクを個別に再処理した後で全体を結合する際にも便利です。

## トラブルシューティング

### APIキーの問題

APIキーに関連するエラーが発生した場合：

1. `.env`ファイル内の関連する行のコメントが解除されているか確認してください
2. APIキーが正しいことを確認してください
3. APIキーに十分なクォータ/クレジットがあるか確認してください

### PDF処理の問題

PDF処理に問題が発生した場合：

1. PDFが破損していないことを確認してください
2. 別のエンジンを試してみてください（一部のエンジンは特定の文書に対してより効果的に機能する場合があります）
3. 複雑な文書の場合、カスタムAIエンジンよりもデフォルトのPDFMathTranslateエンジンの方がうまく機能する場合があります

## クレジット

このプロジェクトは以下の技術を組み合わせています：

- [PDFMathTranslate](https://github.com/ptyin/PDFMathTranslate)：PDF処理と翻訳
- OpenAIのAPI（ChatGPT）
- GoogleのGenerative AI API（Gemini）
- AnthropicのAPI（Claude）

## ライセンス

このプロジェクトはPDFMathTranslateと同じライセンスで配布されています。