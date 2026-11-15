"""
Data processor for Bangladesh Constitution Chatbot (English only)
Handles downloading, extracting, and preprocessing of Constitution text
"""
import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse

import requests
import PyPDF2
import pdfplumber
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

class ConstitutionProcessor:
    """Processes Bangladesh Constitution data for RAG pipeline (English only)"""
    
    def __init__(self):
        self.config = Config()
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [
            self.config.RAW_DATA_DIR,
            self.config.PROCESSED_DATA_DIR,
            self.config.VECTORSTORE_DIR
        ]:
            os.makedirs(directory, exist_ok=True)
    
    def download_file(self, url: str, filename: str) -> bool:
        """Download a file from URL"""
        filepath = os.path.join(self.config.RAW_DATA_DIR, filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"File {filename} already exists. Skipping download.")
            return True
        
        try:
            print(f"Downloading {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as file, tqdm(
                desc=filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = file.write(chunk)
                    pbar.update(size)
            
            print(f"Successfully downloaded {filename}")
            return True
            
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return False
    
    def download_constitution_files(self) -> bool:
        """Download Constitution files (English and Bengali)"""
        success_en = self.download_file(
            self.config.CONSTITUTION_EN_URL, 
            "bangladesh_constitution_en.pdf"
        )
        success_bn = self.download_file(
            self.config.CONSTITUTION_BN_URL,
            "bangladesh_constitution_bn.pdf"
        )
        return success_en and success_bn
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods for best results"""
        text = ""
        
        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}")
        
        # Fallback to PyPDF2 if pdfplumber fails or returns empty
        if not text.strip():
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"PyPDF2 also failed: {e}")
        
        return text
    
    def clean_text(self, text: str, language: str = "en") -> str:
        """Clean and normalize extracted text for both English and Bengali."""
        if not text.strip():
            return ""
        
        # General cleanup for both languages
        text = re.sub(r'\[\s*\d+\s*\]', '', text)  # Remove bracketed numbers like [1]
        
        if language == "en":
            # English-specific cleanup
            text = text.replace("THE CONSTITUTION OF THE PEOPLE'S REPUBLIC OF BANGLADESH", "")
            text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
            text = text.replace("1[", "").replace("2[", "")  # Common OCR error
        elif language == "bn":
            # Bengali-specific cleanup
            # Remove common Bengali header/footer patterns
            text = text.replace("গণপ্রজাতন্ত্রী বাংলাদেশের সংবিধান", "")
            text = re.sub(r'পৃষ্ঠা\s*\d+', '', text)  # Remove page numbers in Bengali
            text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Remove lone numbers
        
        # Normalize whitespace and remove excessive newlines
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'(\n\s*){2,}', '\n', text)
        
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        """Detect language based on text content and Bengali Unicode characters"""
        if not text.strip():
            return 'en'
        
        # Check for Bengali Unicode characters (U+0980 to U+09FF)
        bengali_chars = len([c for c in text if '\u0980' <= c <= '\u09FF'])
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars > 0:
            bengali_ratio = bengali_chars / total_chars
            # If more than 30% of characters are Bengali, classify as Bengali
            if bengali_ratio > 0.3:
                return 'bn'
        
        return 'en'
    
    def _get_article_pattern(self, language: str) -> str:
        """Returns the regex pattern for splitting by articles for both English and Bengali."""
        if language == 'bn':
            # Bengali patterns - matches "ধারা ১", "ভাগ ১", "উদ্দেশিকা", etc.
            return r'(?=\bধারা\s+[০-৯১-৯]+\b|\bভাগ\s+[০-৯১-৯IVXLCivxlc]+\b|\bউদ্দেশিকা\b|\bতফসিল\b)'
        else:
            # English patterns - matches "PART...", "PREAMBLE", "ARTICLE 1", "SCHEDULE"
            return r'(?=\bPART\s+[IVXLC]+\b|PREAMBLE|ARTICLE\s+\d+[A-Z]?\b|THE\s+\w+\s+SCHEDULE\b)'

    def hybrid_chunking_strategy(self, text: str, language: str) -> List[Dict]:
        """
        Combines logical (article-based) and semantic (size-based) chunking.
        Supports both English and Bengali.
        1. Splits the document by major logical boundaries (Parts, Articles).
        2. For each logical section, uses a text splitter to create smaller semantic chunks.
        """
        all_chunks = []
        
        # 1. Split the document by major logical sections (Articles, Parts, etc.)
        article_pattern = self._get_article_pattern(language)
        logical_sections = re.split(article_pattern, text)
        
        # Initialize splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""] if language == 'en' else ["\n\n", "\n", "। ", " ", ""]
        )

        current_metadata = {}
        
        for section in logical_sections:
            if not section.strip():
                continue

            # Update metadata based on language
            if language == 'bn':
                # Bengali header matching
                header_match = re.match(r'(ভাগ\s+[০-৯১-৯IVXLCivxlc]+)|(ধারা\s+[০-৯১-৯]+[ক-য]?)|(উদ্দেশিকা)|(তফসিল)', section)
            else:
                # English header matching
                header_match = re.match(r'(PART\s+[IVXLC]+)|(ARTICLE\s+\d+[A-Z]?)|(PREAMBLE)|(THE\s+\w+\s+SCHEDULE)', section)

            if header_match:
                if header_match.group(1):  # PART/ভাগ
                    current_metadata['part'] = section.strip()
                elif header_match.group(2):  # ARTICLE/ধারা
                    current_metadata['article'] = section.strip()
                    current_metadata['article_number'] = self._extract_article_number(section, language)
                elif header_match.group(3):  # PREAMBLE/উদ্দেশিকা
                    current_metadata['part'] = 'PREAMBLE' if language == 'en' else 'উদ্দেশিকা'
                elif header_match.group(4):  # SCHEDULE/তফসিল
                    current_metadata['part'] = section.strip()

            # 2. Split the current section into smaller semantic chunks
            sub_chunks = text_splitter.split_text(section)
            
            for sub_chunk in sub_chunks:
                chunk_metadata = {
                    'source': 'Bangladesh Constitution',
                    'language': language,
                    'last_amended': '2018',
                    **current_metadata
                }
                
                all_chunks.append({
                    'content': sub_chunk,
                    'metadata': chunk_metadata
                })

        # Post-process to merge content into metadata for clarity
        for i, chunk in enumerate(all_chunks):
            chunk['chunk_id'] = i
            # To avoid redundancy, we can just keep the numbers
            if 'article' in chunk['metadata']:
                chunk['metadata']['article_header'] = chunk['metadata'].pop('article')

        return all_chunks

    def _extract_article_number(self, article_text: str, language: str = 'en') -> Optional[str]:
        """Extract article number from article text for both English and Bengali"""
        if language == 'bn':
            # Bengali number extraction - matches "ধারা ১২৩" or "ধারা ১২ক"
            match = re.search(r'ধারা\s+([০-৯১-৯]+[ক-য]?)', article_text)
            if match:
                bengali_num = match.group(1)
                # Convert Bengali numerals to English for consistency
                bengali_to_english = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
                return bengali_num.translate(bengali_to_english)
        else:
            # English number extraction
            match = re.search(r'ARTICLE\s+(\d+[A-Z]?)', article_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def process_constitution_files(self) -> bool:
        """Process Constitution files (English and Bengali)"""
        files_to_process = [
            ("bangladesh_constitution_en.pdf", "en"),
            ("bangladesh_constitution_bn.pdf", "bn")
        ]
        
        all_chunks_combined = []
        total_chunks = 0
        
        for filename, expected_lang in files_to_process:
            filepath = os.path.join(self.config.RAW_DATA_DIR, filename)
            
            if not os.path.exists(filepath):
                print(f"⚠️ File {filename} not found. Skipping...")
                continue
            
            print(f"📖 Processing {filename}...")
            
            # Extract text
            text = self.extract_text_from_pdf(filepath)
            if not text.strip():
                print(f"❌ No text extracted from {filename}")
                continue
            
            # Detect language (should match expected)
            detected_lang = self.detect_language(text)
            if detected_lang != expected_lang:
                print(f"⚠️ Language mismatch in {filename}: expected {expected_lang}, detected {detected_lang}")
                detected_lang = expected_lang  # Use expected language
            
            print(f"🌐 Processing language: {detected_lang}")
            
            # Clean text
            cleaned_text = self.clean_text(text, detected_lang)
            
            # Save raw text
            text_filename = f"constitution_{detected_lang}_raw.txt"
            with open(os.path.join(self.config.PROCESSED_DATA_DIR, text_filename), 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # Use the hybrid chunking strategy
            chunks = self.hybrid_chunking_strategy(cleaned_text, detected_lang)
            print(f"📄 Created {len(chunks)} chunks for {detected_lang}")
            
            # Save language-specific chunks
            chunks_filename = f"constitution_{detected_lang}_chunks.json"
            with open(os.path.join(self.config.PROCESSED_DATA_DIR, chunks_filename), 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            # Add to combined chunks
            all_chunks_combined.extend(chunks)
            total_chunks += len(chunks)
        
        if not all_chunks_combined:
            print("❌ No chunks created from any file")
            return False
        
        # Save all chunks in standard format (both languages combined)
        final_chunks_for_json = [
            {
                "page_content": chunk['content'],
                "metadata": chunk['metadata']
            } for chunk in all_chunks_combined
        ]

        with open(os.path.join(self.config.PROCESSED_DATA_DIR, "all_chunks.json"), 'w', encoding='utf-8') as f:
            json.dump(final_chunks_for_json, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Total chunks created: {total_chunks} (English + Bengali)")
        
        # Show language breakdown
        lang_counts = {}
        for chunk in all_chunks_combined:
            lang = chunk['metadata'].get('language', 'unknown')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        print("📊 Language breakdown:")
        for lang, count in lang_counts.items():
            lang_name = "English" if lang == "en" else "Bengali" if lang == "bn" else lang
            print(f"   {lang_name}: {count} chunks")
        
        return total_chunks > 0
    
    def get_processing_stats(self) -> Dict:
        """Get statistics about processed data"""
        stats = {
            'raw_files': [],
            'processed_files': [],
            'total_chunks': 0,
            'chunks_by_language': {}
        }
        
        # Check raw files
        for filename in os.listdir(self.config.RAW_DATA_DIR):
            if filename.endswith('.pdf'):
                stats['raw_files'].append(filename)
        
        # Check processed files
        for filename in os.listdir(self.config.PROCESSED_DATA_DIR):
            stats['processed_files'].append(filename)
        
        # Check chunks
        chunks_file = os.path.join(self.config.PROCESSED_DATA_DIR, "all_chunks.json")
        if os.path.exists(chunks_file):
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                stats['total_chunks'] = len(chunks)
                
                for chunk in chunks:
                    lang = chunk.get('metadata', {}).get('language', 'unknown')
                    if lang not in stats['chunks_by_language']:
                        stats['chunks_by_language'][lang] = 0
                    stats['chunks_by_language'][lang] += 1
        
        return stats

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Process Bangladesh Constitution data (English & Bengali)")
    parser.add_argument("--download", action="store_true", help="Download Constitution file")
    parser.add_argument("--process", action="store_true", help="Process Constitution file into chunks")
    parser.add_argument("--stats", action="store_true", help="Show processing statistics")
    parser.add_argument("--all", action="store_true", help="Download and process all data")
    
    args = parser.parse_args()
    
    processor = ConstitutionProcessor()
    
    if args.all:
        args.download = True
        args.process = True
    
    if args.download:
        print("Downloading Constitution file...")
        success = processor.download_constitution_files()
        if success:
            print("✅ Download completed successfully")
        else:
            print("❌ Download failed")
            return False
    
    if args.process:
        print("Processing Constitution file...")
        success = processor.process_constitution_files()
        if success:
            print("✅ Processing completed successfully")
        else:
            print("❌ Processing failed")
            return False
    
    if args.stats:
        stats = processor.get_processing_stats()
        print("\n📊 Processing Statistics:")
        print(f"Raw files: {len(stats['raw_files'])}")
        print(f"Processed files: {len(stats['processed_files'])}")
        print(f"Total chunks: {stats['total_chunks']}")
        print("Chunks by language:")
        for lang, count in stats['chunks_by_language'].items():
            print(f"  {lang}: {count}")
    
    if not any([args.download, args.process, args.stats, args.all]):
        parser.print_help()

if __name__ == "__main__":
    main()