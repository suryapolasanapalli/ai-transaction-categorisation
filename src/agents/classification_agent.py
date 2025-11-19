"""Classification Agent - Categorizes transactions using Agno framework"""
from typing import Dict, Any, Optional
from agno.agent import Agent, RunOutput


class ClassificationAgent:
    """
    Agno Agent responsible for transaction classification
    - Categorize transactions using AI reasoning
    - Assign confidence scores based on evidence
    - Use vendor database and taxonomy tools
    - Provide clear reasoning for classifications
    """
    
    def __init__(self, llm, tools: list):
        """
        Initialize the Classification Agent with Agno
        
        Args:
            llm: Agno LLM instance (Azure OpenAI)
            tools: List of Agno tools (vendor_database_search, get_taxonomy_structure)
        """
        self.llm = llm
        self.tools = tools
        self.agent_name = "ClassificationAgent"
        
        # Create Agno Agent
        self.agent = Agent(
            name="Transaction Classifier",
            id="classification-agent",
            model=llm,
            tools=tools,
            description="Expert at classifying financial transactions into categories",
            instructions=[
                "You are an expert financial transaction classifier.",
                "Follow this priority order for classification:",
                "1. HIGHEST PRIORITY: If MCC code is provided, use classify_by_mcc_code tool first. This gives HIGH confidence.",
                "2. If no MCC code provided, use lookup_mcc_by_vendor tool to check if merchant is a known brand (STARBUCKS, UBER, etc). This also gives HIGH confidence.",
                "3. If MCC not found and vendor not recognized, search vendor_database_search tool for merchant patterns.",
                "4. If still not found, use get_taxonomy_structure tool to see valid categories and reason about best fit.",
                "5. Then reason about the transaction (merchant name, description, amount) to assign best category.",
                "Always consider: merchant name patterns, transaction types, typical amounts for categories.",
                "Assign confidence levels: HIGH (>90% - from MCC or known vendor), MEDIUM (60-90% - database match), LOW (<60% - reasoning only).",
                "Provide clear reasoning that explains which tools were used and why you chose the category."
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
        Execute classification on transaction data using Agno Agent
        
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
        classification_prompt = f"""
Classify this financial transaction:

**Transaction Details:**
- Merchant: {merchant_name}
- Description: {description}
- Amount: ${amount:.2f}
{f"- **MCC Code: {mcc_code}** (PRIORITY: Use classify_by_mcc_code tool with this!)" if mcc_code else "- MCC Code: Not provided"}
{f"- Location: {metadata.get('location')}" if metadata and metadata.get('location') else ""}
{f"- Transaction Type: {metadata.get('transaction_type')}" if metadata and metadata.get('transaction_type') else ""}

**Classification Priority:**
{f"1. FIRST: Call classify_by_mcc_code with MCC code '{mcc_code}' - this gives HIGH confidence!" if mcc_code else "1. No MCC code provided, skip to step 2"}
2. If MCC not found or unavailable, call vendor_database_search to check for known merchant
3. If not found, call get_taxonomy_structure to see valid categories and reason about best fit
4. Assign confidence: HIGH (MCC/database match), MEDIUM (reasoning), LOW (uncertain)

**Respond in this exact format:**
CATEGORY: [category name]
SUBCATEGORY: [subcategory name]
CONFIDENCE: [HIGH/MEDIUM/LOW]
REASONING: [Your detailed reasoning - mention which tools were used and why]
"""
        
        try:
            # Run Agno Agent
            response: RunOutput = self.agent.run(classification_prompt)
            
            # Parse agent response
            result_text = response.content if hasattr(response, 'content') else str(response)
            
            # Extract structured data from response
            category = self._extract_field(result_text, "CATEGORY")
            subcategory = self._extract_field(result_text, "SUBCATEGORY")
            confidence = self._extract_field(result_text, "CONFIDENCE")
            reasoning = self._extract_field(result_text, "REASONING")
            
            # Get tool calls info if available
            tool_calls_made = []
            if hasattr(response, 'messages'):
                for msg in response.messages:
                    if hasattr(msg, 'role') and msg.role == 'tool':
                        tool_calls_made.append(msg.content if hasattr(msg, 'content') else str(msg))
            
            return {
                "category": category or "Other",
                "subcategory": subcategory or "General",
                "confidence": confidence.lower() if confidence else "medium",
                "reasoning": reasoning or result_text,
                "raw_response": result_text,
                "tool_calls": tool_calls_made,
                "agent_used": "Agno Classification Agent",
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
                "agent_used": "Agno Classification Agent (Failed)"
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
