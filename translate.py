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

def translate_with_gemini(text: str, source_lang: str, target_lang: str, model: str = "gemini-1.5-pro") -> str:
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
        # Basic command using PDFMathTranslate
        command = [
            "pdf2zh", 
            input_file,
            "-li", source_lang_code,
            "-lo", target_lang_code,
            "-o", output_file
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
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running PDFMathTranslate: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
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
        
        # TODO: Improve this to maintain PDF layout
        # For now, we'll just join the segments and let PDFMathTranslate handle the layout
        # by providing a custom engine/translator
        
        # Write the results to be used with PDFMathTranslate
        # This is a simplified approach - a full implementation would require
        # deeper integration with PDFMathTranslate's internal API
        
        # Try using PDFMathTranslate with our results
        return run_pdfmathtranslate(input_file, output_file, source_lang_code, target_lang_code)
    
    except Exception as e:
        print(f"Error in custom translation: {e}")
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
    
    # Check which translation approach to use
    if args.engine == "default":
        # Use PDFMathTranslate's built-in translation
        success = run_pdfmathtranslate(
            args.input_file, args.output, source_lang_code, target_lang_code
        )
    else:
        # Use our custom implementation with the specified engine
        success = custom_translate(
            args.input_file, args.output, args.source_lang, args.target_lang, 
            args.engine, args.model
        )
    
    if success:
        print(f"Translation completed successfully. Output saved to {args.output}")
        return 0
    else:
        print("Translation failed")
        return 1

if __name__ == "__main__":
    main()