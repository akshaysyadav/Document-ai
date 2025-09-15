import pytesseract
from PIL import Image
import logging
import os

logger = logging.getLogger(__name__)

# Tesseract configuration
TESSERACT_CMD = os.getenv("TESSERACT_CMD", None)
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image using Tesseract OCR
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text
    """
    try:
        logger.info(f"Starting OCR processing for: {image_path}")
        
        # Open image
        image = Image.open(image_path)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image, lang='eng')
        
        logger.info(f"OCR completed. Extracted {len(text)} characters")
        return text.strip()
        
    except Exception as e:
        logger.error(f"OCR processing failed for {image_path}: {e}")
        raise

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF (placeholder for future implementation)
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    logger.warning("PDF text extraction not implemented yet")
    return "PDF text extraction coming soon..."

def preprocess_image(image_path: str, output_path: str = None) -> str:
    """
    Preprocess image for better OCR results
    
    Args:
        image_path (str): Path to input image
        output_path (str): Path for processed image (optional)
        
    Returns:
        str: Path to processed image
    """
    try:
        logger.info(f"Preprocessing image: {image_path}")
        
        # Open image
        image = Image.open(image_path)
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Simple preprocessing (can be enhanced)
        # For now, just return the grayscale image
        
        if output_path is None:
            output_path = image_path.replace('.', '_processed.')
            
        image.save(output_path)
        logger.info(f"Image preprocessed and saved to: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Image preprocessing failed for {image_path}: {e}")
        raise

def get_ocr_confidence(image_path: str) -> dict:
    """
    Get OCR confidence scores
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: OCR confidence data
    """
    try:
        logger.info(f"Getting OCR confidence for: {image_path}")
        
        # Open image
        image = Image.open(image_path)
        
        # Get OCR data with confidence
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        result = {
            "average_confidence": avg_confidence,
            "total_words": len([word for word in data['text'] if word.strip()]),
            "low_confidence_words": len([conf for conf in confidences if conf < 50])
        }
        
        logger.info(f"OCR confidence analysis completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"OCR confidence analysis failed for {image_path}: {e}")
        raise

# Supported file types
SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif']
SUPPORTED_PDF_TYPES = ['.pdf']

def is_supported_file(file_path: str) -> bool:
    """
    Check if file type is supported for OCR
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if supported, False otherwise
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in SUPPORTED_IMAGE_TYPES or file_ext in SUPPORTED_PDF_TYPES
