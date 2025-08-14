"""
Multi-Model Agents Implementation using LlamaIndex
Core agent classes for the legal RAG system
"""

import json
import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.azuresearch import AzureSearch
from llama_index.agent.openai import OpenAIAgent
from llama_index.tools import QueryEngineTool, ToolMetadata

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import openai

from .agent_config import AGENT_CONFIGS, AgentType, OPTIMIZATION_METRICS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingOptimizer:
    """PyTorch-based embedding optimization for legal domain"""
    
    def __init__(self, model_name: str = "text-embedding-3-large"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.legal_vocab_weights = None
        
    def initialize_optimizer(self):
        """Initialize PyTorch components for embedding optimization"""
        try:
            # Load base embedding model
            self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.model.to(self.device)
            
            # Legal domain vocabulary weights
            self.legal_vocab_weights = self._create_legal_vocab_weights()
            logger.info("Embedding optimizer initialized with PyTorch")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding optimizer: {e}")
            
    def _create_legal_vocab_weights(self) -> torch.Tensor:
        """Create domain-specific weights for legal vocabulary"""
        legal_terms = [
            "statute", "regulation", "precedent", "jurisdiction", "immigration",
            "visa", "citizenship", "deportation", "asylum", "refugee",
            "constitutional", "amendment", "supreme court", "circuit court",
            "CFR", "USC", "INA", "USCIS", "DHS", "ICE"
        ]
        
        # Create weight tensor for legal term boosting
        vocab_size = self.tokenizer.vocab_size if self.tokenizer else 30522
        weights = torch.ones(vocab_size, device=self.device)
        
        # Boost legal terms (simplified - in practice, use proper token mapping)
        for term in legal_terms:
            if self.tokenizer:
                token_ids = self.tokenizer.encode(term, add_special_tokens=False)
                for token_id in token_ids:
                    if token_id < vocab_size:
                        weights[token_id] *= 1.5  # 50% boost for legal terms
        
        return weights
    
    def optimize_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate optimized embeddings for legal texts"""
        try:
            optimized_embeddings = []
            
            for text in texts:
                # Standard OpenAI embedding
                response = openai.Embedding.create(
                    input=text,
                    model="text-embedding-3-large"
                )
                base_embedding = response["data"][0]["embedding"]
                
                # Apply legal domain optimization
                optimized_embedding = self._apply_legal_optimization(base_embedding, text)
                optimized_embeddings.append(optimized_embedding)
            
            return optimized_embeddings
            
        except Exception as e:
            logger.error(f"Embedding optimization failed: {e}")
            return []
    
    def _apply_legal_optimization(self, embedding: List[float], text: str) -> List[float]:
        """Apply legal domain-specific optimizations to embeddings"""
        # Convert to tensor
        emb_tensor = torch.tensor(embedding, device=self.device)
        
        # Legal term detection and boosting
        legal_score = self._calculate_legal_score(text)
        
        # Apply domain-specific transformation
        if legal_score > 0.3:  # Text contains significant legal content
            # Boost embedding dimensions related to legal concepts
            emb_tensor = emb_tensor * (1.0 + legal_score * 0.2)
        
        return emb_tensor.cpu().tolist()
    
    def _calculate_legal_score(self, text: str) -> float:
        """Calculate how legal-domain-specific the text is"""
        legal_indicators = [
            "statute", "regulation", "case law", "precedent", "court",
            "immigration", "visa", "citizenship", "constitutional",
            "USC", "CFR", "INA", "USCIS"
        ]
        
        text_lower = text.lower()
        score = sum(1 for indicator in legal_indicators if indicator in text_lower)
        return min(score / len(legal_indicators), 1.0)

class LegalQueryRouter:
    """Specialized agent for routing and analyzing legal queries"""
    
    def __init__(self):
        self.config = AGENT_CONFIGS[AgentType.QUERY_ROUTER]
        self.llm = OpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    async def route_query(self, query: str) -> Dict[str, Any]:
        """Analyze and route the legal query"""
        routing_prompt = f"""
        {self.config.system_prompt}
        
        Query: {query}
        
        Provide routing decision in JSON format:
        {{
            "legal_domain": "immigration/constitutional/regulatory/civil/criminal",
            "complexity": "simple/intermediate/complex",
            "required_authorities": ["statutes", "cases", "regulations"],
            "retrieval_strategy": "semantic/hybrid/citation_based",
            "priority_sources": ["primary", "secondary"],
            "estimated_confidence": 0.0-1.0
        }}
        """
        
        try:
            response = await self.llm.acomplete(routing_prompt)
            # Parse JSON response (simplified)
            parsed_response = json.loads(response.text)
            return parsed_response
        except Exception as e:
            logger.error(f"Query routing failed: {e}")
            return {"error": str(e)}

class EnhancedDocumentRetriever:
    """Advanced document retrieval with Azure AI Search optimization"""
    
    def __init__(self, azure_endpoint: str, azure_key: str, index_name: str):
        self.config = AGENT_CONFIGS[AgentType.DOCUMENT_RETRIEVAL]
        self.search_client = SearchClient(
            endpoint=azure_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(azure_key)
        )
        self.embedding_optimizer = EmbeddingOptimizer()
        self.embedding_optimizer.initialize_optimizer()
        
    async def retrieve_documents(self, query: str, routing_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced document retrieval with optimization"""
        try:
            # Generate optimized query embedding
            optimized_embeddings = self.embedding_optimizer.optimize_embeddings([query])
            query_embedding = optimized_embeddings[0] if optimized_embeddings else None
            
            # Multi-strategy retrieval
            semantic_results = await self._semantic_search(query, query_embedding)
            keyword_results = await self._keyword_search(query)
            citation_results = await self._citation_search(query)
            
            # Combine and rerank results
            combined_results = self._combine_and_rerank(
                semantic_results, keyword_results, citation_results, routing_info
            )
            
            return combined_results[:10]  # Top 10 results
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return []
    
    async def _semantic_search(self, query: str, query_embedding: Optional[List[float]]) -> List[Dict[str, Any]]:
        """Semantic search using optimized embeddings"""
        if not query_embedding:
            return []
            
        try:
            # Vector search in Azure AI Search
            search_results = self.search_client.search(
                search_text=query,
                vector_queries=[{
                    "vector": query_embedding,
                    "k_nearest_neighbors": 20,
                    "fields": "embedding"
                }],
                select=["content", "title", "source", "legal_domain"],
                top=20
            )
            
            return [
                {
                    "content": doc["content"],
                    "title": doc.get("title", ""),
                    "source": doc.get("source", ""),
                    "score": doc.get("@search.score", 0.0),
                    "retrieval_method": "semantic"
                }
                for doc in search_results
            ]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """Traditional keyword search"""
        try:
            search_results = self.search_client.search(
                search_text=query,
                search_mode="all",
                select=["content", "title", "source"],
                top=15
            )
            
            return [
                {
                    "content": doc["content"],
                    "title": doc.get("title", ""),
                    "source": doc.get("source", ""),
                    "score": doc.get("@search.score", 0.0),
                    "retrieval_method": "keyword"
                }
                for doc in search_results
            ]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    async def _citation_search(self, query: str) -> List[Dict[str, Any]]:
        """Search for specific legal citations"""
        citation_patterns = [
            r'\d+\s+U\.S\.C\.\s+§?\s*\d+',  # USC citations
            r'\d+\s+C\.F\.R\.\s+§?\s*\d+',   # CFR citations
            r'\d+\s+F\.\d+\s+\d+',           # Federal Reporter
        ]
        
        # Extract potential citations from query
        import re
        citations = []
        for pattern in citation_patterns:
            citations.extend(re.findall(pattern, query, re.IGNORECASE))
        
        if not citations:
            return []
        
        try:
            # Search for documents containing these citations
            citation_query = " OR ".join(citations)
            search_results = self.search_client.search(
                search_text=citation_query,
                search_fields=["content"],
                select=["content", "title", "source"],
                top=10
            )
            
            return [
                {
                    "content": doc["content"],
                    "title": doc.get("title", ""),
                    "source": doc.get("source", ""),
                    "score": doc.get("@search.score", 0.0),
                    "retrieval_method": "citation"
                }
                for doc in search_results
            ]
            
        except Exception as e:
            logger.error(f"Citation search failed: {e}")
            return []
    
    def _combine_and_rerank(self, *result_sets, routing_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine multiple result sets and rerank based on legal relevance"""
        all_results = []
        for results in result_sets:
            all_results.extend(results)
        
        # Remove duplicates and rerank
        unique_results = {}
        for result in all_results:
            content_hash = hash(result["content"][:100])  # Simple deduplication
            if content_hash not in unique_results:
                unique_results[content_hash] = result
            else:
                # Boost score if found in multiple retrieval methods
                unique_results[content_hash]["score"] += result["score"] * 0.1
        
        # Sort by enhanced score
        ranked_results = sorted(
            unique_results.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        return ranked_results

class LegalContextSynthesizer:
    """Agent for synthesizing legal context from retrieved documents"""
    
    def __init__(self):
        self.config = AGENT_CONFIGS[AgentType.CONTEXT_SYNTHESIS]
        self.llm = OpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    async def synthesize_context(self, documents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Synthesize retrieved documents into coherent legal context"""
        try:
            # Organize documents by source type and relevance
            organized_docs = self._organize_documents(documents)
            
            # Create synthesis prompt
            synthesis_prompt = f"""
            {self.config.system_prompt}
            
            Query: {query}
            
            Documents to synthesize:
            {self._format_documents_for_synthesis(organized_docs)}
            
            Provide synthesized context focusing on:
            1. Primary legal authorities
            2. Key legal principles
            3. Relevant precedents
            4. Current regulatory framework
            """
            
            response = await self.llm.acomplete(synthesis_prompt)
            
            return {
                "synthesized_context": response.text,
                "primary_sources": organized_docs.get("primary", []),
                "secondary_sources": organized_docs.get("secondary", []),
                "confidence_score": self._calculate_synthesis_confidence(documents)
            }
            
        except Exception as e:
            logger.error(f"Context synthesis failed: {e}")
            return {"error": str(e)}
    
    def _organize_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize documents by legal hierarchy"""
        organized = {"primary": [], "secondary": [], "other": []}
        
        for doc in documents:
            content = doc.get("content", "").lower()
            title = doc.get("title", "").lower()
            
            # Classify document type
            if any(term in content or term in title for term in ["usc", "cfr", "statute", "regulation"]):
                organized["primary"].append(doc)
            elif any(term in content or term in title for term in ["case", "court", "decision"]):
                organized["primary"].append(doc)
            else:
                organized["secondary"].append(doc)
        
        return organized
    
    def _format_documents_for_synthesis(self, organized_docs: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format documents for the synthesis prompt"""
        formatted = ""
        
        for category, docs in organized_docs.items():
            if docs:
                formatted += f"\n{category.upper()} SOURCES:\n"
                for i, doc in enumerate(docs[:3]):  # Limit to top 3 per category
                    formatted += f"{i+1}. {doc.get('title', 'Untitled')}\n"
                    formatted += f"   Content: {doc.get('content', '')[:500]}...\n\n"
        
        return formatted
    
    def _calculate_synthesis_confidence(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the synthesized context"""
        if not documents:
            return 0.0
        
        # Base confidence on number and quality of sources
        primary_sources = sum(1 for doc in documents if "primary" in doc.get("source", "").lower())
        avg_score = sum(doc.get("score", 0.0) for doc in documents) / len(documents)
        
        confidence = min((primary_sources * 0.2 + avg_score * 0.8), 1.0)
        return confidence

class LegalResponseGenerator:
    """Final response generation agent"""
    
    def __init__(self):
        self.config = AGENT_CONFIGS[AgentType.RESPONSE_GENERATION]
        self.llm = OpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    async def generate_response(self, 
                              query: str, 
                              synthesized_context: Dict[str, Any],
                              routing_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final legal response"""
        try:
            response_prompt = f"""
            {self.config.system_prompt}
            
            Client Query: {query}
            
            Legal Context: {synthesized_context.get('synthesized_context', '')}
            
            Domain: {routing_info.get('legal_domain', 'general')}
            Complexity: {routing_info.get('complexity', 'intermediate')}
            
            Generate a comprehensive response that:
            1. Directly answers the query
            2. Cites relevant legal authorities
            3. Explains applicable legal principles
            4. Provides practical guidance
            5. Notes any limitations or disclaimers
            """
            
            response = await self.llm.acomplete(response_prompt)
            
            return {
                "answer": response.text,
                "sources": synthesized_context.get("primary_sources", []),
                "confidence": synthesized_context.get("confidence_score", 0.0),
                "legal_domain": routing_info.get("legal_domain"),
                "response_quality_score": self._calculate_response_quality(response.text)
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_response_quality(self, response: str) -> float:
        """Calculate response quality score"""
        quality_indicators = [
            len(response) > 200,  # Adequate length
            "pursuant to" in response.lower(),  # Legal language
            any(cite in response for cite in ["U.S.C.", "C.F.R.", "§"]),  # Citations
            "however" in response.lower() or "although" in response.lower(),  # Nuanced analysis
        ]
        
        return sum(quality_indicators) / len(quality_indicators)
