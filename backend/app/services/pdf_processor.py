"""
PDF processing service for extracting text and handling OCR fallback.
"""
import logging
import io
from typing import List, Dict, Any, Optional
import PyPDF2
import pdfplumber
from PIL import Image
import pytesseract
from ..settings import settings

logger = logging.getLogger(__name__)


class PDFProcessorService:
    def __init__(self):
        self.ocr_enabled = True  # Enable OCR fallback
        
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF bytes
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            result = {
                'pages': [],
                'total_pages': 0,
                'extraction_method': 'pdfplumber',
                'success': True,
                'error': None
            }
            
            # Try pdfplumber first (better text extraction)
            try:
                result = self._extract_with_pdfplumber(pdf_bytes)
                if result['success'] and any(page['text'].strip() for page in result['pages']):
                    logger.info(f"Successfully extracted text using pdfplumber: {result['total_pages']} pages")
                    return result
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}")
            
            # Fallback to PyPDF2
            try:
                result = self._extract_with_pypdf2(pdf_bytes)
                if result['success'] and any(page['text'].strip() for page in result['pages']):
                    logger.info(f"Successfully extracted text using PyPDF2: {result['total_pages']} pages")
                    return result
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed: {e}")
            
            # If no text extracted, try OCR on page images (if enabled)
            if self.ocr_enabled:
                try:
                    result = self._extract_with_ocr(pdf_bytes)
                    if result['success']:
                        logger.info(f"Successfully extracted text using OCR: {result['total_pages']} pages")
                        return result
                except Exception as e:
                    logger.warning(f"OCR extraction failed: {e}")
            
            # If all methods fail
            result['success'] = False
            result['error'] = "All text extraction methods failed"
            logger.error("All PDF text extraction methods failed")
            return result
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return {
                'pages': [],
                'total_pages': 0,
                'extraction_method': 'failed',
                'success': False,
                'error': str(e)
            }
    
    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text using pdfplumber"""
        result = {
            'pages': [],
            'total_pages': 0,
            'extraction_method': 'pdfplumber',
            'success': False,
            'error': None
        }
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                result['total_pages'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    
                    page_data = {
                        'page_number': page_num,
                        'text': text,
                        'confidence': 1.0,  # pdfplumber doesn't provide confidence scores
                        'extraction_method': 'pdfplumber'
                    }
                    
                    result['pages'].append(page_data)
                
                result['success'] = True
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"pdfplumber extraction failed: {e}")
        
        return result
    
    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text using PyPDF2"""
        result = {
            'pages': [],
            'total_pages': 0,
            'extraction_method': 'pypdf2',
            'success': False,
            'error': None
        }
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            result['total_pages'] = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text() or ""
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    text = ""
                
                page_data = {
                    'page_number': page_num,
                    'text': text,
                    'confidence': 1.0,  # PyPDF2 doesn't provide confidence scores
                    'extraction_method': 'pypdf2'
                }
                
                result['pages'].append(page_data)
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"PyPDF2 extraction failed: {e}")
        
        return result
    
    def _extract_with_ocr(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text using OCR (requires pdf2image or similar)"""
        result = {
            'pages': [],
            'total_pages': 0,
            'extraction_method': 'ocr',
            'success': False,
            'error': None
        }
        
        try:
            # This is a simplified OCR implementation
            # In production, you might want to use pdf2image to convert PDF to images first
            logger.warning("OCR extraction not fully implemented - requires pdf2image")
            result['error'] = "OCR extraction not implemented"
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"OCR extraction failed: {e}")
        
        return result
    
    def get_page_text(self, pdf_bytes: bytes, page_number: int) -> Optional[str]:
        """
        Get text from a specific page
        
        Args:
            pdf_bytes: PDF file as bytes
            page_number: Page number (1-indexed)
            
        Returns:
            Text from the specified page or None if not found
        """
        try:
            result = self.extract_text_from_pdf(pdf_bytes)
            if result['success'] and page_number <= len(result['pages']):
                return result['pages'][page_number - 1]['text']
        except Exception as e:
            logger.error(f"Failed to get page {page_number} text: {e}")
        
        return None
    
    def get_pdf_info(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Get PDF metadata and basic info
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Dictionary with PDF information
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            info = {
                'total_pages': len(pdf_reader.pages),
                'metadata': pdf_reader.metadata or {},
                'is_encrypted': pdf_reader.is_encrypted,
                'success': True
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get PDF info: {e}")
            return {
                'total_pages': 0,
                'metadata': {},
                'is_encrypted': False,
                'success': False,
                'error': str(e)
            }


# Global instance
pdf_processor_service = PDFProcessorService()

