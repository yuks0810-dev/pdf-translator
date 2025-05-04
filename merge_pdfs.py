#!/usr/bin/env python3
"""
PDF結合ツール - チャンク分割されたPDFファイルを結合するためのユーティリティ
"""

import os
import argparse
import glob
import re
import shutil
from typing import List, Dict, Tuple

try:
    from PyPDF2 import PdfMerger
    merger_available = True
except ImportError:
    try:
        from PyPDF2 import PdfFileMerger as PdfMerger
        merger_available = True
    except ImportError:
        merger_available = False
        print("警告: PyPDF2がインストールされていません。pip install PyPDF2 でインストールしてください。")


def find_chunk_files(directory: str, pattern: str = "*_japanese_*.pdf") -> Dict[str, List[str]]:
    """
    指定されたディレクトリ内のチャンクファイルを探し、種類ごとにグループ化します
    """
    chunk_dirs = {}
    
    # chunk_NNNディレクトリを探す
    chunk_pattern = re.compile(r'chunk_\d+$')
    
    # 全てのサブディレクトリを走査
    for root, dirs, files in os.walk(directory):
        # チャンクディレクトリのみを処理
        if chunk_pattern.search(os.path.basename(root)):
            # 各チャンクディレクトリ内のファイルをチェック
            for file in files:
                if file.endswith('.pdf'):
                    # ファイルタイプを判断（translated or bilingual）
                    file_type = 'translated' if 'translated.pdf' in file else 'bilingual'
                    
                    # 親ディレクトリを取得（プロジェクト名を特定）
                    parent_dir = os.path.basename(os.path.dirname(root))
                    
                    # キーを作成 (親ディレクトリ + ファイルタイプ)
                    key = f"{parent_dir}_{file_type}"
                    
                    if key not in chunk_dirs:
                        chunk_dirs[key] = []
                    
                    chunk_dirs[key].append(os.path.join(root, file))
    
    # 各グループ内のファイルをチャンク番号順にソート
    for key in chunk_dirs:
        chunk_dirs[key].sort(key=lambda x: int(re.search(r'chunk_(\d+)', x).group(1)))
    
    return chunk_dirs


def merge_pdf_files(files: List[str], output_file: str, delete_originals: bool = False) -> bool:
    """
    PDFファイルのリストを1つのPDFファイルに結合します
    成功した場合は元のファイルを削除します（オプション）
    """
    if not merger_available:
        print("エラー: PyPDF2がインストールされていません。")
        return False
    
    if not files:
        print("エラー: 結合するファイルがありません。")
        return False
    
    try:
        print(f"PDFファイルを結合しています...")
        print(f"結合するファイル: {len(files)}個")
        
        merger = PdfMerger()
        
        for pdf_file in files:
            print(f"追加: {pdf_file}")
            merger.append(pdf_file)
        
        # 出力ディレクトリが存在することを確認
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # PDFを結合して保存
        merger.write(output_file)
        merger.close()
        
        print(f"PDFファイルを正常に結合しました: {output_file}")
        
        # 元のファイルを削除（オプション）
        if delete_originals:
            print("元のファイルを削除しています...")
            for pdf_file in files:
                os.remove(pdf_file)
                print(f"削除: {pdf_file}")
        
        return True
        
    except Exception as e:
        print(f"PDFの結合中にエラーが発生しました: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="チャンク分割されたPDFファイルを結合するユーティリティ")
    
    parser.add_argument("directory", help="PDFチャンクファイルを含むディレクトリ")
    parser.add_argument("--output-dir", "-o", help="結合されたPDFの出力先ディレクトリ", default=None)
    parser.add_argument("--keep-originals", "-k", action="store_true", help="元のファイルを保持する（デフォルトでは削除）")
    parser.add_argument("--project", "-p", help="特定のプロジェクトのみを処理", default=None)
    parser.add_argument("--type", "-t", choices=["translated", "bilingual", "both"], 
                       default="both", help="処理するファイルタイプ（translated/bilingual/both）")
    
    args = parser.parse_args()
    
    # ディレクトリが存在するか確認
    if not os.path.exists(args.directory) or not os.path.isdir(args.directory):
        print(f"エラー: ディレクトリ '{args.directory}' が見つかりません")
        return 1
    
    # 出力ディレクトリの設定
    output_dir = args.output_dir if args.output_dir else args.directory
    
    # チャンクファイルを検索
    chunk_groups = find_chunk_files(args.directory)
    
    if not chunk_groups:
        print(f"結合するPDFチャンクファイルが見つかりません。ディレクトリ: {args.directory}")
        return 1
    
    success_count = 0
    processed_count = 0
    
    # 各グループの処理
    for key, files in chunk_groups.items():
        # キーをプロジェクト名とファイルタイプに分割
        project, file_type = key.rsplit('_', 1)
        
        # プロジェクトフィルタリング
        if args.project and args.project != project:
            continue
            
        # ファイルタイプフィルタリング
        if args.type != "both" and args.type != file_type:
            continue
        
        processed_count += 1
        
        # 出力ファイル名の構築
        output_file = os.path.join(output_dir, f"{project}_{file_type}_merged.pdf")
        
        # PDF結合の実行
        if merge_pdf_files(files, output_file, not args.keep_originals):
            success_count += 1
    
    # 結果の表示
    if processed_count == 0:
        print("処理対象のファイルグループが見つかりませんでした。フィルタを確認してください。")
        return 1
        
    print(f"処理完了: {success_count}/{processed_count} グループのPDFを結合しました。")
    return 0 if success_count == processed_count else 1


if __name__ == "__main__":
    main()