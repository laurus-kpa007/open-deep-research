"""Language detection utility for multilingual support."""

import re
import logging
from typing import Literal
import langdetect
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

LanguageCode = Literal["ko", "en"]

class LanguageDetector:
    """Utility class for detecting and handling multiple languages."""
    
    @staticmethod
    def detect_language(text: str) -> LanguageCode:
        """
        Detect the primary language of the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code ('ko' for Korean, 'en' for English)
        """
        if not text or not text.strip():
            return "en"
        
        try:
            # Clean text for better detection
            cleaned_text = LanguageDetector._clean_text(text)
            
            # Check for Korean characters first (more reliable)
            korean_char_count = len(re.findall(r'[가-힣]', cleaned_text))
            total_chars = len(re.sub(r'\s', '', cleaned_text))
            
            # If more than 10% Korean characters, it's likely Korean
            if total_chars > 0 and (korean_char_count / total_chars) > 0.1:
                return "ko"
            
            # Use langdetect for other languages
            detected = langdetect.detect(cleaned_text)
            
            # Map detected languages to supported languages
            if detected == "ko":
                return "ko"
            else:
                return "en"  # Default to English for all non-Korean languages
                
        except LangDetectException:
            logger.warning(f"Language detection failed for text: {text[:50]}...")
            # Fallback: check for Korean characters
            if re.search(r'[가-힣]', text):
                return "ko"
            return "en"
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            return "en"
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text for better language detection."""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def is_korean(text: str) -> bool:
        """
        Check if the text is primarily Korean.
        
        Args:
            text: Input text to check
            
        Returns:
            True if the text is primarily Korean
        """
        return LanguageDetector.detect_language(text) == "ko"
    
    @staticmethod
    def is_english(text: str) -> bool:
        """
        Check if the text is primarily English.
        
        Args:
            text: Input text to check
            
        Returns:
            True if the text is primarily English
        """
        return LanguageDetector.detect_language(text) == "en"
    
    @staticmethod
    def get_language_confidence(text: str) -> dict:
        """
        Get language detection confidence scores.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with language codes and confidence scores
        """
        try:
            from langdetect import detect_langs
            
            cleaned_text = LanguageDetector._clean_text(text)
            if not cleaned_text:
                return {"en": 1.0}
            
            # Get detection probabilities
            lang_probs = detect_langs(cleaned_text)
            
            result = {}
            for lang_prob in lang_probs:
                lang_code = "ko" if lang_prob.lang == "ko" else "en"
                if lang_code in result:
                    result[lang_code] += lang_prob.prob
                else:
                    result[lang_code] = lang_prob.prob
            
            # Ensure we have Korean and English scores
            if "ko" not in result:
                result["ko"] = 0.0
            if "en" not in result:
                result["en"] = 0.0
            
            # Adjust for Korean character presence
            korean_chars = len(re.findall(r'[가-힣]', cleaned_text))
            total_chars = len(re.sub(r'\s', '', cleaned_text))
            
            if total_chars > 0:
                korean_ratio = korean_chars / total_chars
                if korean_ratio > 0.1:
                    result["ko"] = max(result["ko"], korean_ratio)
                    result["en"] = min(result["en"], 1 - korean_ratio)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting language confidence: {e}")
            # Fallback
            if re.search(r'[가-힣]', text):
                return {"ko": 0.8, "en": 0.2}
            return {"ko": 0.1, "en": 0.9}
    
    @staticmethod
    def format_for_language(text: str, language: LanguageCode) -> str:
        """
        Format text appropriately for the target language.
        
        Args:
            text: Text to format
            language: Target language
            
        Returns:
            Formatted text
        """
        if language == "ko":
            # Korean-specific formatting
            # Ensure proper spacing around Korean punctuation
            text = re.sub(r'([가-힣])\s*([,.!?])', r'\1\2', text)
            # Add space after punctuation
            text = re.sub(r'([,.!?])([가-힣])', r'\1 \2', text)
        else:
            # English-specific formatting
            # Ensure proper spacing around punctuation
            text = re.sub(r'\s*([,.!?])\s*', r'\1 ', text)
            # Remove extra spaces
            text = re.sub(r'\s+', ' ', text)
        
        return text.strip()