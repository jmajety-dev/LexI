"""
Multi-Model Agents Configuration
Defines specialized agents for the legal RAG system
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

class AgentType(Enum):
    QUERY_ROUTER = "query_router"
    DOCUMENT_RETRIEVAL = "document_retrieval" 
    LEGAL_ENTITY_EXTRACTION = "legal_entity_extraction"
    CITATION_VALIDATION = "citation_validation"
    CONTEXT_SYNTHESIS = "context_synthesis"
    RESPONSE_GENERATION = "response_generation"
    EMBEDDING_OPTIMIZATION = "embedding_optimization"

@dataclass
class AgentConfig:
    """Configuration for each specialized agent"""
    name: str
    model: str
    temperature: float
    max_tokens: int
    system_prompt: str
    tools: List[str]
    optimization_params: Dict[str, Any]

# Agent Configurations
AGENT_CONFIGS = {
    AgentType.QUERY_ROUTER: AgentConfig(
        name="Legal Query Router",
        model="gpt-4-turbo",
        temperature=0.1,
        max_tokens=150,
        system_prompt="""You are a specialized legal query router. Analyze the user's question and determine:
        1. Legal domain (immigration, constitutional, regulatory, etc.)
        2. Query complexity level (simple, intermediate, complex)
        3. Required legal authorities (statutes, cases, regulations)
        4. Retrieval strategy needed
        Return structured routing decision.""",
        tools=["legal_domain_classifier", "complexity_analyzer"],
        optimization_params={"fine_tuned": True, "domain_specific": True}
    ),
    
    AgentType.DOCUMENT_RETRIEVAL: AgentConfig(
        name="Enhanced Document Retrieval Agent",
        model="text-embedding-3-large",
        temperature=0.0,
        max_tokens=0,
        system_prompt="""Specialized retrieval agent optimized for legal documents.
        Use semantic similarity, legal citation matching, and contextual relevance scoring.""",
        tools=["azure_search", "semantic_search", "citation_matcher"],
        optimization_params={"embedding_model": "optimized", "reranking": True}
    ),
    
    AgentType.LEGAL_ENTITY_EXTRACTION: AgentConfig(
        name="Legal Entity Recognition Agent",
        model="gpt-3.5-turbo",
        temperature=0.0,
        max_tokens=300,
        system_prompt="""Extract legal entities from text: case names, statutes, regulations,
        court names, dates, legal concepts, and procedural terms. Maintain legal accuracy.""",
        tools=["spacy_legal_ner", "legal_regex_patterns"],
        optimization_params={"fine_tuned_ner": True, "legal_domain": True}
    ),
    
    AgentType.CITATION_VALIDATION: AgentConfig(
        name="Legal Citation Validator",
        model="gpt-3.5-turbo",
        temperature=0.0,
        max_tokens=200,
        system_prompt="""Validate legal citations for accuracy, format, and current status.
        Check if cases are still good law and regulations are current.""",
        tools=["westlaw_api", "legal_citation_checker"],
        optimization_params={"citation_database": True, "real_time_validation": True}
    ),
    
    AgentType.CONTEXT_SYNTHESIS: AgentConfig(
        name="Legal Context Synthesis Agent",
        model="gpt-4-turbo",
        temperature=0.2,
        max_tokens=800,
        system_prompt="""Synthesize retrieved legal documents into coherent context.
        Prioritize primary sources, resolve conflicts, and maintain legal hierarchy.""",
        tools=["legal_hierarchy_ranker", "conflict_resolver"],
        optimization_params={"context_optimization": True, "legal_reasoning": True}
    ),
    
    AgentType.RESPONSE_GENERATION: AgentConfig(
        name="Legal Response Generator",
        model="gpt-4-turbo",
        temperature=0.3,
        max_tokens=1200,
        system_prompt="""Generate comprehensive legal responses with proper citations.
        Maintain professional tone, cite sources accurately, and provide actionable guidance.""",
        tools=["legal_writer", "citation_formatter"],
        optimization_params={"fine_tuned_legal": True, "response_optimization": True}
    ),
    
    AgentType.EMBEDDING_OPTIMIZATION: AgentConfig(
        name="Embedding Optimization Agent",
        model="text-embedding-3-large",
        temperature=0.0,
        max_tokens=0,
        system_prompt="""Optimize embeddings for legal domain through fine-tuning and
        domain-specific preprocessing.""",
        tools=["pytorch_optimizer", "embedding_fine_tuner"],
        optimization_params={"continuous_learning": True, "domain_adaptation": True}
    )
}

# Agent Workflow Configuration
AGENT_WORKFLOW = {
    "query_processing": [
        AgentType.QUERY_ROUTER,
        AgentType.EMBEDDING_OPTIMIZATION
    ],
    "retrieval_phase": [
        AgentType.DOCUMENT_RETRIEVAL,
        AgentType.LEGAL_ENTITY_EXTRACTION
    ],
    "validation_phase": [
        AgentType.CITATION_VALIDATION
    ],
    "synthesis_phase": [
        AgentType.CONTEXT_SYNTHESIS
    ],
    "generation_phase": [
        AgentType.RESPONSE_GENERATION
    ]
}

# Performance Metrics for 70% Improvement
OPTIMIZATION_METRICS = {
    "embedding_similarity_threshold": 0.85,
    "context_relevance_score": 0.80,
    "citation_accuracy_rate": 0.95,
    "response_coherence_score": 0.88,
    "domain_specificity_boost": 0.70
}
