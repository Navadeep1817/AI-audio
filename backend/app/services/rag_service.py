import os
from typing import List, Dict

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

import boto3

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RAGService:
    """
    Retrieval-Augmented Generation service for sales coaching knowledge.
    """

    def __init__(self):
        self.settings = settings

        # ✅ USE DEFAULT AWS CREDENTIAL CHAIN (DO NOT PASS KEYS)
        self.embeddings = BedrockEmbeddings(
            client=boto3.client(
                "bedrock-runtime",
                region_name=settings.AWS_REGION
            ),
            model_id=settings.BEDROCK_EMBEDDING_MODEL,
        )

        self.vector_store = None
        self.load_or_create_index()

    # ==========================================================
    # PATH HELPERS
    # ==========================================================
    def get_project_root(self):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../")
        )

    def resolve_path(self, relative_path: str):
        return os.path.join(self.get_project_root(), relative_path)

    # ==========================================================
    # KNOWLEDGE BASE LOADING
    # ==========================================================
    def load_knowledge_base_documents(self) -> List[Document]:
        documents = []
        kb_path = self.resolve_path(settings.KNOWLEDGE_BASE_PATH)

        if not os.path.exists(kb_path):
            logger.warning(f"Knowledge base path not found: {kb_path}")
            return documents

        for filename in os.listdir(kb_path):
            if filename.endswith(".txt"):
                filepath = os.path.join(kb_path, filename)

                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": filename,
                        "category": filename.replace(".txt", "")
                    },
                )

                documents.append(doc)
                logger.info(f"Loaded document: {filename}")

        return documents

    # ==========================================================
    # CHUNK DOCUMENTS
    # ==========================================================
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )

        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks

    # ==========================================================
    # BUILD VECTOR INDEX
    # ==========================================================
    def build_vector_index(self, documents: List[Document]) -> FAISS:
        chunks = self.chunk_documents(documents)

        logger.info("Building FAISS index...")
        vector_store = FAISS.from_documents(chunks, self.embeddings)
        logger.info("FAISS index built successfully")

        return vector_store

    # ==========================================================
    # SAVE / LOAD INDEX (🔥 FIXED — NO PICKLE)
    # ==========================================================
    def save_index(self, vector_store: FAISS):
        index_dir = self.resolve_path("backend/data/embeddings")

        os.makedirs(index_dir, exist_ok=True)

        vector_store.save_local(index_dir)

        logger.info(f"Saved FAISS index to {index_dir}")

    def load_index(self) -> FAISS:
        index_dir = self.resolve_path("backend/data/embeddings")

        vector_store = FAISS.load_local(
    index_dir,
    self.embeddings
)


        logger.info(f"Loaded FAISS index from {index_dir}")
        return vector_store

    # ==========================================================
    # INDEX MANAGEMENT
    # ==========================================================
    def load_or_create_index(self):
        index_dir = self.resolve_path("backend/data/embeddings")

        if os.path.exists(index_dir):
            try:
                self.vector_store = self.load_index()
            except Exception as e:
                logger.error(f"Error loading index: {e}. Creating new index...")
                self.create_new_index()
        else:
            self.create_new_index()

    def create_new_index(self):
        documents = self.load_knowledge_base_documents()

        if not documents:
            logger.warning("No documents found. Creating empty index.")

            self.vector_store = FAISS.from_texts(
                ["Sales coaching knowledge base placeholder"],
                self.embeddings,
            )
        else:
            self.vector_store = self.build_vector_index(documents)
            self.save_index(self.vector_store)

    # ==========================================================
    # RETRIEVE CONTEXT
    # ==========================================================
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict]:
        if top_k is None:
            top_k = settings.TOP_K_RESULTS

        results = self.vector_store.similarity_search_with_score(query, k=top_k)

        context_docs = []
        for doc, score in results:
            context_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score),
            })

        logger.info(f"Retrieved {len(context_docs)} context documents for query")
        return context_docs

    def format_context_for_prompt(self, context_docs: List[Dict]) -> str:
        formatted_context = "# SALES COACHING KNOWLEDGE BASE\n\n"

        for i, doc in enumerate(context_docs, 1):
            category = doc["metadata"].get("category", "general")
            formatted_context += f"## Context {i} ({category})\n"
            formatted_context += f"{doc['content']}\n\n"

        return formatted_context
