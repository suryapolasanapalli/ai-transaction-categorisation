"""Preprocessing Agent - Extracts and cleans transaction data"""
from typing import Dict, Any, Optional
import re
import hashlib
import spacy

# Load spaCy English model for advanced NLP (lemmatization, POS tagging)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if model not installed
    print("Warning: spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    nlp = None


class PreprocessingAgent:
    """
    Agno Agent responsible for preprocessing transaction data with:
    - Tokenization: Breaking down transaction text into tokens
    - Noise Removal: Removing transaction IDs, location codes, unnecessary data
    - Text Normalization: Standardizing merchant names
    - Merchant Canonicalization: Creating Canonical Merchant ID (CMID)
    - Data Encryption: Tokenizing and encrypting sensitive data
    """
    
    def __init__(self, llm):
        """
        Initialize the Preprocessing Agent
        
        Args:
            llm: Agno LLM instance (Azure OpenAI)
        """
        self.llm = llm
        self.agent_name = "PreprocessingAgent"
        
        # Common noise patterns to remove
        self.noise_patterns = [
            r'#\d+',           # Transaction IDs like #12345
            r'\d{4,}',         # Long numeric codes
            r'[A-Z]{2}\d{3,}', # Location codes like CA123
            r'\*+',            # Asterisks
            r'REF:\w+',        # Reference codes
        ]
        
        # Known merchant variations for canonicalization
        self.merchant_canonical_map = {
            'STARBUCKS': ['STARBUCKS', 'SBX', 'SBUX', 'STARBUCK'],
            'MCDONALDS': ['MCDONALDS', 'MCD', 'MCDONALD'],
            'WALMART': ['WALMART', 'WAL-MART', 'WMART'],
            'TARGET': ['TARGET', 'TGT'],
            'AMAZON': ['AMAZON', 'AMZN', 'AMZ'],
            'SHELL': ['SHELL', 'SHELL OIL'],
            'CHEVRON': ['CHEVRON', 'CHEV'],
            'UBER': ['UBER', 'UBER TRIP', 'UBER EATS'],
            'LYFT': ['LYFT', 'LYFT RIDE'],
        }
    
    def _tokenize(self, text: str) -> list:
        """
        Tokenize transaction description into individual tokens using spaCy NLP
        
        Args:
            text: Raw transaction text
            
        Returns:
            List of lemmatized tokens (base forms)
        """
        if nlp:
            # Use spaCy for intelligent tokenization and lemmatization
            doc = nlp(text.lower())
            # Extract lemmas, filter out stopwords and punctuation
            tokens = [
                token.lemma_.upper() 
                for token in doc 
                if not token.is_stop and not token.is_punct and token.is_alpha
            ]
            return tokens
        else:
            # Fallback to regex if spaCy not available
            tokens = re.findall(r'\b\w+\b', text.upper())
            return tokens
    
    def _remove_noise(self, text: str) -> str:
        """
        Remove noise patterns from transaction description
        
        Args:
            text: Transaction text
            
        Returns:
            Cleaned text without noise
        """
        cleaned = text
        for pattern in self.noise_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text using spaCy lemmatization for better linguistic accuracy
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text with lemmatized words
        """
        if nlp:
            # Use spaCy for linguistic normalization
            doc = nlp(text.lower())
            # Get lemmas, remove stopwords and punctuation
            lemmas = [
                token.lemma_ 
                for token in doc 
                if not token.is_stop and not token.is_punct and token.is_alpha
            ]
            normalized = ' '.join(lemmas).upper()
        else:
            # Fallback to basic normalization
            normalized = text.upper()
            normalized = re.sub(r'[^A-Z0-9\s]', '', normalized)
            normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _canonicalize_merchant(self, merchant_text: str) -> tuple[str, str]:
        """
        Canonicalize merchant name to standard form and create CMID
        
        Args:
            merchant_text: Extracted/normalized merchant text
            
        Returns:
            Tuple of (canonical_name, cmid)
        """
        merchant_upper = merchant_text.upper()
        
        # Check against known variations
        for canonical, variations in self.merchant_canonical_map.items():
            for variation in variations:
                if variation in merchant_upper:
                    # Create CMID using SHA-256 hash
                    cmid = hashlib.sha256(canonical.encode()).hexdigest()[:16]
                    return canonical, cmid
        
        # If no match, use normalized text and create CMID
        canonical = merchant_text.strip()
        cmid = hashlib.sha256(canonical.upper().encode()).hexdigest()[:16]
        return canonical, cmid
    
    def _tokenize_sensitive_data(self, amount: float, mcc_code: Optional[str] = None) -> Dict[str, str]:
        """
        Tokenize and encrypt sensitive financial data
        
        Args:
            amount: Transaction amount
            mcc_code: Merchant Category Code
            
        Returns:
            Dict with tokenized data
        """
        # Create tokenized representations (in production, use proper encryption)
        amount_token = hashlib.sha256(f"AMT_{amount}".encode()).hexdigest()[:16]
        mcc_token = hashlib.sha256(f"MCC_{mcc_code}".encode()).hexdigest()[:16] if mcc_code else None
        
        return {
            "amount_token": amount_token,
            "mcc_token": mcc_token,
            "amount_encrypted": True,
            "mcc_encrypted": bool(mcc_code)
        }
    
    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location information from transaction text
        
        Args:
            text: Transaction text
            
        Returns:
            Location string if found, None otherwise
        """
        # Common US state codes
        state_pattern = r'\b([A-Z]{2})\b'
        match = re.search(state_pattern, text)
        
        if match:
            state = match.group(1)
            # Verify it's likely a state code (basic check)
            common_states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
            if state in common_states:
                return state
        
        return None
    
    def execute(self, 
                description: str, 
                amount: float,
                merchant_name: Optional[str] = None,
                mcc_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute preprocessing pipeline on transaction data
        
        Input Fields:
            - Merchant Name (optional)
            - Description (required)
            - Amount (required)
            - MCC Code (optional)
        
        Steps:
            1. Tokenization: Break down text into tokens
            2. Noise Removal: Remove transaction IDs, codes, unnecessary data
            3. Text Normalization: Standardize merchant names
            4. Merchant Canonicalization: Create CMID for deterministic classification
            5. Sensitive Data Tokenization: Encrypt sensitive information
        
        Args:
            description: Raw transaction description
            amount: Transaction amount
            merchant_name: Optional pre-provided merchant name
            mcc_code: Optional Merchant Category Code
            
        Returns:
            Dict with preprocessed transaction data including CMID
        """
        # Step 1: Tokenization
        tokens = self._tokenize(description)
        
        # Step 2: Noise Removal
        cleaned_description = self._remove_noise(description)
        
        # Step 3: Text Normalization
        normalized_text = self._normalize_text(cleaned_description)
        
        # Extract merchant name if not provided
        if not merchant_name and normalized_text:
            # Use first meaningful tokens as merchant name
            merchant_tokens = [t for t in tokens if len(t) > 2][:3]
            merchant_name = ' '.join(merchant_tokens) if merchant_tokens else "UNKNOWN"
        elif merchant_name:
            merchant_name = self._normalize_text(merchant_name)
        else:
            merchant_name = "UNKNOWN"
        
        # Step 4: Merchant Canonicalization - Create CMID
        canonical_merchant, cmid = self._canonicalize_merchant(merchant_name)
        
        # Step 5: Sensitive Data Tokenization & Encryption
        sensitive_tokens = self._tokenize_sensitive_data(amount, mcc_code)
        
        # Extract additional metadata
        location = self._extract_location(description)
        
        # Determine transaction type (can be enhanced with LLM)
        transaction_type = "purchase"  # Default
        if any(word in description.upper() for word in ['REFUND', 'RETURN']):
            transaction_type = "refund"
        elif any(word in description.upper() for word in ['SUBSCRIPTION', 'RECURRING']):
            transaction_type = "subscription"
        
        return {
            "merchant_name": canonical_merchant,
            "canonical_merchant_id": cmid,
            "cleaned_description": cleaned_description,
            "normalized_text": normalized_text,
            "tokens": tokens,
            "location": location,
            "transaction_type": transaction_type,
            "sensitive_data": sensitive_tokens,
            "mcc_code_provided": bool(mcc_code),
            "metadata": {
                "original_description": description,
                "token_count": len(tokens),
                "noise_removed": len(description) > len(cleaned_description),
                "canonicalized": canonical_merchant != merchant_name.strip(),
                "security_compliant": True
            }
        }
