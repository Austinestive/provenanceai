# ProvenanceAI

**Knowledge Provenance & Trust Infrastructure for AI Systems**

ProvenanceAI is a Python library that provides a standard, explainable, machine-readable way for AI systems to understand the provenance, authority, trustworthiness, and permitted use of knowledge sources.

## Why ProvenanceAI?

Modern AI systems (RAG pipelines, agents, knowledge graphs) process vast amounts of information, but they lack standardized ways to:
- Understand **where information comes from**
- Assess **how trustworthy it is**
- Know **what they're allowed to do with it**
- **Explain** their trust decisions to users

ProvenanceAI solves this by providing a library-first, framework-agnostic solution that outputs provenance metadata optimized for AI consumption.

## Key Features

- **📄 Document Ingestion**: Support for PDF, DOCX, TXT with metadata extraction
- **🔍 Provenance Inference**: Heuristic + NER-based inference of authors, institutions, dates
- **📊 Trust Scoring**: Rule-based, explainable trust scores across multiple dimensions
- **⚖️ AI Usage Policy**: License-aware determination of what AI can do with content
- **🤖 AI-Optimized Output**: JSON metadata ready for RAG pipelines and vector databases
- **🔬 Standards-Inspired**: Based on library science principles (Dublin Core, PROV-O)

## Quick Start

```python
from provenanceai import analyze

# Analyze a document
report = analyze("research_paper.pdf")

# Get JSON output for your RAG pipeline
metadata = report.to_json()
print(metadata)

# Or access structured data
print(f"Trust Score: {report.trust.overall_score.score:.2f}")
print(f"Allowed AI Actions: {report.ai_use.allowed_actions}")
    