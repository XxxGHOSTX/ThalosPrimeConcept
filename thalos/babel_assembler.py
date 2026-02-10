"""
Library of Babel Book Assembly Module

Assembles coherent "books" from sequences of Library of Babel pages.
Uses address adjacency and semantic similarity to group related pages.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class BabelPage:
    """Represents a single Library of Babel page with metadata."""
    address: str
    content: str
    coherence_score: float
    scores: Dict[str, float] = field(default_factory=dict)
    retrieved_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.retrieved_at is None:
            self.retrieved_at = datetime.now()
    
    @property
    def page_hash(self) -> str:
        """Generate a hash of the page content."""
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]


@dataclass
class BabelBook:
    """Represents an assembled book from multiple pages."""
    book_id: str
    title: str
    pages: List[BabelPage]
    coherence_score: float
    assembly_method: str
    created_at: datetime = field(default_factory=lambda: datetime.now())
    metadata: Dict = field(default_factory=dict)
    
    @property
    def page_count(self) -> int:
        """Number of pages in the book."""
        return len(self.pages)
    
    @property
    def total_length(self) -> int:
        """Total character count across all pages."""
        return sum(len(page.content) for page in self.pages)
    
    def to_dict(self) -> Dict:
        """Convert book to dictionary representation."""
        return {
            'book_id': self.book_id,
            'title': self.title,
            'page_count': self.page_count,
            'total_length': self.total_length,
            'coherence_score': self.coherence_score,
            'assembly_method': self.assembly_method,
            'created_at': self.created_at.isoformat(),
            'pages': [
                {
                    'address': page.address,
                    'coherence_score': page.coherence_score,
                    'page_hash': page.page_hash,
                    'length': len(page.content)
                }
                for page in self.pages
            ],
            'metadata': self.metadata
        }
    
    def export_text(self, include_metadata: bool = True) -> str:
        """Export book as plain text."""
        lines = []
        
        if include_metadata:
            lines.append(f"# {self.title}")
            lines.append(f"Book ID: {self.book_id}")
            lines.append(f"Pages: {self.page_count}")
            lines.append(f"Coherence: {self.coherence_score:.2f}")
            lines.append(f"Assembly Method: {self.assembly_method}")
            lines.append(f"Created: {self.created_at.isoformat()}")
            lines.append("")
            lines.append("=" * 80)
            lines.append("")
        
        for i, page in enumerate(self.pages, 1):
            lines.append(f"--- Page {i} (Address: {page.address}) ---")
            lines.append(page.content)
            lines.append("")
        
        return "\n".join(lines)


class BookAssembler:
    """
    Assembles books from Library of Babel pages using various strategies.
    """
    
    def __init__(self, default_book_size: int = 32):
        """
        Initialize the book assembler.
        
        Args:
            default_book_size: Default number of pages per book
        """
        self.default_book_size = default_book_size
    
    def assemble_by_address_adjacency(
        self,
        pages: List[BabelPage],
        book_size: Optional[int] = None
    ) -> List[BabelBook]:
        """
        Assemble books from pages with adjacent addresses.
        
        Args:
            pages: List of BabelPage objects
            book_size: Number of pages per book (uses default if None)
            
        Returns:
            List of assembled BabelBook objects
        """
        book_size = book_size or self.default_book_size
        
        # Sort pages by address
        sorted_pages = sorted(pages, key=lambda p: int(p.address, 16))
        
        books = []
        for i in range(0, len(sorted_pages), book_size):
            book_pages = sorted_pages[i:i + book_size]
            
            if len(book_pages) < book_size // 2:
                # Skip incomplete books that are too small
                continue
            
            # Calculate average coherence
            avg_coherence = sum(p.coherence_score for p in book_pages) / len(book_pages)
            
            # Generate book ID
            book_id = self._generate_book_id(book_pages)
            
            # Create title based on first page address
            title = f"Book at Address {book_pages[0].address[:8]}..."
            
            book = BabelBook(
                book_id=book_id,
                title=title,
                pages=book_pages,
                coherence_score=avg_coherence,
                assembly_method="address_adjacency",
                metadata={
                    'first_address': book_pages[0].address,
                    'last_address': book_pages[-1].address,
                    'address_range': self._calculate_address_range(book_pages)
                }
            )
            books.append(book)
        
        return books
    
    def assemble_by_coherence_threshold(
        self,
        pages: List[BabelPage],
        min_coherence: float = 50.0,
        book_size: Optional[int] = None
    ) -> List[BabelBook]:
        """
        Assemble books from pages meeting coherence threshold.
        
        Args:
            pages: List of BabelPage objects
            min_coherence: Minimum coherence score threshold
            book_size: Number of pages per book
            
        Returns:
            List of assembled BabelBook objects
        """
        book_size = book_size or self.default_book_size
        
        # Filter pages by coherence
        coherent_pages = [p for p in pages if p.coherence_score >= min_coherence]
        
        # Sort by coherence score (best first)
        coherent_pages.sort(key=lambda p: p.coherence_score, reverse=True)
        
        books = []
        for i in range(0, len(coherent_pages), book_size):
            book_pages = coherent_pages[i:i + book_size]
            
            if len(book_pages) < 3:
                # Need at least 3 pages for a book
                continue
            
            avg_coherence = sum(p.coherence_score for p in book_pages) / len(book_pages)
            book_id = self._generate_book_id(book_pages)
            title = f"Coherent Collection (Score: {avg_coherence:.1f})"
            
            book = BabelBook(
                book_id=book_id,
                title=title,
                pages=book_pages,
                coherence_score=avg_coherence,
                assembly_method="coherence_threshold",
                metadata={
                    'min_coherence': min_coherence,
                    'page_scores': [p.coherence_score for p in book_pages]
                }
            )
            books.append(book)
        
        return books
    
    def assemble_by_phrase_relevance(
        self,
        pages: List[BabelPage],
        target_phrase: str,
        book_size: Optional[int] = None
    ) -> Optional[BabelBook]:
        """
        Assemble a book from pages most relevant to a target phrase.
        
        Args:
            pages: List of BabelPage objects
            target_phrase: Target phrase to optimize for
            book_size: Number of pages per book
            
        Returns:
            Single BabelBook optimized for phrase relevance
        """
        book_size = book_size or self.default_book_size
        
        # Score pages by phrase relevance
        phrase_lower = target_phrase.lower()
        page_scores = []
        
        for page in pages:
            # Count phrase occurrences and fragments
            content_lower = page.content.lower()
            exact_count = content_lower.count(phrase_lower)
            
            # Split phrase into words and count individual occurrences
            words = phrase_lower.split()
            word_counts = sum(content_lower.count(word) for word in words)
            
            # Combined relevance score
            relevance = (exact_count * 100) + (word_counts * 10) + page.coherence_score
            page_scores.append((relevance, page))
        
        # Sort by relevance
        page_scores.sort(reverse=True)
        
        # Take top pages
        top_pages = [page for _, page in page_scores[:book_size]]
        
        if not top_pages:
            return None
        
        avg_coherence = sum(p.coherence_score for p in top_pages) / len(top_pages)
        book_id = self._generate_book_id(top_pages)
        title = f"Collection: \"{target_phrase[:50]}...\""
        
        return BabelBook(
            book_id=book_id,
            title=title,
            pages=top_pages,
            coherence_score=avg_coherence,
            assembly_method="phrase_relevance",
            metadata={
                'target_phrase': target_phrase,
                'top_relevance_score': page_scores[0][0] if page_scores else 0
            }
        )
    
    def assemble_custom(
        self,
        pages: List[BabelPage],
        title: str,
        book_id: Optional[str] = None
    ) -> BabelBook:
        """
        Assemble a custom book from manually selected pages.
        
        Args:
            pages: List of BabelPage objects
            title: Custom book title
            book_id: Optional custom book ID
            
        Returns:
            BabelBook with custom configuration
        """
        if not pages:
            raise ValueError("Cannot create empty book")
        
        avg_coherence = sum(p.coherence_score for p in pages) / len(pages)
        book_id = book_id or self._generate_book_id(pages)
        
        return BabelBook(
            book_id=book_id,
            title=title,
            pages=pages,
            coherence_score=avg_coherence,
            assembly_method="custom",
            metadata={
                'custom_title': True
            }
        )
    
    def _generate_book_id(self, pages: List[BabelPage]) -> str:
        """Generate a unique book ID from pages."""
        # Combine page addresses and hash
        address_str = "".join(p.address for p in pages[:5])  # Use first 5 addresses
        return hashlib.sha256(address_str.encode()).hexdigest()[:16]
    
    def _calculate_address_range(self, pages: List[BabelPage]) -> int:
        """Calculate the address range span for a book."""
        if len(pages) < 2:
            return 0
        
        addresses = [int(p.address, 16) for p in pages]
        return max(addresses) - min(addresses)


class BookExporter:
    """
    Export books to various formats.
    """
    
    @staticmethod
    def export_to_text(book: BabelBook, filepath: str):
        """Export book to plain text file."""
        content = book.export_text(include_metadata=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def export_to_json(book: BabelBook, filepath: str):
        """Export book to JSON file."""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(book.to_dict(), f, indent=2)
    
    @staticmethod
    def export_metadata_only(book: BabelBook, filepath: str):
        """Export only book metadata (no full page content)."""
        import json
        metadata = book.to_dict()
        # Remove full content, keep only hashes
        for page in metadata['pages']:
            page.pop('content', None)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)


# Convenience functions
def assemble_book(
    pages: List[BabelPage],
    method: str = "address_adjacency",
    **kwargs
) -> Optional[BabelBook]:
    """
    Assemble a book using the specified method.
    
    Args:
        pages: List of BabelPage objects
        method: Assembly method ("address_adjacency", "coherence_threshold", "phrase_relevance", "custom")
        **kwargs: Additional arguments for the specific method
        
    Returns:
        Assembled BabelBook or None
    """
    assembler = BookAssembler()
    
    if method == "address_adjacency":
        books = assembler.assemble_by_address_adjacency(pages, **kwargs)
        return books[0] if books else None
    elif method == "coherence_threshold":
        books = assembler.assemble_by_coherence_threshold(pages, **kwargs)
        return books[0] if books else None
    elif method == "phrase_relevance":
        return assembler.assemble_by_phrase_relevance(pages, **kwargs)
    elif method == "custom":
        return assembler.assemble_custom(pages, **kwargs)
    else:
        raise ValueError(f"Unknown assembly method: {method}")
