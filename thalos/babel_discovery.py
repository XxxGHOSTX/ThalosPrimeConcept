"""
Library of Babel Discovery API

High-level API for discovering, decoding, and assembling content from the Library of Babel.
Integrates generator, decoder, and assembler modules into a cohesive interface.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from .babel_generator import BabelGenerator, BabelSearcher
from .babel_decoder import CoherenceScorer, PageDecoder
from .babel_assembler import BabelPage, BabelBook, BookAssembler, BookExporter


@dataclass
class DiscoveryQuery:
    """Represents a discovery query with parameters."""
    query: str
    strategy: str = "fragments"  # "exact", "fragments", "ngram"
    max_candidates: int = 50
    min_coherence: float = 30.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class DiscoveryResult:
    """Represents the result of a discovery operation."""
    query: DiscoveryQuery
    pages: List[BabelPage]
    total_candidates: int
    coherent_pages: int
    average_coherence: float
    execution_time: float
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            'query': self.query.query,
            'strategy': self.query.strategy,
            'total_candidates': self.total_candidates,
            'coherent_pages': self.coherent_pages,
            'average_coherence': self.average_coherence,
            'execution_time': self.execution_time,
            'pages': [
                {
                    'address': page.address,
                    'coherence_score': page.coherence_score,
                    'snippet': page.content[:100] + "..." if len(page.content) > 100 else page.content
                }
                for page in self.pages
            ]
        }


class DiscoveryEngine:
    """
    High-level discovery engine for Library of Babel exploration.
    
    Provides a unified interface for searching, decoding, and assembling
    coherent content from the Library of Babel.
    """
    
    def __init__(
        self,
        min_coherence: float = 30.0,
        cache_enabled: bool = True
    ):
        """
        Initialize the discovery engine.
        
        Args:
            min_coherence: Minimum coherence score threshold
            cache_enabled: Whether to cache generated pages
        """
        self.generator = BabelGenerator()
        self.searcher = BabelSearcher(self.generator)
        self.scorer = CoherenceScorer()
        self.decoder = PageDecoder(self.scorer, min_coherence)
        self.assembler = BookAssembler()
        self.cache_enabled = cache_enabled
        self._page_cache = {} if cache_enabled else None
    
    def search(
        self,
        query: str,
        strategy: str = "fragments",
        max_results: int = 10,
        min_coherence: float = 30.0
    ) -> DiscoveryResult:
        """
        Search the Library of Babel for a query.
        
        Args:
            query: Search query string
            strategy: Search strategy ("exact", "fragments", "ngram")
            max_results: Maximum number of results to return
            min_coherence: Minimum coherence score
            
        Returns:
            DiscoveryResult with pages and metadata
        """
        import time
        start_time = time.time()
        
        # Create query object
        discovery_query = DiscoveryQuery(
            query=query,
            strategy=strategy,
            max_candidates=max_results * 5,
            min_coherence=min_coherence
        )
        
        # Search for candidates
        search_results = self.searcher.search(
            query,
            strategy=strategy,
            max_results=max_results * 5
        )
        
        # Convert to BabelPage objects with coherence scoring
        pages = []
        target_phrases = [query] + self.generator.split_phrase_to_fragments(query)
        
        for result in search_results:
            address = result['address']
            
            # Check cache
            if self.cache_enabled and address in self._page_cache:
                content = self._page_cache[address]
            else:
                content = self.generator.page_from_address(address)
                if self.cache_enabled:
                    self._page_cache[address] = content
            
            # Score coherence
            scores = self.scorer.score_page(content, target_phrases)
            coherence = scores['composite']
            
            if coherence >= min_coherence:
                page = BabelPage(
                    address=address,
                    content=content,
                    coherence_score=coherence,
                    scores=scores
                )
                pages.append(page)
        
        # Sort by coherence
        pages.sort(key=lambda p: p.coherence_score, reverse=True)
        pages = pages[:max_results]
        
        # Calculate statistics
        avg_coherence = sum(p.coherence_score for p in pages) / len(pages) if pages else 0.0
        execution_time = time.time() - start_time
        
        return DiscoveryResult(
            query=discovery_query,
            pages=pages,
            total_candidates=len(search_results),
            coherent_pages=len(pages),
            average_coherence=avg_coherence,
            execution_time=execution_time
        )
    
    def get_page(self, address: str) -> Optional[BabelPage]:
        """
        Get a single page by address with coherence scoring.
        
        Args:
            address: Hexadecimal page address
            
        Returns:
            BabelPage object or None if invalid address
        """
        try:
            # Check cache
            if self.cache_enabled and address in self._page_cache:
                content = self._page_cache[address]
            else:
                content = self.generator.page_from_address(address)
                if self.cache_enabled:
                    self._page_cache[address] = content
            
            # Score coherence
            scores = self.scorer.score_page(content)
            
            return BabelPage(
                address=address,
                content=content,
                coherence_score=scores['composite'],
                scores=scores
            )
        except (ValueError, Exception):
            return None
    
    def assemble_book(
        self,
        query: str,
        book_size: int = 32,
        coherence_threshold: float = 50.0,
        assembly_method: str = "phrase_relevance"
    ) -> Optional[BabelBook]:
        """
        Search and assemble a book from discovered pages.
        
        Args:
            query: Search query
            book_size: Number of pages in the book
            coherence_threshold: Minimum coherence for pages
            assembly_method: Assembly strategy
            
        Returns:
            Assembled BabelBook or None
        """
        # First, discover pages
        result = self.search(
            query=query,
            strategy="fragments",
            max_results=book_size * 3,
            min_coherence=coherence_threshold
        )
        
        if not result.pages:
            return None
        
        # Assemble book based on method
        if assembly_method == "phrase_relevance":
            return self.assembler.assemble_by_phrase_relevance(
                result.pages,
                target_phrase=query,
                book_size=book_size
            )
        elif assembly_method == "coherence_threshold":
            books = self.assembler.assemble_by_coherence_threshold(
                result.pages,
                min_coherence=coherence_threshold,
                book_size=book_size
            )
            return books[0] if books else None
        elif assembly_method == "address_adjacency":
            books = self.assembler.assemble_by_address_adjacency(
                result.pages,
                book_size=book_size
            )
            return books[0] if books else None
        else:
            raise ValueError(f"Unknown assembly method: {assembly_method}")
    
    def export_book(
        self,
        book: BabelBook,
        filepath: str,
        format: str = "text"
    ):
        """
        Export a book to a file.
        
        Args:
            book: BabelBook to export
            filepath: Output file path
            format: Export format ("text", "json", "metadata")
        """
        if format == "text":
            BookExporter.export_to_text(book, filepath)
        elif format == "json":
            BookExporter.export_to_json(book, filepath)
        elif format == "metadata":
            BookExporter.export_metadata_only(book, filepath)
        else:
            raise ValueError(f"Unknown export format: {format}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        if not self.cache_enabled:
            return {"cache_enabled": False}
        
        return {
            "cache_enabled": True,
            "cached_pages": len(self._page_cache),
            "cache_size_bytes": sum(len(content) for content in self._page_cache.values())
        }
    
    def clear_cache(self):
        """Clear the page cache."""
        if self.cache_enabled:
            self._page_cache.clear()


class DiscoveryAPI:
    """
    REST-like API interface for discovery operations.
    
    Provides methods that mirror REST endpoints for integration with web services.
    """
    
    def __init__(self, engine: Optional[DiscoveryEngine] = None):
        """
        Initialize the API.
        
        Args:
            engine: DiscoveryEngine instance (creates new one if None)
        """
        self.engine = engine or DiscoveryEngine()
    
    def post_search(self, request: Dict) -> Dict:
        """
        Handle POST /api/v1/discovery/search
        
        Args:
            request: Dictionary with query, strategy, maxCandidates, minCoherence
            
        Returns:
            Response dictionary with results
        """
        query = request.get('query', '')
        strategy = request.get('strategy', 'fragments')
        max_candidates = request.get('maxCandidates', 50)
        min_coherence = request.get('minCoherence', 30.0)
        
        result = self.engine.search(
            query=query,
            strategy=strategy,
            max_results=max_candidates,
            min_coherence=min_coherence
        )
        
        return {
            'success': True,
            'data': result.to_dict()
        }
    
    def get_page(self, address: str) -> Dict:
        """
        Handle GET /api/v1/discovery/page/{address}
        
        Args:
            address: Hexadecimal page address
            
        Returns:
            Response dictionary with page data
        """
        page = self.engine.get_page(address)
        
        if page is None:
            return {
                'success': False,
                'error': 'Invalid address or page not found'
            }
        
        return {
            'success': True,
            'data': {
                'address': page.address,
                'content': page.content,
                'coherence_score': page.coherence_score,
                'scores': page.scores,
                'page_hash': page.page_hash
            }
        }
    
    def post_assemble(self, request: Dict) -> Dict:
        """
        Handle POST /api/v1/discovery/assemble
        
        Args:
            request: Dictionary with query, book_size, coherence_threshold, assembly_method
            
        Returns:
            Response dictionary with book data
        """
        query = request.get('query', '')
        book_size = request.get('book_size', 32)
        coherence_threshold = request.get('coherence_threshold', 50.0)
        assembly_method = request.get('assembly_method', 'phrase_relevance')
        
        book = self.engine.assemble_book(
            query=query,
            book_size=book_size,
            coherence_threshold=coherence_threshold,
            assembly_method=assembly_method
        )
        
        if book is None:
            return {
                'success': False,
                'error': 'No coherent pages found for assembly'
            }
        
        return {
            'success': True,
            'data': book.to_dict()
        }
    
    def get_book(self, book_id: str, books_cache: Dict[str, BabelBook]) -> Dict:
        """
        Handle GET /api/v1/discovery/book/{book_id}
        
        Args:
            book_id: Book identifier
            books_cache: Cache of assembled books
            
        Returns:
            Response dictionary with book data
        """
        book = books_cache.get(book_id)
        
        if book is None:
            return {
                'success': False,
                'error': 'Book not found'
            }
        
        return {
            'success': True,
            'data': book.to_dict()
        }


# Convenience functions for direct usage
def search_and_discover(
    query: str,
    strategy: str = "fragments",
    max_results: int = 10
) -> DiscoveryResult:
    """
    Convenience function for quick searches.
    
    Args:
        query: Search query
        strategy: Search strategy
        max_results: Maximum results
        
    Returns:
        DiscoveryResult
    """
    engine = DiscoveryEngine()
    return engine.search(query, strategy, max_results)


def quick_page_lookup(address: str) -> Optional[str]:
    """
    Quick lookup of a single page by address.
    
    Args:
        address: Hexadecimal address
        
    Returns:
        Page content or None
    """
    generator = BabelGenerator()
    try:
        return generator.page_from_address(address)
    except (ValueError, Exception):
        return None
