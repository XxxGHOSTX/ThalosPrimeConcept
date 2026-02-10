"""
Unit tests for Library of Babel Discovery System.
"""

import unittest
from thalos import (
    BabelGenerator,
    BabelSearcher,
    CoherenceScorer,
    PageDecoder,
    BabelPage,
    BabelBook,
    BookAssembler,
    DiscoveryEngine,
    generate_page,
    search_babel,
    score_page,
    is_coherent
)


class TestBabelGenerator(unittest.TestCase):
    """Tests for the BabelGenerator class."""
    
    def test_page_generation(self):
        """Test basic page generation."""
        generator = BabelGenerator()
        address = "1a2b3c"
        page = generator.page_from_address(address)
        
        self.assertEqual(len(page), 3200)
        self.assertTrue(all(c in generator.CHARSET for c in page))
    
    def test_deterministic_generation(self):
        """Test that generation is deterministic."""
        generator = BabelGenerator()
        address = "abcdef"
        
        page1 = generator.page_from_address(address)
        page2 = generator.page_from_address(address)
        
        self.assertEqual(page1, page2)
    
    def test_address_from_seed(self):
        """Test seed to address conversion."""
        generator = BabelGenerator()
        seed = 12345
        address = generator.address_from_seed(seed)
        
        self.assertIsInstance(address, str)
        self.assertTrue(len(address) > 0)
    
    def test_split_phrase_to_fragments(self):
        """Test phrase splitting."""
        generator = BabelGenerator()
        phrase = "test phrase here"
        fragments = generator.split_phrase_to_fragments(phrase)
        
        self.assertIn("test", fragments)
        self.assertIn("phrase", fragments)
        self.assertIn("test phrase", fragments)
    
    def test_generate_candidate_addresses(self):
        """Test candidate address generation."""
        generator = BabelGenerator()
        candidates = generator.generate_candidate_addresses("test", num_candidates=10)
        
        # Should return at most num_candidates (may be less due to deduplication)
        self.assertLessEqual(len(candidates), 10)
        self.assertGreater(len(candidates), 0)
        self.assertTrue(all(isinstance(addr, str) for addr in candidates))


class TestBabelSearcher(unittest.TestCase):
    """Tests for the BabelSearcher class."""
    
    def test_exact_search(self):
        """Test exact phrase search."""
        searcher = BabelSearcher()
        results = searcher.search("test", strategy="exact", max_results=5)
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) <= 5)
    
    def test_fragment_search(self):
        """Test fragment-based search."""
        searcher = BabelSearcher()
        results = searcher.search("hello world", strategy="fragments", max_results=5)
        
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIn("address", result)
            self.assertIn("score", result)
    
    def test_ngram_search(self):
        """Test n-gram search."""
        searcher = BabelSearcher()
        results = searcher.search("abc", strategy="ngram", max_results=3)
        
        self.assertIsInstance(results, list)


class TestCoherenceScorer(unittest.TestCase):
    """Tests for the CoherenceScorer class."""
    
    def test_score_random_text(self):
        """Test scoring of random text (should score low)."""
        scorer = CoherenceScorer()
        random_text = "xyzqpw asdfjkl zxcvbn " * 50
        scores = scorer.score_page(random_text)
        
        self.assertIn("composite", scores)
        self.assertIn("english_density", scores)
        self.assertGreaterEqual(scores["composite"], 0)
        self.assertLessEqual(scores["composite"], 100)
    
    def test_score_coherent_text(self):
        """Test scoring of coherent English text."""
        scorer = CoherenceScorer()
        coherent_text = "This is a coherent English sentence. It has proper structure and punctuation. "
        coherent_text += "The words are real English words. This text should score relatively high."
        
        scores = scorer.score_page(coherent_text)
        
        # Coherent text should have reasonable English density
        self.assertGreater(scores["english_density"], 0.25)
    
    def test_phrase_match_scoring(self):
        """Test scoring with target phrase matching."""
        scorer = CoherenceScorer()
        text = "The quick brown fox jumps over the lazy dog."
        target_phrases = ["quick brown", "lazy dog"]
        
        scores = scorer.score_page(text, target_phrases)
        
        self.assertIn("phrase_match", scores)
        self.assertGreater(scores["phrase_match"], 0)


class TestBabelPage(unittest.TestCase):
    """Tests for the BabelPage dataclass."""
    
    def test_create_page(self):
        """Test creating a BabelPage."""
        page = BabelPage(
            address="abc123",
            content="test content",
            coherence_score=75.5
        )
        
        self.assertEqual(page.address, "abc123")
        self.assertEqual(page.content, "test content")
        self.assertEqual(page.coherence_score, 75.5)
        self.assertIsNotNone(page.retrieved_at)
    
    def test_page_hash(self):
        """Test page hash generation."""
        page = BabelPage(
            address="abc",
            content="test",
            coherence_score=50.0
        )
        
        hash1 = page.page_hash
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 16)


class TestBookAssembler(unittest.TestCase):
    """Tests for the BookAssembler class."""
    
    def setUp(self):
        """Set up test pages."""
        self.pages = [
            BabelPage(address="a", content="test1 " * 100, coherence_score=60.0),
            BabelPage(address="b", content="test2 " * 100, coherence_score=70.0),
            BabelPage(address="c", content="test3 " * 100, coherence_score=80.0),
        ]
    
    def test_assemble_by_coherence(self):
        """Test book assembly by coherence threshold."""
        assembler = BookAssembler()
        books = assembler.assemble_by_coherence_threshold(
            self.pages,
            min_coherence=50.0,
            book_size=10
        )
        
        self.assertIsInstance(books, list)
        if books:
            self.assertIsInstance(books[0], BabelBook)
    
    def test_assemble_by_phrase_relevance(self):
        """Test book assembly by phrase relevance."""
        assembler = BookAssembler()
        book = assembler.assemble_by_phrase_relevance(
            self.pages,
            target_phrase="test",
            book_size=3
        )
        
        self.assertIsInstance(book, BabelBook)
        self.assertEqual(len(book.pages), 3)
    
    def test_assemble_custom(self):
        """Test custom book assembly."""
        assembler = BookAssembler()
        book = assembler.assemble_custom(
            self.pages,
            title="My Custom Book"
        )
        
        self.assertEqual(book.title, "My Custom Book")
        self.assertEqual(len(book.pages), 3)


class TestBabelBook(unittest.TestCase):
    """Tests for the BabelBook dataclass."""
    
    def setUp(self):
        """Set up test book."""
        pages = [
            BabelPage(address="1", content="page1", coherence_score=60.0),
            BabelPage(address="2", content="page2", coherence_score=70.0),
        ]
        self.book = BabelBook(
            book_id="test123",
            title="Test Book",
            pages=pages,
            coherence_score=65.0,
            assembly_method="test"
        )
    
    def test_page_count(self):
        """Test page count property."""
        self.assertEqual(self.book.page_count, 2)
    
    def test_total_length(self):
        """Test total length calculation."""
        expected_length = len("page1") + len("page2")
        self.assertEqual(self.book.total_length, expected_length)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        book_dict = self.book.to_dict()
        
        self.assertEqual(book_dict["book_id"], "test123")
        self.assertEqual(book_dict["title"], "Test Book")
        self.assertEqual(book_dict["page_count"], 2)
    
    def test_export_text(self):
        """Test text export."""
        text = self.book.export_text(include_metadata=True)
        
        self.assertIn("Test Book", text)
        self.assertIn("page1", text)
        self.assertIn("page2", text)


class TestDiscoveryEngine(unittest.TestCase):
    """Tests for the DiscoveryEngine class."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = DiscoveryEngine(min_coherence=30.0)
        
        self.assertIsNotNone(engine.generator)
        self.assertIsNotNone(engine.searcher)
        self.assertIsNotNone(engine.scorer)
    
    def test_get_page(self):
        """Test single page retrieval."""
        engine = DiscoveryEngine()
        page = engine.get_page("abc123")
        
        self.assertIsNotNone(page)
        self.assertIsInstance(page, BabelPage)
        self.assertEqual(page.address, "abc123")
    
    def test_search(self):
        """Test search functionality."""
        engine = DiscoveryEngine()
        result = engine.search("test", strategy="fragments", max_results=3)
        
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.total_candidates, 0)
        self.assertGreaterEqual(result.execution_time, 0)
    
    def test_cache(self):
        """Test page caching."""
        engine = DiscoveryEngine(cache_enabled=True)
        
        # First access
        page1 = engine.get_page("abc")
        
        # Second access (should be cached)
        page2 = engine.get_page("abc")
        
        self.assertEqual(page1.content, page2.content)
        
        stats = engine.get_cache_stats()
        self.assertTrue(stats["cache_enabled"])
        self.assertGreater(stats["cached_pages"], 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for convenience functions."""
    
    def test_generate_page(self):
        """Test generate_page convenience function."""
        page = generate_page("abc")
        
        self.assertIsInstance(page, str)
        self.assertEqual(len(page), 3200)
    
    def test_search_babel(self):
        """Test search_babel convenience function."""
        results = search_babel("test", max_results=3)
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) <= 3)
    
    def test_score_page(self):
        """Test score_page convenience function."""
        scores = score_page("test text here")
        
        self.assertIn("composite", scores)
        self.assertIsInstance(scores["composite"], (int, float))
    
    def test_is_coherent(self):
        """Test is_coherent convenience function."""
        result = is_coherent("test text", min_score=0.0)
        
        self.assertIsInstance(result, bool)


def run_discovery_tests():
    """Run all discovery system tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBabelGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestBabelSearcher))
    suite.addTests(loader.loadTestsFromTestCase(TestCoherenceScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestBabelPage))
    suite.addTests(loader.loadTestsFromTestCase(TestBookAssembler))
    suite.addTests(loader.loadTestsFromTestCase(TestBabelBook))
    suite.addTests(loader.loadTestsFromTestCase(TestDiscoveryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_discovery_tests()
    exit(0 if success else 1)
