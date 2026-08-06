from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain.tools import tool

from core.config import Settings
from retrieval.index import LocalEmbeddingIndex
from retrieval.llm import build_llm


def _message_content_to_text(content: Any) -> str:
    """Normalize LangChain provider-specific message content to plain text."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") in {None, "text"}:
                text = block.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()
    return str(content).strip() if content is not None else ""


def build_agent(settings: Settings, index: LocalEmbeddingIndex) -> Any:
    """Build a tool-using RAG agent over the supplied local paper index."""

    @tool
    def semantic_search_papers(query: str, top_k: int = 4) -> str:
        """Search the local paper corpus with embeddings and return the most relevant papers."""
        query = query.strip()
        if not query:
            return "A non-empty search query is required."
        collection_size = index.collection.count()
        if collection_size == 0:
            return "The local paper corpus is empty."
        safe_top_k = min(max(1, top_k), collection_size)
        results = index.search(query, top_k=safe_top_k)
        if not results:
            return "No relevant papers were found in the local corpus."
        lines = []
        for result in results:
            lines.append(
                f"paper_id: {result.paper_id}\n"
                f"title: {result.title}\n"
                f"score: {result.score:.4f}\n"
                f"{result.content}"
            )
        return "\n\n".join(lines)

    @tool
    def lookup_paper(paper_id_or_title: str) -> str:
        """Look up a paper by exact paper_id or exact title from the local corpus."""
        record = index.lookup(paper_id_or_title)
        if not record:
            return "No exact paper match found."
        return (
            f"paper_id: {record['paper_id']}\n"
            f"title: {record['title']}\n"
            f"{record['content']}"
        )

    llm = build_llm(settings=settings, temperature=0.0)
    return create_agent(
        model=llm,
        tools=[semantic_search_papers, lookup_paper],
        system_prompt=(
            "You answer questions about the indexed scholarly paper corpus sourced from Crossref. "
            "Use tools before answering factual questions. "
            "Use exact lookup when the user supplies a paper_id or exact title; otherwise use semantic search. "
            "Base every factual claim only on tool results and cite the supporting paper_id values. "
            "If the indexed corpus does not support the answer, say so clearly and do not invent details."
        ),
        name="paper_corpus_agent",
    )


def run_agent_question(agent: Any, question: str) -> str:
    question = question.strip()
    if not question:
        raise ValueError("question must not be empty")
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    messages = result.get("messages", [])
    if not messages:
        return ""
    final_message = messages[-1]
    return _message_content_to_text(getattr(final_message, "content", final_message))
