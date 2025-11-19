"""Parser utilities for agent responses"""
import json
import re
from typing import Dict, Any, Optional


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text that may contain other content
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Parsed JSON dict or None if not found
    """
    # Try to find JSON object in text
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None


def parse_agent_response(response: str) -> Dict[str, Any]:
    """
    Parse agent response into structured format
    
    Args:
        response: Raw agent response text
        
    Returns:
        Dict with parsed fields
    """
    result = {}
    
    # Try JSON extraction first
    json_data = extract_json_from_text(response)
    if json_data:
        return json_data
    
    # Fallback to line-by-line parsing
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            result[key] = value
    
    return result


def parse_key_value_pairs(text: str, keys: list) -> Dict[str, str]:
    """
    Parse specific key-value pairs from text
    
    Args:
        text: Text to parse
        keys: List of keys to look for
        
    Returns:
        Dict with found key-value pairs
    """
    result = {}
    
    for key in keys:
        # Look for pattern: KEY: value
        pattern = rf"{key}:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result[key.lower()] = match.group(1).strip()
    
    return result
