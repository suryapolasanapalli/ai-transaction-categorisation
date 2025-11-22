"""Custom Categories Management - User-defined transaction categories"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class CustomCategoriesManager:
    """
    Manages user-defined custom categories for transaction classification.
    """
    
    def __init__(self, storage_path: str = "custom_categories.json"):
        """
        Initialize the custom categories manager.
        
        Args:
            storage_path: Path to JSON file for persistent storage
        """
        self.storage_path = storage_path
        self.custom_categories: Dict[str, List[str]] = {}
        self._load_categories()
    
    def _load_categories(self):
        """Load custom categories from storage file"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.custom_categories = data.get("categories", {})
            except Exception as e:
                print(f"Error loading custom categories: {e}")
                self.custom_categories = {}
        else:
            self.custom_categories = {}
    
    def _save_categories(self):
        """Save custom categories to storage file"""
        try:
            data = {
                "categories": self.custom_categories,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving custom categories: {e}")
    
    def add_category(self, category: str, subcategories: List[str]) -> bool:
        """
        Add a custom category with subcategories.
        
        Args:
            category: Category name
            subcategories: List of subcategory names
            
        Returns:
            True if added successfully
        """
        if not category or not subcategories:
            return False
        
        self.custom_categories[category] = subcategories
        self._save_categories()
        return True
    
    def remove_category(self, category: str) -> bool:
        """
        Remove a custom category.
        
        Args:
            category: Category name to remove
            
        Returns:
            True if removed successfully
        """
        if category in self.custom_categories:
            del self.custom_categories[category]
            self._save_categories()
            return True
        return False
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get all custom categories"""
        return self.custom_categories.copy()
    
    def has_categories(self) -> bool:
        """Check if any custom categories exist"""
        return len(self.custom_categories) > 0
    
    def get_category_structure(self) -> str:
        """
        Get custom categories as formatted text for LLM prompts.
        
        Returns:
            Formatted string with categories and subcategories
        """
        if not self.custom_categories:
            return ""
        
        result = "CUSTOM CATEGORIES (User-Defined):\n\n"
        for category, subcategories in self.custom_categories.items():
            result += f"- {category}\n"
            for subcat in subcategories:
                result += f"  • {subcat}\n"
        return result


# Global instance
_custom_categories_manager: Optional[CustomCategoriesManager] = None


def get_custom_categories_manager() -> CustomCategoriesManager:
    """Get or create the global custom categories manager instance"""
    global _custom_categories_manager
    if _custom_categories_manager is None:
        _custom_categories_manager = CustomCategoriesManager()
    return _custom_categories_manager

