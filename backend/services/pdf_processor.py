import re
import PyPDF2
from pathlib import Path
from typing import List, Dict

class PDFProcessor:
    
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:!?()，。；：！？（）、]', '', text)
        text = text.strip()
        return text
    
    @staticmethod
    def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def process_pdf(self, pdf_path: str, chunk_size: int = 500, overlap: int = 50) -> Dict:
        raw_text = self.extract_text(pdf_path)
        cleaned_text = self.clean_text(raw_text)
        chunks = self.split_into_chunks(cleaned_text, chunk_size, overlap)
        
        return {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'chunks': chunks,
            'num_chunks': len(chunks)
        }

