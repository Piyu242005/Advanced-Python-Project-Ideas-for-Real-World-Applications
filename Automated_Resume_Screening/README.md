# Automated_Resume_Screening

Advanced AI-driven resume parsing and candidate ranking system utilizing Large Language Models (LLMs) and Vector Databases for semantic skill matching.

## Features
- **Semantic Search:** Uses vector embeddings (Pinecone/Milvus) to match candidates with job descriptions based on context rather than just keyword matching.
- **LLM Information Extraction:** Leverages fine-tuned transformer models (like RoBERTa or domain-specific LLMs) to accurately extract complex work history and education.
- **Bias Mitigation:** Implementing fair-AI checks and anonymization preprocessing to ensure equitable screening.
- **Scalable Architecture:** Built with modern async frameworks (FastAPI) and Celery for distributed document processing.
