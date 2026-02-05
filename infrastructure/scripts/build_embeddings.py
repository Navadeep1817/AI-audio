#!/usr/bin/env python3
"""
build_embeddings.py — Build FAISS vector index from knowledge base documents

This script must be run BEFORE starting the backend server for the first time.

Prerequisites:
  1. AWS credentials configured in backend/.env
  2. AWS Bedrock Titan Embeddings model access approved
  3. Knowledge base documents present in data/knowledge_base/

Usage:
  cd backend
  python ../infrastructure/scripts/build_embeddings.py

The script will:
  1. Load all .txt files from data/knowledge_base/
  2. Chunk documents using RecursiveCharacterTextSplitter
  3. Generate embeddings via AWS Bedrock (amazon.titan-embed-text-v1)
  4. Build a FAISS vector index
  5. Save the index to data/embeddings/faiss_index.pkl
  6. Run a test query to verify functionality
"""

import sys
import os
from pathlib import Path

# Add backend to Python path so we can import from app/
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.rag_service import RAGService
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Build and save FAISS index from knowledge base."""
    
    print("=" * 80)
    print("  AI SALES COACH — KNOWLEDGE BASE EMBEDDING BUILDER")
    print("=" * 80)
    print()
    
    logger.info("Initializing RAG service...")
    
    try:
        # Initialize RAG service (this will attempt to load existing index)
        rag_service = RAGService()
        
        # Force rebuild of index
        logger.info("Loading knowledge base documents...")
        documents = rag_service.load_knowledge_base_documents()
        
        if not documents:
            logger.error("❌ No documents found in knowledge base!")
            logger.error(f"   Expected location: {rag_service.settings.KNOWLEDGE_BASE_PATH}")
            logger.error("   Make sure .txt files exist in data/knowledge_base/")
            return 1
        
        logger.info(f"✓ Loaded {len(documents)} documents")
        print()
        
        # Show document inventory
        print("Documents found:")
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'unknown')
            word_count = len(doc.page_content.split())
            print(f"  {i}. {source:40s} ({word_count:,} words)")
        print()
        
        # Build index
        logger.info("Building FAISS vector index...")
        logger.info("⏳ This will take 2-5 minutes depending on document size...")
        print()
        
        vector_store = rag_service.build_vector_index(documents)
        
        logger.info("✓ Index built successfully")
        print()
        
        # Save to disk
        logger.info("Saving index to disk...")
        rag_service.save_index(vector_store)
        
        logger.info(f"✓ Index saved to: {rag_service.settings.FAISS_INDEX_PATH}")
        print()
        
        # Test query
        logger.info("Running test query to verify index...")
        test_query = "How do I handle price objections?"
        results = rag_service.retrieve_context(test_query, top_k=3)
        
        print("─" * 80)
        print(f"Test Query: '{test_query}'")
        print(f"Retrieved {len(results)} relevant chunks:")
        print()
        
        for i, result in enumerate(results, 1):
            category = result['metadata'].get('category', 'unknown')
            score = result['relevance_score']
            preview = result['content'][:200].replace('\n', ' ')
            
            print(f"  {i}. [{category}] (score: {score:.4f})")
            print(f"     {preview}...")
            print()
        
        print("─" * 80)
        print()
        
        # Success
        print("=" * 80)
        print("  ✓✓✓ EMBEDDING BUILD COMPLETE ✓✓✓")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Verify .env file has correct AWS credentials")
        print("  2. Start backend: cd backend && python -m app.main")
        print("  3. Start frontend: cd frontend && npm run dev")
        print()
        
        return 0
    
    except Exception as e:
        logger.error("=" * 80)
        logger.error("  ❌ EMBEDDING BUILD FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("  1. Check AWS credentials in backend/.env")
        logger.error("  2. Verify Bedrock Titan Embeddings access is approved")
        logger.error("  3. Ensure knowledge base documents exist in data/knowledge_base/")
        logger.error("  4. Check that boto3 and langchain packages are installed")
        logger.error("")
        
        import traceback
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        
        return 1


if __name__ == "__main__":
    sys.exit(main())      