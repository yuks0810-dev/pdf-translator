#!/usr/bin/env python3
"""
PDF Translator using PDFMathTranslate with multiple AI providers
(OpenAI/ChatGPT, Google/Gemini, Anthropic/Claude)
"""

import os
import argparse
import time
import subprocess
import json
import tempfile
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Import API libraries conditionally to avoid errors if API keys are missing
openai_available = False
gemini_available = False
claude_available = False

if OPENAI_API_KEY:
    import openai
    openai.api_key = OPENAI_API_KEY
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    openai_available = True

if GOOGLE_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_available = True

if ANTHROPIC_API_KEY:
    import anthropic
    claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    claude_available = True

# 結合用にPyPDF2のPdfFileMergerを使用
try:
    from PyPDF2 import PdfMerger
    merger_available = True
except ImportError:
    try:
        from PyPDF2 import PdfFileMerger as PdfMerger
        merger_available = True
    except ImportError:
        merger_available = False
        print("Warning: PyPDF2 not available. PDF merging will not work.")

# Language code mappings
LANGUAGE_CODES = {
    "english": "en",
    "japanese": "ja",
    "chinese": "zh",
    "korean": "ko",
    "french": "fr",
    "german": "de",
    "spanish": "es",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    # Add more languages as needed
}

def translate_with_openai(text: str, source_lang: str, target_lang: str, model: str = "gpt-4o") -> str:
    """Translate text using OpenAI API"""
    if not openai_available:
        raise ValueError("OpenAI API key not configured")
    
    system_prompt = f"You are a professional translator from {source_lang} to {target_lang}. Translate the following text accurately, preserving the original meaning, formatting, and any technical terminology. Only respond with the translated text, nothing else."
    
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.1  # Lower temperature for more consistent translations
    )
    
    return response.choices[0].message.content

def translate_with_gemini(text: str, source_lang: str, target_lang: str, model: str = "gemini-2.5-pro-exp-03-25") -> str:
    """Translate text using Google Gemini API"""
    if not gemini_available:
        raise ValueError("Google Gemini API key not configured")
    
    model = genai.GenerativeModel(model)
    
    prompt = f"""Translate the following text from {source_lang} to {target_lang}. 
Preserve all formatting, maintain scientific accuracy, and keep any special notation intact.
Only respond with the translated text, nothing else.

TEXT TO TRANSLATE:
{text}
"""
    
    response = model.generate_content(prompt)
    return response.text

def translate_with_claude(text: str, source_lang: str, target_lang: str, model: str = "claude-3-opus-20240229") -> str:
    """Translate text using Anthropic Claude API"""
    if not claude_available:
        raise ValueError("Anthropic Claude API key not configured")
    
    system_prompt = f"You are a professional translator from {source_lang} to {target_lang}. Translate accurately, preserving the original meaning, formatting, and technical terminology."
    
    message = claude_client.messages.create(
        model=model,
        system=system_prompt,
        max_tokens=4000,
        messages=[
            {"role": "user", "content": text}
        ]
    )
    
    return message.content[0].text

def run_pdfmathtranslate(input_file: str, output_file: str, source_lang_code: str, target_lang_code: str, 
                         custom_engine: Optional[str] = None) -> bool:
    """Run PDFMathTranslate CLI tool with appropriate arguments"""
    
    try:
        # Create structured output directory based on language
        input_basename = os.path.splitext(os.path.basename(input_file))[0]
        target_lang_name = next((lang for lang, code in LANGUAGE_CODES.items() if code == target_lang_code), target_lang_code)
        
        # Create a structured output directory format
        structured_output_dir = f"/app/data/output/translations/{target_lang_name}/{input_basename}"
        
        # Ensure the directory exists
        os.makedirs(structured_output_dir, exist_ok=True)
        
        # PDFMathTranslate will create files in this directory
        output_dir = structured_output_dir
        
        # Basic command using PDFMathTranslate
        command = [
            "pdf2zh", 
            input_file,
            "-li", source_lang_code,
            "-lo", target_lang_code,
            "-o", output_dir
        ]
        
        # If using a custom engine, add those arguments
        if custom_engine:
            command.extend(["-e", custom_engine])
            
        # Execute the command
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        print(f"PDFMathTranslate output: {result.stdout}")
        if result.stderr:
            print(f"PDFMathTranslate errors: {result.stderr}")
            
        # The generated files will be in the structured directory
        # PDFMathTranslate creates files with patterns like: base_name-mono.pdf, base_name-dual.pdf
        expected_mono_output = f"{output_dir}/{input_basename}-mono.pdf"
        expected_dual_output = f"{output_dir}/{input_basename}-dual.pdf"
        
        # Final output paths with more descriptive names
        final_mono_output = f"{output_dir}/{input_basename}_{target_lang_name}_translated.pdf"
        final_dual_output = f"{output_dir}/{input_basename}_{target_lang_name}_bilingual.pdf"
        
        success = False
        
        # Rename the output files to more descriptive names if they exist
        if os.path.exists(expected_mono_output):
            import shutil
            shutil.move(expected_mono_output, final_mono_output)
            print(f"Created translated PDF: {final_mono_output}")
            success = True
            
        if os.path.exists(expected_dual_output):
            import shutil
            shutil.move(expected_dual_output, final_dual_output)
            print(f"Created bilingual PDF: {final_dual_output}")
            success = True
            
        # If the requested output_file doesn't match our structure, copy the mono version there
        if success and output_file and output_file.strip() and output_file != final_mono_output:
            import shutil
            # Ensure the output directory exists
            output_dir_path = os.path.dirname(output_file)
            if output_dir_path:  # 出力先ディレクトリが指定されている場合のみ作成
                os.makedirs(output_dir_path, exist_ok=True)
            # Copy the translated file to the requested output location
            shutil.copy(final_mono_output, output_file)
            print(f"Copied translated PDF to requested location: {output_file}")
            
        if success:
            print(f"Translation files available in: {output_dir}")
            return True
        else:
            print(f"Warning: Expected output files not found")
            # Check what files were created in the output directory
            if os.path.exists(output_dir):
                print(f"Files in output directory: {os.listdir(output_dir)}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error running PDFMathTranslate: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def extract_text_segments(pdf_path: str) -> List[str]:
    """Extract text segments from a PDF using PyMuPDF for custom translation"""
    import fitz  # PyMuPDF
    
    segments = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Split text into manageable chunks (paragraphs)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        segments.extend(paragraphs)
    
    return segments

def custom_translate(input_file: str, output_file: str, source_lang: str, target_lang: str, 
                     engine: str, model: str = None) -> bool:
    """Custom translation logic with our API implementations"""
    
    # Get language codes
    source_lang_code = LANGUAGE_CODES.get(source_lang.lower(), source_lang)
    target_lang_code = LANGUAGE_CODES.get(target_lang.lower(), target_lang)
    
    try:
        # Extract text segments from PDF
        segments = extract_text_segments(input_file)
        
        translated_segments = []
        
        # Translate each segment with the chosen engine
        for i, segment in enumerate(segments):
            print(f"Translating segment {i+1}/{len(segments)}")
            
            if engine == "openai":
                translated_text = translate_with_openai(segment, source_lang, target_lang, model)
            elif engine == "gemini":
                translated_text = translate_with_gemini(segment, source_lang, target_lang, model)
            elif engine == "claude":
                translated_text = translate_with_claude(segment, source_lang, target_lang, model)
            else:
                raise ValueError(f"Unknown engine: {engine}")
                
            translated_segments.append(translated_text)
            
            # Avoid rate limits
            time.sleep(0.5)
        
        # Ensure output_file is a valid path if not provided
        if not output_file or not output_file.strip():
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_{target_lang_code}.pdf"
            print(f"No output file specified, using: {output_file}")
        
        # Try using PDFMathTranslate with our results
        return run_pdfmathtranslate(input_file, output_file, source_lang_code, target_lang_code)
    
    except Exception as e:
        print(f"Error in custom translation: {e}")
        return False

def split_pdf(input_file: str, pages_per_chunk: int = 20) -> List[str]:
    """入力PDFファイルを指定されたページ数のチャンクに分割する"""
    import fitz  # PyMuPDF
    import os
    
    temp_dir = tempfile.mkdtemp(prefix="pdf_translate_")
    print(f"一時ファイル用ディレクトリを作成しました: {temp_dir}")
    
    doc = fitz.open(input_file)
    total_pages = len(doc)
    print(f"PDFの総ページ数: {total_pages}")
    
    # チャンク数を計算
    num_chunks = (total_pages + pages_per_chunk - 1) // pages_per_chunk
    
    chunk_files = []
    
    for i in range(num_chunks):
        start_page = i * pages_per_chunk
        end_page = min((i + 1) * pages_per_chunk - 1, total_pages - 1)
        
        # 新しいPDFドキュメントを作成
        new_doc = fitz.open()
        
        # 元のドキュメントからページを選択してコピー
        for page_num in range(start_page, end_page + 1):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        # 一時ファイルとして保存
        chunk_filename = os.path.join(temp_dir, f"chunk_{i+1:03d}.pdf")
        new_doc.save(chunk_filename)
        new_doc.close()
        
        chunk_files.append(chunk_filename)
        print(f"チャンク {i+1}/{num_chunks} を作成しました: ページ {start_page+1}-{end_page+1}")
    
    doc.close()
    return chunk_files

def merge_pdfs(pdf_files: List[str], output_file: str) -> bool:
    """複数のPDFファイルを1つのファイルに結合する"""
    if not merger_available:
        print("警告: PyPDF2がインストールされていないため、PDFの結合ができません。")
        return False
    
    if not pdf_files:
        print("結合するPDFファイルがありません。")
        return False
    
    try:
        merger = PdfMerger()
        
        for pdf in pdf_files:
            if os.path.exists(pdf):
                merger.append(pdf)
            else:
                print(f"警告: ファイル {pdf} が見つかりません。スキップします。")
        
        # 出力先ディレクトリが存在することを確認
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        merger.write(output_file)
        merger.close()
        
        print(f"PDFファイルを正常に結合し、{output_file} に保存しました。")
        return True
    except Exception as e:
        print(f"PDFの結合中にエラーが発生しました: {e}")
        return False

def process_large_pdf(input_file: str, output_file: str, source_lang: str, target_lang: str, 
                     engine: str, model: str = None, pages_per_chunk: int = 20) -> bool:
    """大きなPDFファイルを小さなチャンクに分割して処理し、結果を結合する"""
    # 言語コードを取得
    source_lang_code = LANGUAGE_CODES.get(source_lang.lower(), source_lang)
    target_lang_code = LANGUAGE_CODES.get(target_lang.lower(), target_lang)
    target_lang_name = next((lang for lang, code in LANGUAGE_CODES.items() if code == target_lang_code), target_lang_code)
    
    # 出力ディレクトリの設定
    output_basename = os.path.splitext(os.path.basename(input_file))[0]
    structured_output_dir = f"/app/data/output/translations/{target_lang_name}/{output_basename}"
    os.makedirs(structured_output_dir, exist_ok=True)
    
    # 最終出力ファイルのパスを先に定義しておく
    final_mono_output = f"{structured_output_dir}/{output_basename}_{target_lang_name}_translated.pdf"
    final_dual_output = f"{structured_output_dir}/{output_basename}_{target_lang_name}_bilingual.pdf"
    
    try:
        # PDFを分割
        print(f"PDFを{pages_per_chunk}ページごとに分割しています...")
        chunk_files = split_pdf(input_file, pages_per_chunk)
        
        translated_mono_files = []
        translated_dual_files = []
        
        # 各チャンクを処理
        for i, chunk_file in enumerate(chunk_files):
            print(f"チャンク {i+1}/{len(chunk_files)} を処理しています...")
            
            # 各チャンクの出力ファイル名を設定
            chunk_basename = os.path.splitext(os.path.basename(chunk_file))[0]
            chunk_output_dir = f"{structured_output_dir}/{chunk_basename}"
            os.makedirs(chunk_output_dir, exist_ok=True)
            
            # チャンクを翻訳
            if engine == "default":
                success = run_pdfmathtranslate(
                    chunk_file, None, source_lang_code, target_lang_code
                )
            else:
                success = custom_translate(
                    chunk_file, None, source_lang, target_lang, 
                    engine, model
                )
            
            if success:
                # 翻訳されたファイルを特定
                expected_mono_output = f"{chunk_output_dir}/{chunk_basename}_{target_lang_name}_translated.pdf"
                expected_dual_output = f"{chunk_output_dir}/{chunk_basename}_{target_lang_name}_bilingual.pdf"
                
                if os.path.exists(expected_mono_output):
                    translated_mono_files.append(expected_mono_output)
                if os.path.exists(expected_dual_output):
                    translated_dual_files.append(expected_dual_output)
            else:
                print(f"警告: チャンク {i+1} の処理に失敗しました")
        
        translation_success = False
        
        # 翻訳されたPDFを結合
        if translated_mono_files:
            mono_success = merge_pdfs(translated_mono_files, final_mono_output)
            if mono_success:
                print(f"翻訳済みPDFを作成しました: {final_mono_output}")
                translation_success = True
        else:
            print("警告: 翻訳されたモノリンガルPDFが見つかりません")
        
        if translated_dual_files:
            dual_success = merge_pdfs(translated_dual_files, final_dual_output)
            if dual_success:
                print(f"バイリンガルPDFを作成しました: {final_dual_output}")
                translation_success = True
        else:
            print("警告: 翻訳されたバイリンガルPDFが見つかりません")
        
        # リクエストされた出力ファイルが存在し、かつ異なる場合はコピー
        if translation_success and output_file and output_file.strip() and os.path.exists(final_mono_output) and output_file != final_mono_output:
            import shutil
            output_dir_path = os.path.dirname(output_file)
            if output_dir_path:
                os.makedirs(output_dir_path, exist_ok=True)
            shutil.copy(final_mono_output, output_file)
            print(f"翻訳済みPDFをリクエストされた場所にコピーしました: {output_file}")
        
        return translation_success
        
    except Exception as e:
        print(f"大きなPDFの処理中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Translate PDF documents using PDFMathTranslate with various AI models")
    
    parser.add_argument("input_file", help="Path to the input PDF file")
    parser.add_argument("--output", "-o", help="Path to save the translated PDF", default=None)
    parser.add_argument("--source-lang", "-s", help="Source language", default="english")
    parser.add_argument("--target-lang", "-t", help="Target language", default="japanese")
    parser.add_argument("--engine", "-e", help="Translation engine (openai, gemini, claude, default)",
                        choices=["openai", "gemini", "claude", "default"], default="default")
    parser.add_argument("--model", "-m", help="Specific model for the chosen engine")
    parser.add_argument("--pages-per-chunk", "-p", type=int, help="Number of pages per chunk for large PDFs", default=20)
    parser.add_argument("--large", "-l", action="store_true", help="Force processing as a large PDF with chunking")
    
    args = parser.parse_args()
    
    # Set defaults
    if not args.output:
        # Generate output filename based on input
        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        args.output = f"{base_name}_{args.target_lang}.pdf"
    
    # Get language codes
    source_lang_code = LANGUAGE_CODES.get(args.source_lang.lower(), args.source_lang)
    target_lang_code = LANGUAGE_CODES.get(args.target_lang.lower(), args.target_lang)
    
    # Check if the file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return 1
    
    print(f"Translating {args.input_file} from {args.source_lang} to {args.target_lang}...")
    
    # PyPDF2がインストールされているか確認
    if not merger_available:
        print("警告: PyPDF2がインストールされていません。PDFの分割と結合機能が制限されます。")
        print("PyPDF2をインストールするには: pip install PyPDF2")
    
    # PDFのサイズとページ数を確認
    import fitz
    try:
        doc = fitz.open(args.input_file)
        page_count = len(doc)
        doc.close()
        file_size_mb = os.path.getsize(args.input_file) / (1024 * 1024)
        print(f"PDFファイル情報: {page_count}ページ, {file_size_mb:.2f}MB")
        
        # 大きなPDFまたは多くのページを持つPDFかどうかを判断
        is_large_pdf = args.large or page_count > 30 or file_size_mb > 10
    except Exception as e:
        print(f"PDFファイルの分析中にエラーが発生しました: {e}")
        is_large_pdf = args.large  # エラーが発生した場合は引数に基づいて判断
    
    # Check which translation approach to use
    if args.engine == "default" and not is_large_pdf:
        # 小さなPDFの場合はPDFMathTranslateの組み込み翻訳を使用
        print("小さなPDFとして処理しています...")
        success = run_pdfmathtranslate(
            args.input_file, args.output, source_lang_code, target_lang_code
        )
    else:
        # 大きなPDFまたはカスタムエンジンの場合は分割処理を使用
        print(f"大きなPDFとして処理しています（{args.pages_per_chunk}ページごとに分割）...")
        success = process_large_pdf(
            args.input_file, args.output, args.source_lang, args.target_lang, 
            args.engine, args.model, args.pages_per_chunk
        )
    
    if success:
        print(f"Translation completed successfully. Output saved to {args.output}")
        return 0
    else:
        print("Translation failed")
        return 1

if __name__ == "__main__":
    main()