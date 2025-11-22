"""Custom Categories Tool - Match transactions to user-defined custom categories"""
from typing import Dict, Any, Optional
from agno.tools import tool
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.custom_categories import get_custom_categories_manager


@tool
def get_custom_categories() -> Dict[str, Any]:
    """
    Get all available custom categories defined by the user.
    
    Use this tool to check if custom categories exist and see their structure.
    If custom categories exist, you should use match_to_custom_category tool
    to classify the transaction.
    
    Returns:
        Dict with custom categories information:
        {
            "has_custom_categories": True/False,
            "categories": {
                "Category Name": ["subcategory1", "subcategory2", ...],
                ...
            },
            "category_structure": "Formatted text with all categories and subcategories",
            "message": "Custom categories available" or "No custom categories defined"
        }
    """
    custom_categories_manager = get_custom_categories_manager()
    custom_categories = custom_categories_manager.get_categories()
    
    if custom_categories:
        return {
            "has_custom_categories": True,
            "categories": custom_categories,
            "category_structure": custom_categories_manager.get_category_structure(),
            "message": f"Found {len(custom_categories)} custom categories. Use match_to_custom_category tool to classify."
        }
    else:
        return {
            "has_custom_categories": False,
            "categories": {},
            "category_structure": "",
            "message": "No custom categories defined. Use default taxonomy for classification."
        }


@tool
def match_to_custom_category(merchant_name: str, description: str, amount: float) -> Dict[str, Any]:
    """
    Get custom category structure for AI reasoning to match a transaction.
    
    Use this tool AFTER checking if custom categories exist with get_custom_categories.
    This tool returns the custom category structure. The agent will use its LLM to reason
    about whether the transaction matches any custom category.
    
    Args:
        merchant_name: Merchant name from the transaction
        description: Transaction description
        amount: Transaction amount
        
    Returns:
        Dict with custom category structure and transaction details:
        {
            "has_custom_categories": True/False,
            "categories": {...},
            "category_structure": "Formatted text with categories",
            "transaction_details": {
                "merchant_name": str,
                "description": str,
                "amount": float
            },
            "message": "Instructions for matching"
        }
    
    Note: The agent will use its LLM to reason about whether the transaction matches
    any of the custom categories provided in the structure.
    """
    custom_categories_manager = get_custom_categories_manager()
    custom_categories = custom_categories_manager.get_categories()
    
    if not custom_categories:
        return {
            "has_custom_categories": False,
            "match": False,
            "message": "No custom categories defined. Use default taxonomy for classification.",
            "confidence": "NONE"
        }
    
    category_structure = custom_categories_manager.get_category_structure()
    
    return {
        "has_custom_categories": True,
        "categories": custom_categories,
        "category_structure": category_structure,
        "transaction_details": {
            "merchant_name": merchant_name,
            "description": description,
            "amount": amount
        },
        "message": f"Custom categories available. Use your AI reasoning to determine if this transaction matches any of the {len(custom_categories)} custom categories. If it matches, use that category/subcategory. If not, proceed to MCC categorization.",
        "instructions": "Review the category_structure above and reason about whether the transaction matches any custom category. If yes, use that category. If no, proceed to next classification method."
    }

