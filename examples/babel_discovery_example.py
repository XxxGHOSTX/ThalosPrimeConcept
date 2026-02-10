"""
Example: Library of Babel Discovery System Usage

This example demonstrates how to use the Library of Babel discovery system
to search for phrases, score page coherence, and assemble books.
"""

from thalos import (
    DiscoveryEngine,
    BabelGenerator,
    search_babel,
    generate_page,
    score_page,
    is_coherent
)


def example_basic_page_generation():
    """Example 1: Basic page generation from an address."""
    print("=" * 80)
    print("Example 1: Basic Page Generation")
    print("=" * 80)
    
    # Generate a page from a hexadecimal address
    address = "1a2b3c4d"
    page = generate_page(address)
    
    print(f"\nPage at address {address}:")
    print(f"First 200 characters: {page[:200]}")
    print(f"Total length: {len(page)} characters")
    
    # Score the page for coherence
    scores = score_page(page)
    print(f"\nCoherence Scores:")
    print(f"  English Density: {scores['english_density']:.2f}")
    print(f"  Punctuation: {scores['punctuation']:.2f}")
    print(f"  Sentence Structure: {scores['sentence_structure']:.2f}")
    print(f"  Composite Score: {scores['composite']:.2f}/100")
    print(f"  Is Coherent: {is_coherent(page, min_score=30.0)}")
    print()


def example_simple_search():
    """Example 2: Simple search for a phrase."""
    print("=" * 80)
    print("Example 2: Simple Search")
    print("=" * 80)
    
    query = "thalos prime"
    print(f"\nSearching for: '{query}'")
    
    # Quick search using convenience function
    results = search_babel(query, strategy="fragments", max_results=5)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    Address: {result['address']}")
        print(f"    Score: {result['score']:.2f}")
        print(f"    Strategy: {result['strategy']}")
        print(f"    Snippet: {result['snippet'][:100]}...")
    print()


def example_advanced_discovery():
    """Example 3: Advanced discovery with the DiscoveryEngine."""
    print("=" * 80)
    print("Example 3: Advanced Discovery Engine")
    print("=" * 80)
    
    # Create discovery engine
    engine = DiscoveryEngine(min_coherence=30.0, cache_enabled=True)
    
    # Perform a search
    query = "created by tony ray macier"
    print(f"\nSearching for: '{query}'")
    
    result = engine.search(
        query=query,
        strategy="fragments",
        max_results=5,
        min_coherence=30.0
    )
    
    print(f"\nDiscovery Results:")
    print(f"  Total candidates evaluated: {result.total_candidates}")
    print(f"  Coherent pages found: {result.coherent_pages}")
    print(f"  Average coherence: {result.average_coherence:.2f}")
    print(f"  Execution time: {result.execution_time:.3f} seconds")
    
    print(f"\n  Top Pages:")
    for i, page in enumerate(result.pages[:3], 1):
        print(f"\n    Page {i}:")
        print(f"      Address: {page.address}")
        print(f"      Coherence: {page.coherence_score:.2f}/100")
        print(f"      Content preview: {page.content[:100]}...")
    
    # Check cache stats
    stats = engine.get_cache_stats()
    print(f"\n  Cache Statistics:")
    print(f"    Cached pages: {stats['cached_pages']}")
    print(f"    Cache size: {stats['cache_size_bytes']} bytes")
    print()


def example_book_assembly():
    """Example 4: Book assembly from discovered pages."""
    print("=" * 80)
    print("Example 4: Book Assembly")
    print("=" * 80)
    
    # Create discovery engine
    engine = DiscoveryEngine(min_coherence=30.0)
    
    # Search and assemble a book
    query = "thalos prime discovery engine"
    print(f"\nAssembling book for query: '{query}'")
    
    book = engine.assemble_book(
        query=query,
        book_size=10,
        coherence_threshold=30.0,
        assembly_method="phrase_relevance"
    )
    
    if book:
        print(f"\nBook assembled successfully:")
        print(f"  Book ID: {book.book_id}")
        print(f"  Title: {book.title}")
        print(f"  Pages: {book.page_count}")
        print(f"  Total length: {book.total_length} characters")
        print(f"  Average coherence: {book.coherence_score:.2f}/100")
        print(f"  Assembly method: {book.assembly_method}")
        
        print(f"\n  First page preview:")
        print(f"    Address: {book.pages[0].address}")
        print(f"    Content: {book.pages[0].content[:200]}...")
        
        # Export the book
        # engine.export_book(book, "babel_book.txt", format="text")
        # print(f"\n  Book exported to: babel_book.txt")
    else:
        print("\n  No coherent pages found for book assembly.")
    print()


def example_multiple_strategies():
    """Example 5: Compare different search strategies."""
    print("=" * 80)
    print("Example 5: Comparing Search Strategies")
    print("=" * 80)
    
    query = "knowledge discovery"
    strategies = ["exact", "fragments", "ngram"]
    
    engine = DiscoveryEngine()
    
    print(f"\nSearching for: '{query}'")
    print(f"Using different strategies:\n")
    
    for strategy in strategies:
        result = engine.search(
            query=query,
            strategy=strategy,
            max_results=3,
            min_coherence=25.0
        )
        
        print(f"  Strategy: {strategy}")
        print(f"    Coherent pages: {result.coherent_pages}")
        print(f"    Average coherence: {result.average_coherence:.2f}")
        print(f"    Execution time: {result.execution_time:.3f}s")
        
        if result.pages:
            print(f"    Top result: {result.pages[0].address} (score: {result.pages[0].coherence_score:.2f})")
        print()


def example_custom_generator():
    """Example 6: Using the BabelGenerator directly."""
    print("=" * 80)
    print("Example 6: Custom Generator Usage")
    print("=" * 80)
    
    generator = BabelGenerator()
    
    # Generate a page from a seed
    seed = 12345
    address = generator.address_from_seed(seed)
    page = generator.page_from_address(address)
    
    print(f"\nGenerated page from seed {seed}:")
    print(f"  Address: {address}")
    print(f"  Content preview: {page[:150]}...")
    
    # Split a phrase into searchable fragments
    phrase = "Thalos Prime created by Tony Ray Macier III"
    fragments = generator.split_phrase_to_fragments(phrase)
    
    print(f"\n\nPhrase: '{phrase}'")
    print(f"Fragments for search:")
    for i, fragment in enumerate(fragments, 1):
        print(f"  {i}. '{fragment}'")
    
    # Generate candidate addresses
    candidates = generator.generate_candidate_addresses(phrase, num_candidates=5)
    print(f"\n\nCandidate addresses to search:")
    for i, addr in enumerate(candidates, 1):
        print(f"  {i}. {addr}")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("Library of Babel Discovery System - Examples")
    print("=" * 80 + "\n")
    
    try:
        example_basic_page_generation()
        example_simple_search()
        example_advanced_discovery()
        example_book_assembly()
        example_multiple_strategies()
        example_custom_generator()
        
        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
