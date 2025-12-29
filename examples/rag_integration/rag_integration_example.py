# File: examples/rag_integration_example.py
"""
Example: Integrating ProvenanceAI with a RAG pipeline.
"""

from provenanceai import analyze
from provenanceai.integration.rag_adapters import RAGMetadataAdapter
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_rag_documents(file_paths):
    """Create RAG documents with provenance metadata."""
    documents = []
    
    for file_path in file_paths:
        # Analyze document for provenance
        report = analyze(file_path)
        
        # Load and split document content
        loader = TextLoader(str(file_path))
        raw_documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        chunks = text_splitter.split_documents(raw_documents)
        
        # Add provenance metadata to each chunk
        for chunk in chunks:
            chunk.metadata.update(
                RAGMetadataAdapter.for_langchain(report)
            )
            documents.append(chunk)
    
    return documents