from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Normalize newlines for cross-platform robustness
        normalized_text = text.replace("\r\n", "\n")
        
        # Split on sentence boundaries: ". ", "! ", "? ", ".\n"
        # Each branch in the lookbehind is exactly length 2, keeping the regex compatible and safe
        raw_sentences = re.split(r'(?<=\. |! |\? |\.\n)', normalized_text)
        
        # Filter out empty or whitespace-only elements
        sentences = [s for s in raw_sentences if s.strip()]
        
        if not sentences:
            return []
        
        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_str = "".join(group).strip()
            if chunk_str:
                chunks.append(chunk_str)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        # Normalize newlines for robustness
        normalized_text = text.replace("\r\n", "\n")
        normalized_separators = [sep.replace("\r\n", "\n") for sep in self.separators]
        return self._split(normalized_text, normalized_separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            # Fallback when there are no separators left
            # Split by chunk_size characters
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        # Try the first separator
        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # If the separator is not in the text, skip to the next separator
        if separator not in current_text:
            return self._split(current_text, next_separators)

        # Split the text by the separator.
        if separator == "":
            parts = list(current_text)
        else:
            parts = current_text.split(separator)

        # Now, for each part, if it's too large, recursively split it
        split_parts = []
        for part in parts:
            if len(part) > self.chunk_size:
                # Recursively split with the next separators
                split_parts.extend(self._split(part, next_separators))
            else:
                split_parts.append(part)

        # Now merge the split parts back together
        return self._merge_splits(split_parts, separator)

    def _merge_splits(self, splits: list[str], separator: str) -> list[str]:
        docs: list[str] = []
        current_doc: list[str] = []
        total = 0
        for s in splits:
            if not s:
                continue
            sep_len = len(separator) if current_doc else 0
            if total + len(s) + sep_len <= self.chunk_size:
                current_doc.append(s)
                total += len(s) + sep_len
            else:
                if current_doc:
                    docs.append(separator.join(current_doc))
                current_doc = [s]
                total = len(s)
        if current_doc:
            docs.append(separator.join(current_doc))
        return docs


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(y * y for y in vec_b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed_size_chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=chunk_size // 10)
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

        strategies = {
            "fixed_size": fixed_size_chunker,
            "by_sentences": sentence_chunker,
            "recursive": recursive_chunker,
        }

        result = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            result[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }
        return result

