"""Store User Preference Tool - Save user corrections to RAG system for Agno agents"""
from typing import Dict, Any, Optional
from agno.tools import tool
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.user_preferences import get_preferences_store


@tool
def store_user_preference(
    merchant_name: str,
    description: str,
    user_category: str,
    user_subcategory: str,
    original_category: Optional[str] = None,
    original_subcategory: Optional[str] = None,
    amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Store a user preference (correction) in the RAG system for future transaction classification.
    
    Use this tool when a user corrects a transaction classification. This saves the correction
    so that future similar transactions will automatically use the user's preferred category.
    
    This is a critical tool for learning from user feedback and improving classification accuracy.
    
    Args:
        merchant_name: Merchant name from the transaction (e.g., "STARBUCKS")
        description: Transaction description (e.g., "Starbucks Coffee Shop")
        user_category: User's preferred/corrected category (e.g., "Food & Dining")
        user_subcategory: User's preferred/corrected subcategory (e.g., "Restaurant")
        original_category: Original category before correction (optional, for tracking)
        original_subcategory: Original subcategory before correction (optional, for tracking)
        amount: Transaction amount (optional)
        
    Returns:
        Dict with storage result:
        {
            "stored": True,
            "preference_id": "abc123...",
            "message": "User preference stored successfully",
            "merchant_name": "STARBUCKS",
            "user_category": "Food & Dining",
            "user_subcategory": "Restaurant",
            "original_category": "Shopping",
            "original_subcategory": "Retail"
        }
        
    Example:
        When user corrects a transaction from "Shopping/Retail" to "Food & Dining/Restaurant",
        call this tool to save the preference. Future similar transactions will automatically
        use "Food & Dining/Restaurant" with HIGH confidence.
    """
    preferences_store = get_preferences_store()
    
    try:
        preference = preferences_store.add_preference(
            merchant_name=merchant_name,
            description=description,
            user_category=user_category,
            user_subcategory=user_subcategory,
            original_category=original_category,
            original_subcategory=original_subcategory,
            amount=amount
        )
        
        return {
            "stored": True,
            "preference_id": preference.get("id"),
            "message": f"User preference stored successfully. Future similar transactions will use '{user_category}' / '{user_subcategory}' with HIGH confidence.",
            "merchant_name": preference.get("merchant_name"),
            "user_category": preference.get("user_category"),
            "user_subcategory": preference.get("user_subcategory"),
            "original_category": preference.get("original_category"),
            "original_subcategory": preference.get("original_subcategory"),
            "created_at": preference.get("created_at")
        }
    except Exception as e:
        return {
            "stored": False,
            "message": f"Error storing user preference: {str(e)}",
            "error": str(e)
        }

