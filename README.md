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

### 学術論文の翻訳

```bash
./run.sh data/research_paper.pdf -s english -t japanese -e openai -m gpt-4o
```

### 数学の教科書の翻訳

```bash
./run.sh data/math_textbook.pdf -s english -t chinese -e claude -m claude-3-opus-20240229
```

### 科学記事の翻訳

```bash
./run.sh data/scientific_article.pdf -s german -t english -e gemini -m gemini-1.5-pro
```

## 仕組み

1. スクリプトはPDFMathTranslateを実行してPDFを処理しコンテンツを抽出します
2. AIエンジンを使用する場合、抽出されたコンテンツは適切なAPIに送信されます
3. 数式やレイアウトを保持したまま翻訳が適用されます
4. 翻訳されたコンテンツは元のフォーマットを保持したままPDFにレンダリングされます

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