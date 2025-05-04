#!/bin/bash
# merge_pdfs.sh - チャンク分割されたPDFファイルを結合するシェルスクリプト

# 実行権限を付与
chmod +x merge_pdfs.py

# ヘルプメッセージを表示する関数
show_help() {
  echo "使用法: $0 [オプション] [ディレクトリ]"
  echo ""
  echo "オプション:"
  echo "  -h, --help                このヘルプメッセージを表示"
  echo "  -o, --output-dir DIR      結合されたPDFの出力先ディレクトリを指定"
  echo "  -k, --keep-originals      元のPDFファイルを削除せずに保持"
  echo "  -p, --project NAME        特定のプロジェクトのみを処理"
  echo "  -t, --type TYPE           処理するファイルタイプ (translated/bilingual/both)"
  echo ""
  echo "例:"
  echo "  $0 data/translations/japanese                   # 日本語翻訳ディレクトリの全てのチャンクを結合"
  echo "  $0 -p hernanrobins_WhatIf_2jan25 data/translations/japanese  # 特定のプロジェクトのみ処理"
  echo "  $0 -t translated data/translations/japanese     # 翻訳済みPDFのみ結合"
  echo "  $0 -k data/translations/japanese                # 元ファイルを保持"
  echo ""
}

# デフォルト値
DIRECTORY="data/translations/japanese"
DOCKER_ARGS=""

# 引数の解析
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      show_help
      exit 0
      ;;
    -o|--output-dir)
      DOCKER_ARGS="$DOCKER_ARGS --output-dir $2"
      shift 2
      ;;
    -k|--keep-originals)
      DOCKER_ARGS="$DOCKER_ARGS --keep-originals"
      shift
      ;;
    -p|--project)
      DOCKER_ARGS="$DOCKER_ARGS --project $2"
      shift 2
      ;;
    -t|--type)
      DOCKER_ARGS="$DOCKER_ARGS --type $2"
      shift 2
      ;;
    *)
      DIRECTORY="$1"
      shift
      ;;
  esac
done

# Dockerコンテナ内で実行
echo "Dockerコンテナ内でPDF結合を実行します..."

# DIRECTORYがdata/で始まるか確認し、そうでない場合は追加
if [[ ! "$DIRECTORY" =~ ^data/ ]]; then
  # DIRECTORYが/で始まらない場合はdata/を追加
  DIRECTORY="data/$DIRECTORY"
fi

# PDFMathTranslateコンテナを使用して実行
docker run --rm -it \
  --name pdf-translator-container \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/merge_pdfs.py:/app/merge_pdfs.py" \
  pdf-translator \
  python /app/merge_pdfs.py /app/data/${DIRECTORY#data/} $DOCKER_ARGS