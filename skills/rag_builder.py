import os
import chromadb
from chromadb.utils import embedding_functions

class LocalRAGKnowledgeBase:
    """
    Offline RAG Knowledge Base using ChromaDB.
    Ingests professional course materials (e.g., Big Data, Data Structures) 
    to eliminate LLM hallucinations.
    """
    def __init__(self, db_path="./chroma_db", collection_name="lite_tutor_kb"):
        print("[SYSTEM] Initializing Local Vector Database...")
        # Persist the database locally in the project folder
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Using a lightweight, fast local embedding model (downloads automatically on first run)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or load the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        print(f"[SUCCESS] Connected to collection: {collection_name}")

    def ingest_text_file(self, file_path: str, chunk_size: int = 500):
        """Reads a text file, chunks it, and upserts to the vector database."""
        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return
            
        print(f"\n[PROCESS] Reading and chunking {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Simple chunking strategy (splitting by paragraphs/length)
        # In a real scenario, you'd use LangChain's RecursiveCharacterTextSplitter
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        ids = [f"{os.path.basename(file_path)}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file_path} for _ in range(len(chunks))]
        
        print(f"[PROCESS] Upserting {len(chunks)} chunks into ChromaDB...")
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print("[SUCCESS] Ingestion complete!")

    def query_knowledge(self, query_text: str, n_results: int = 2) -> str:
        """Searches the database for the most relevant chunks."""
        print(f"\n[SEARCH] Querying knowledge base for: '{query_text}'")
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        if not results['documents'][0]:
            return "No relevant context found in the local knowledge base."
            
        # Combine the retrieved chunks into a single context string
        context = "\n---\n".join(results['documents'][0])
        return context

# Quick Local Test Block
if __name__ == "__main__":
    # 1. Initialize the RAG engine
    rag = LocalRAGKnowledgeBase()
    
    # 2. Let's create a dummy textbook file for testing
    dummy_file = "data_structure_notes.txt"
    with open(dummy_file, "w", encoding="utf-8") as f:
        f.write("KMP Algorithm Core Concept: KMP avoids redundant comparisons by utilizing a partial match table (next array) to skip characters safely during string matching.\n")
        f.write("Depth-First Search (DFS): A graph traversal algorithm that explores as far as possible along each branch before backtracking. It commonly uses a Stack data structure.\n")
        f.write("Big Data Principles: Hadoop uses HDFS for distributed storage and MapReduce for distributed processing of massive datasets.\n")
    
    # 3. Feed the textbook to the database
    rag.ingest_text_file(dummy_file)
    
    # 4. Pull the trigger (Test a search)
    question = "What data structure does DFS use?"
    retrieved_info = rag.query_knowledge(question)
    
    print("\n[RESULT] Retrieved Context:")
    print("========================================")
    print(retrieved_info)
    print("========================================")