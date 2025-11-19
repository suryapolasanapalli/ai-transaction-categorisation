"""Governance Agent - Validates and audits classifications using Agno framework"""
from typing import Dict, Any, Optional
from agno.agent import Agent, RunOutput


class GovernanceAgent:
    """
    Agno Agent responsible for governance and validation
    - Validate classifications for accuracy and compliance
    - Assign/verify MCC codes
    - Generate audit trails
    - Flag compliance concerns
    - Produce final validated output
    """
    
    def __init__(self, llm, tools: list):
        """
        Initialize the Governance Agent with Agno
        
        Args:
            llm: Agno LLM instance (Azure OpenAI)
            tools: List of Agno tools (assign_mcc_code_for_category)
        """
        self.llm = llm
        self.tools = tools
        self.agent_name = "GovernanceAgent"
        
        # Create Agno Agent
        self.agent = Agent(
            name="Transaction Governance Auditor",
            id="governance-agent",
            model=llm,
            tools=tools,
            description="Financial compliance and audit specialist for transaction validation",
            instructions=[
                "You are a financial compliance and audit specialist.",
                "Your task is to validate transaction classifications and ensure accuracy and compliance.",
                "Follow this validation process:",
                "1. Review the classification results (category, subcategory, confidence).",
                "2. Verify if the category is appropriate for the merchant and transaction type.",
                "3. If MCC code is missing, use assign_mcc_code_for_category tool to assign it.",
                "4. If MCC code is provided, validate it matches the category.",
                "5. Evaluate if the confidence level is justified based on evidence.",
                "6. Check for any compliance concerns or red flags (unusual amounts, mismatches, etc.).",
                "7. Adjust confidence if needed based on validation.",
                "8. Provide clear audit notes explaining validation decisions.",
                "Always maintain objectivity and flag genuine concerns for review."
            ],
            markdown=False,
            add_history_to_context=True
        )
    
    def execute(self,
                merchant_name: str,
                description: str,
                amount: float,
                category: str,
                confidence: str,
                reasoning: str,
                subcategory: Optional[str] = None,
                mcc_code: Optional[str] = None,
                metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute governance and validation using Agno Agent
        
        Args:
            merchant_name: Merchant name
            description: Transaction description
            amount: Transaction amount
            category: Classified category
            confidence: Classification confidence
            reasoning: Classification reasoning
            subcategory: Specific subcategory
            mcc_code: Optional pre-provided MCC code
            metadata: Additional metadata
            
        Returns:
            Dict with complete validated transaction data
        """
        # Build governance validation prompt
        validation_prompt = f"""Review and validate this transaction classification.

**Transaction Details:**
- Merchant: {merchant_name}
- Description: {description}
- Amount: ${amount:.2f}

**Classification Results:**
- Category: {category}
- Subcategory: {subcategory or "General"}
- Confidence: {confidence.upper()}
- Reasoning: {reasoning}
{f"- MCC Code: {mcc_code} (provided by user)" if mcc_code else "- MCC Code: Not provided - use assign_mcc_code_for_category tool"}

**Your Validation Tasks:**
1. **Category Validation**: Is the category appropriate for this merchant/transaction?
2. **MCC Code Assignment**: {"Verify the provided MCC code matches the category" if mcc_code else "Use assign_mcc_code_for_category tool to assign the correct MCC code"}
3. **Confidence Assessment**: Is the confidence level justified? Should it be adjusted?
4. **Compliance Check**: Are there any concerns or flags? (e.g., unusual amount, category mismatch, suspicious patterns)

**Respond in this exact format:**
VALIDATION: [PASS/FAIL]
ADJUSTED_CONFIDENCE: [HIGH/MEDIUM/LOW]
MCC_CODE: [4-digit code]
MCC_DESCRIPTION: [description]
FLAGS: [any concerns or "none"]
AUDIT_NOTES: [detailed validation notes explaining your decisions]
"""
        
        try:
            # Run Agno Agent for validation
            response: RunOutput = self.agent.run(validation_prompt)
            
            # Parse agent response
            result_text = response.content if hasattr(response, 'content') else str(response)
            
            # Extract structured data from validation response
            validation_status = self._extract_field(result_text, "VALIDATION") or "PASS"
            adjusted_confidence = self._extract_field(result_text, "ADJUSTED_CONFIDENCE") or confidence
            final_mcc_code = self._extract_field(result_text, "MCC_CODE") or mcc_code or "5999"
            mcc_description = self._extract_field(result_text, "MCC_DESCRIPTION") or "Miscellaneous"
            flags_text = self._extract_field(result_text, "FLAGS") or "none"
            audit_notes = self._extract_field(result_text, "AUDIT_NOTES") or "Validation completed"
            
            # Parse flags
            flags = None
            if flags_text.lower() != "none":
                flags = [flag.strip() for flag in flags_text.split(",") if flag.strip()]
            
            # Get tool calls info if available
            tool_calls_made = []
            if hasattr(response, 'messages'):
                for msg in response.messages:
                    if hasattr(msg, 'role') and msg.role == 'tool':
                        tool_calls_made.append(msg.content if hasattr(msg, 'content') else str(msg))
            
            # Generate final structured output
            return {
                "merchant_name": merchant_name,
                "category": category,
                "subcategory": subcategory or "General",
                "mcc_code": final_mcc_code,
                "mcc_description": mcc_description,
                "confidence": adjusted_confidence.lower(),
                "reasoning": reasoning,
                "amount": amount,
                "validation_status": validation_status,
                "flags": flags,
                "audit_notes": audit_notes,
                "governance_response": result_text,
                "tool_calls": tool_calls_made,
                "metadata": metadata,
                "agent_used": "Agno Governance Agent",
                "status": "success"
            }
            
        except Exception as e:
            # Fallback if Agno agent fails
            return {
                "merchant_name": merchant_name,
                "category": category,
                "subcategory": subcategory or "General",
                "mcc_code": mcc_code or "5999",
                "mcc_description": "Miscellaneous",
                "confidence": confidence.lower(),
                "reasoning": reasoning,
                "amount": amount,
                "validation_status": "ERROR",
                "flags": [f"Validation failed: {str(e)}"],
                "audit_notes": f"Governance validation encountered an error: {str(e)}",
                "error": str(e),
                "metadata": metadata,
                "agent_used": "Agno Governance Agent (Failed)",
                "status": "error"
            }
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Extract a field value from the agent response
        
        Args:
            text: Agent response text
            field_name: Field to extract (e.g., "VALIDATION", "MCC_CODE")
            
        Returns:
            Extracted value or None
        """
        import re
        pattern = rf"{field_name}:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
