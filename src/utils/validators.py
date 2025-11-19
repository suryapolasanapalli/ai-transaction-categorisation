"""Validation utilities for transaction data"""
from typing import Dict, Any, List, Optional


def validate_transaction_data(data: Dict[str, Any]) -> tuple[bool, Optional[List[str]]]:
    """
    Validate transaction data completeness and correctness
    
    Args:
        data: Transaction data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = [
        'merchant_name',
        'category',
        'mcc_code',
        'confidence',
        'validation_status'
    ]
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Validate confidence level
    valid_confidence = ['high', 'medium', 'low']
    if 'confidence' in data and data['confidence'] not in valid_confidence:
        errors.append(f"Invalid confidence level: {data['confidence']}")
    
    # Validate MCC code format (4 digits)
    if 'mcc_code' in data:
        mcc = str(data['mcc_code'])
        if not mcc.isdigit() or len(mcc) != 4:
            errors.append(f"Invalid MCC code format: {mcc}")
    
    # Validate validation status
    valid_statuses = ['PASS', 'FAIL', 'REVIEW']
    if 'validation_status' in data and data['validation_status'] not in valid_statuses:
        errors.append(f"Invalid validation status: {data['validation_status']}")
    
    is_valid = len(errors) == 0
    return is_valid, errors if errors else None


def validate_category(category: str, valid_categories: List[str]) -> bool:
    """
    Validate if category is in the list of valid categories
    
    Args:
        category: Category to validate
        valid_categories: List of valid category names
        
    Returns:
        True if valid, False otherwise
    """
    return category in valid_categories


def sanitize_amount(amount: Any) -> float:
    """
    Sanitize and convert amount to float
    
    Args:
        amount: Amount value (any type)
        
    Returns:
        Float value of amount
    """
    try:
        return float(amount)
    except (ValueError, TypeError):
        return 0.0
