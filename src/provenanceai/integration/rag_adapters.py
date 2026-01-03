"""
RAG Integration Adapters for ProvenanceAI.

This module provides adapters for integrating ProvenanceAI with popular RAG frameworks.
"""
from typing import Any, Dict

try:
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from llama_index.core.schema import Document as LlamaDocument
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False


class LangChainAdapter:
    """Adapter for LangChain integration."""
    
    def __init__(self, provenance_tracker):
        """Initialize the LangChain adapter.
        
        Args:
            provenance_tracker: ProvenanceAI tracker instance
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not installed. Install with: pip install langchain")
        self.tracker = provenance_tracker
    
    def track_document(self, document: 'Document', source_info: Dict[str, Any] = None):
        """Track a LangChain document.
        
        Args:
            document: LangChain Document instance
            source_info: Additional source information
        """
        metadata = {
            'content': document.page_content,
            'metadata': document.metadata,
            **(source_info or {})
        }
        self.tracker.track_source('langchain_document', metadata)
    
    def track_retrieval(self, query: str, documents: list, retriever_info: Dict[str, Any] = None):
        """Track a retrieval operation.
        
        Args:
            query: The query string
            documents: List of retrieved documents
            retriever_info: Information about the retriever
        """
        self.tracker.track_operation('retrieval', {
            'query': query,
            'num_results': len(documents),
            'retriever': retriever_info or {}
        })
        
        for doc in documents:
            self.track_document(doc)


class LlamaIndexAdapter:
    """Adapter for LlamaIndex integration."""
    
    def __init__(self, provenance_tracker):
        """Initialize the LlamaIndex adapter.
        
        Args:
            provenance_tracker: ProvenanceAI tracker instance
        """
        if not LLAMAINDEX_AVAILABLE:
            raise ImportError("LlamaIndex is not installed. Install with: pip install llama-index")
        self.tracker = provenance_tracker
    
    def track_document(self, document: 'LlamaDocument', source_info: Dict[str, Any] = None):
        """Track a LlamaIndex document.
        
        Args:
            document: LlamaIndex Document instance
            source_info: Additional source information
        """
        metadata = {
            'content': document.text,
            'metadata': document.metadata,
            'doc_id': document.doc_id,
            **(source_info or {})
        }
        self.tracker.track_source('llamaindex_document', metadata)
    
    def track_query(self, query: str, response, engine_info: Dict[str, Any] = None):
        """Track a query operation.
        
        Args:
            query: The query string
            response: The response object
            engine_info: Information about the query engine
        """
        self.tracker.track_operation('query', {
            'query': query,
            'response': str(response),
            'engine': engine_info or {}
        })
        
        # Track source documents if available
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                if hasattr(node, 'node'):
                    self.track_document(LlamaDocument(
                        text=node.node.text,
                        metadata=node.node.metadata
                    ))
