"""
AGENTIC AI ARCHITECTURE OVERVIEW
================================

This system implements a Multi-Agent Architecture where specialized AI agents
collaborate to process financial transactions. Each agent has distinct
responsibilities, tools, and expertise.

AGENT HIERARCHY:
---------------

┌─────────────────────────────────────────────────────────────┐
│                    TransactionOrchestrator                   │
│         (Coordinates workflow between agents)                │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Preprocessing │   │Classification │   │  Governance   │
│     Agent     │   │     Agent     │   │     Agent     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
  Extract Data      Categorize           Validate & Audit
  Clean Text        Assign Category      Assign MCC Codes
  Parse Metadata    Calculate Confidence Check Compliance


AGENT DETAILS:
-------------

1. PreprocessingAgent
   - Role: Data extraction and normalization
   - Inputs: Raw transaction description, amount
   - Tools: NLP parsing, pattern recognition
   - Outputs: Merchant name, location, cleaned description, metadata
   - Temperature: 1.0 (creative for entity extraction)

2. ClassificationAgent
   - Role: Transaction categorization
   - Inputs: Preprocessed data, merchant info
   - Tools: Vendor database lookup, taxonomy validation
   - Outputs: Category, subcategory, confidence, reasoning
   - Temperature: 1.0 (balanced for classification)

3. GovernanceAgent
   - Role: Validation, auditing, and compliance
   - Inputs: Preprocessing + Classification results
   - Tools: MCC code database, validation rules
   - Outputs: MCC code, validation status, flags, audit notes
   - Temperature: 1 (conservative for governance)


WORKFLOW EXECUTION:
------------------

Step 1: Transaction Input
        ↓
Step 2: PreprocessingAgent.execute()
        → Extracts merchant name
        → Cleans description
        → Identifies location and type
        ↓
Step 3: ClassificationAgent.execute()
        → Uses vendor database tool
        → Applies taxonomy rules
        → Assigns category and confidence
        ↓
Step 4: GovernanceAgent.execute()
        → Validates classification
        → Determines MCC code
        → Performs compliance checks
        → Generates audit trail
        ↓
Step 5: Final Result with Complete Workflow Log


AGENT AUTONOMY:
--------------

Each agent operates autonomously with:
- Independent LLM calls via BaseAgent._call_llm()
- Specialized system prompts defining their role
- Access to domain-specific tools and knowledge
- Ability to reason and make decisions
- Structured output format for downstream agents


TOOLS & KNOWLEDGE:
-----------------

PreprocessingAgent:
  - Pattern matching for merchant extraction
  - Location parsing algorithms
  - Transaction type classification

ClassificationAgent:
  - Vendor database (40+ known merchants)
  - Transaction taxonomy (12 categories)
  - Historical pattern matching

GovernanceAgent:
  - MCC code database (40+ codes)
  - Validation rules engine
  - Compliance checking framework


BENEFITS OF THIS ARCHITECTURE:
-----------------------------

1. Separation of Concerns
   - Each agent focuses on specific expertise
   - Easier to debug and improve individual agents

2. Modularity
   - Can swap out agents independently
   - Easy to add new agents to the pipeline

3. Transparency
   - Complete workflow logging
   - Visibility into each agent's decisions

4. Scalability
   - Parallel execution possible (future)
   - Can handle complex multi-step workflows

5. Maintainability
   - Clear responsibilities
   - Self-contained agent logic
"""
