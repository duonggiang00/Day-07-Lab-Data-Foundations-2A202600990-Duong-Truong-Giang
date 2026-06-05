from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Retrieve relevant chunks from the vector store
        chunks = self.store.search(question, top_k=top_k)
        
        # Build prompt with chunks as context
        context_items = []
        for idx, chunk in enumerate(chunks, start=1):
            context_items.append(f"[Source {idx}]: {chunk['content']}")
            
        context_str = "\n\n".join(context_items)
        
        prompt = (
            "You are an expert assistant. Answer the following question using only the provided context.\n"
            "If you cannot find the answer, state that the context does not contain enough information.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )
        
        # Call the LLM with the formatted prompt
        return self.llm_fn(prompt)

