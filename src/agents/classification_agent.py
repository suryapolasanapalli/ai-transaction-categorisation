"""Classification Agent - Categorizes transactions using Agno framework with RAG"""
from typing import Dict, Any, Optional
from agno.agent import Agent, RunOutput
from utils.user_preferences import get_preferences_store
from utils.custom_categories import get_custom_categories_manager
from tools.user_preferences_tool import lookup_user_preference
from tools.custom_categories_tool import get_custom_categories, match_to_custom_category


class ClassificationAgent:
    """
    Enhanced Agno Agent responsible for transaction classification with RAG
    - Uses user preferences (RAG-based similarity search)
    - Supports custom categories with GenAI categorization
    - Falls back to MCC categorization
    - Default GenAI LLM categorization
    
    Priority Order:
    1. User Preferred Category (from feedback history via RAG)
    2. Custom Categories (with GenAI LLM categorization)
    3. MCC Categorization
    4. GenAI LLM Categorization (default)
    """
    
    def __init__(self, llm, tools: list):
        """
        Initialize the Enhanced Classification Agent with Agno and RAG
        
        Args:
            llm: Agno LLM instance (Azure OpenAI)
            tools: List of Agno tools (must include lookup_user_preference, get_custom_categories, 
                  match_to_custom_category, classify_by_mcc_code, lookup_mcc_by_vendor, 
                  vendor_database_search, get_taxonomy_structure)
        """
        self.llm = llm
        self.tools = tools
        self.agent_name = "ClassificationAgent"
        self.preferences_store = get_preferences_store()
        self.custom_categories_manager = get_custom_categories_manager()
        
        # Create Agno Agent with enhanced instructions
        self.agent = Agent(
            name="Transaction Classifier",
            id="classification-agent",
            model=llm,
            tools=tools,
            description="Expert at classifying financial transactions into categories with RAG and custom categories",
            instructions=[
                "You are an expert financial transaction classifier with RAG capabilities.",
                "Follow this priority order for classification:",
                "1. FIRST: Call lookup_user_preference tool with merchant_name and description. This checks if user has previously corrected similar transactions. If match=True, use that category/subcategory with HIGH confidence and STOP.",
                "2. SECOND: Call get_custom_categories tool to check if custom categories exist. If has_custom_categories=True, call match_to_custom_category tool which returns the category structure. Use your AI reasoning to determine if the transaction matches any custom category. If it matches, use that category/subcategory with HIGH confidence and STOP.",
                "3. THIRD: If MCC code is provided, use classify_by_mcc_code tool. This gives HIGH confidence.",
                "4. FOURTH: Use lookup_mcc_by_vendor tool for known brands (STARBUCKS, UBER, etc). This gives HIGH confidence.",
                "5. FIFTH: Search vendor_database_search tool for merchant patterns. This gives MEDIUM confidence.",
                "6. LAST: Use get_taxonomy_structure tool and reason about best fit. This gives MEDIUM/LOW confidence.",
                "Always consider: merchant name patterns, transaction types, typical amounts for categories.",
                "Assign confidence levels: HIGH (>90% - user preference/MCC/known vendor), MEDIUM (60-90% - database match/custom category), LOW (<60% - reasoning only).",
                "Provide clear reasoning that explains which tools were used and why you chose the category.",
                "Include CLASSIFICATION_METHOD in your response: user_preference_rag, custom_categories_genai, mcc_categorization, or genai_llm_default."
            ],
            markdown=False,
            add_history_to_context=True
        )
    
    def execute(self,
                merchant_name: str,
                description: str,
                amount: float,
                mcc_code: Optional[str] = None,
                metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute classification with RAG and priority order using Agno tools.
        The agent autonomously uses tools in priority order:
        1. User Preferred Category (RAG) - lookup_user_preference tool
        2. Custom Categories (GenAI) - get_custom_categories + match_to_custom_category tools
        3. MCC Categorization - classify_by_mcc_code tool
        4. GenAI LLM Categorization (default) - other tools
        
        Args:
            merchant_name: Merchant name from preprocessing
            description: Cleaned transaction description
            amount: Transaction amount
            mcc_code: Optional pre-provided MCC code
            metadata: Additional metadata from preprocessing
            
        Returns:
            Dict with classification results (category, subcategory, confidence, reasoning)
        """
        # Build classification prompt for Agno Agent
        # The agent will use tools autonomously based on instructions
        classification_prompt = f"""
Classify this financial transaction:

**Transaction Details:**
- Merchant: {merchant_name}
- Description: {description}
- Amount: ${amount:.2f}
{f"- **MCC Code: {mcc_code}** (Use classify_by_mcc_code tool with this!)" if mcc_code else "- MCC Code: Not provided"}
{f"- Location: {metadata.get('location')}" if metadata and metadata.get('location') else ""}
{f"- Transaction Type: {metadata.get('transaction_type')}" if metadata and metadata.get('transaction_type') else ""}

**Follow this priority order (use tools in this sequence):**

1. **FIRST:** Call lookup_user_preference tool with merchant_name="{merchant_name}" and description="{description}". 
   - If match found (match=True), use that category/subcategory with HIGH confidence.
   - If no match (match=False), proceed to step 2.

2. **SECOND:** Call get_custom_categories tool to check if custom categories exist.
   - If has_custom_categories=True, call match_to_custom_category tool with merchant_name, description, and amount.
   - If match found, use that category/subcategory with HIGH confidence.
   - If no match or no custom categories, proceed to step 3.

3. **THIRD:** If MCC code provided, call classify_by_mcc_code tool with mcc_code="{mcc_code}". This gives HIGH confidence.
   - If MCC not found, use lookup_mcc_by_vendor tool for known brands. This gives HIGH confidence.

4. **FOURTH:** If vendor not recognized, call vendor_database_search tool. This gives MEDIUM confidence.

5. **LAST:** Use get_taxonomy_structure tool to see valid categories and reason about best fit. This gives MEDIUM/LOW confidence.

**Important:** Use the tools in the exact order above. Stop and return result as soon as you get a match from steps 1-3.

**Respond in this exact format:**
CATEGORY: [category name]
SUBCATEGORY: [subcategory name]
CONFIDENCE: [HIGH/MEDIUM/LOW]
REASONING: [Your detailed reasoning - mention which tools were used and why]
CLASSIFICATION_METHOD: [user_preference_rag/custom_categories_genai/mcc_categorization/genai_llm_default]
"""
        
        try:
            # Run Agno Agent - it will use tools autonomously
            response: RunOutput = self.agent.run(classification_prompt)
            
            # Parse agent response
            result_text = response.content if hasattr(response, 'content') else str(response)
            
            # Extract structured data from response
            category = self._extract_field(result_text, "CATEGORY")
            subcategory = self._extract_field(result_text, "SUBCATEGORY")
            confidence = self._extract_field(result_text, "CONFIDENCE")
            agent_reasoning = self._extract_field(result_text, "REASONING")
            classification_method = self._extract_field(result_text, "CLASSIFICATION_METHOD")
            
            # Determine classification method from tool calls if not in response
            if not classification_method:
                # Check tool calls to determine method
                tool_calls_made = []
                if hasattr(response, 'messages'):
                    for msg in response.messages:
                        if hasattr(msg, 'role') and msg.role == 'tool':
                            tool_calls_made.append(msg.content if hasattr(msg, 'content') else str(msg))
                
                # Determine method from tool calls
                if any('lookup_user_preference' in str(tc) for tc in tool_calls_made):
                    # Check if match was found
                    for tc in tool_calls_made:
                        if isinstance(tc, dict) and tc.get('match'):
                            classification_method = "user_preference_rag"
                            break
                elif any('match_to_custom_category' in str(tc) or 'get_custom_categories' in str(tc) for tc in tool_calls_made):
                    classification_method = "custom_categories_genai"
                elif any('classify_by_mcc_code' in str(tc) or 'lookup_mcc_by_vendor' in str(tc) for tc in tool_calls_made):
                    classification_method = "mcc_categorization"
                else:
                    classification_method = "genai_llm_default"
            else:
                # Get tool calls for tracking
                tool_calls_made = []
                if hasattr(response, 'messages'):
                    for msg in response.messages:
                        if hasattr(msg, 'role') and msg.role == 'tool':
                            tool_calls_made.append(msg.content if hasattr(msg, 'content') else str(msg))
            
            # Extract user preference match info if RAG was used
            user_preference_match = None
            if classification_method == "user_preference_rag":
                for tc in tool_calls_made:
                    if isinstance(tc, dict) and tc.get('match'):
                        user_preference_match = {
                            "similarity_score": tc.get('similarity_score', 0),
                            "preference_id": tc.get('preference_id'),
                            "original_category": tc.get('original_category'),
                            "original_subcategory": tc.get('original_subcategory')
                        }
                        break
            
            return {
                "category": category or "Other",
                "subcategory": subcategory or "General",
                "confidence": confidence.lower() if confidence else "medium",
                "reasoning": agent_reasoning or result_text,
                "raw_response": result_text,
                "tool_calls": tool_calls_made,
                "agent_used": "Classification Agent (Agno)",
                "classification_method": classification_method or "genai_llm_default",
                "user_preference_match": user_preference_match,
                "metadata": {
                    "merchant_analyzed": merchant_name,
                    "amount_analyzed": amount,
                    "mcc_provided": bool(mcc_code)
                }
            }
            
        except Exception as e:
            # Fallback if Agno agent fails
            return {
                "category": "Other",
                "subcategory": "General",
                "confidence": "low",
                "reasoning": f"Classification failed: {str(e)}",
                "error": str(e),
                "agent_used": "Classification Agent (Failed)",
                "classification_method": "error"
            }
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Extract a field value from the agent response
        
        Args:
            text: Agent response text
            field_name: Field to extract (e.g., "CATEGORY", "CONFIDENCE")
            
        Returns:
            Extracted value or None
        """
        import re
        pattern = rf"{field_name}:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
