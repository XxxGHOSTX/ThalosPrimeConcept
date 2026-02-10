"""
Library of Babel Decoder and Coherence Scoring Module

Implements multi-stage decoding and coherence detection for Library of Babel pages.
Scores pages based on English density, punctuation, sentence structure, and n-gram presence.
"""

from typing import List, Dict, Tuple, Optional, Set
import re
from collections import Counter
import string


class EnglishDictionary:
    """
    Simple English dictionary for word validation.
    Uses a basic word list for coherence checking.
    """
    
    def __init__(self):
        """Initialize with common English words."""
        # Top 1000 most common English words (subset shown here)
        self.words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
            'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
            'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
            'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
            'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
            # Add more common words for better detection
            'created', 'by', 'system', 'prime', 'thalos', 'tony', 'ray', 'macier',
            'discovery', 'knowledge', 'engine', 'platform', 'data', 'process', 'generate',
            'library', 'babel', 'page', 'book', 'text', 'search', 'find', 'algorithm',
            'computer', 'science', 'mathematics', 'research', 'study', 'analysis',
        }
    
    def is_word(self, word: str) -> bool:
        """Check if a word is in the dictionary."""
        return word.lower() in self.words
    
    def add_words(self, words: List[str]):
        """Add words to the dictionary."""
        self.words.update(w.lower() for w in words)


class CoherenceScorer:
    """
    Multi-stage coherence scoring for Library of Babel pages.
    
    Implements a pipeline of heuristics to determine if a page contains
    meaningful, coherent English text.
    """
    
    def __init__(self, dictionary: Optional[EnglishDictionary] = None):
        """
        Initialize the coherence scorer.
        
        Args:
            dictionary: EnglishDictionary instance (creates default if None)
        """
        self.dictionary = dictionary or EnglishDictionary()
        self.sentence_endings = {'.', '!', '?'}
        self.punctuation = set(string.punctuation)
    
    def score_page(
        self,
        page: str,
        target_phrases: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Compute comprehensive coherence score for a page.
        
        Args:
            page: Page content to score
            target_phrases: Optional list of target phrases to check for
            
        Returns:
            Dictionary with individual scores and final composite score
        """
        scores = {}
        
        # 1. Preprocessing
        cleaned = self._preprocess(page)
        
        # 2. English density (what fraction of tokens are English words?)
        scores['english_density'] = self._score_english_density(cleaned)
        
        # 3. Punctuation score (reasonable punctuation usage)
        scores['punctuation'] = self._score_punctuation(page)
        
        # 4. Sentence structure (capitalization, sentence boundaries)
        scores['sentence_structure'] = self._score_sentence_structure(page)
        
        # 5. Word distribution (not too repetitive)
        scores['word_distribution'] = self._score_word_distribution(cleaned)
        
        # 6. N-gram presence (if target phrases provided)
        if target_phrases:
            scores['phrase_match'] = self._score_phrase_match(page, target_phrases)
        else:
            scores['phrase_match'] = 0.0
        
        # 7. Character entropy (randomness check)
        scores['entropy'] = self._score_entropy(page)
        
        # Composite score calculation
        scores['composite'] = self._compute_composite_score(scores)
        
        return scores
    
    def _preprocess(self, text: str) -> str:
        """Clean and normalize text for analysis."""
        # Convert to lowercase
        text = text.lower()
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _score_english_density(self, text: str) -> float:
        """
        Score based on fraction of recognized English words.
        
        Returns: 0.0 to 1.0
        """
        words = text.split()
        if not words:
            return 0.0
        
        english_count = sum(1 for word in words if self.dictionary.is_word(word))
        return english_count / len(words)
    
    def _score_punctuation(self, text: str) -> float:
        """
        Score based on punctuation usage.
        
        Too little punctuation suggests random text.
        Too much suggests noise.
        Optimal range: 2-8% punctuation.
        
        Returns: 0.0 to 1.0
        """
        if not text:
            return 0.0
        
        punct_count = sum(1 for char in text if char in self.punctuation)
        punct_ratio = punct_count / len(text)
        
        # Optimal range
        if 0.02 <= punct_ratio <= 0.08:
            return 1.0
        elif 0.01 <= punct_ratio <= 0.12:
            return 0.7
        elif punct_ratio < 0.01:
            return 0.3
        else:
            return 0.2
    
    def _score_sentence_structure(self, text: str) -> float:
        """
        Score based on sentence-like structure.
        
        Checks for:
        - Sentence endings (. ! ?)
        - Capitalization after periods
        - Reasonable sentence lengths
        
        Returns: 0.0 to 1.0
        """
        score = 0.0
        
        # Check for sentence endings
        sentence_ending_count = sum(1 for char in text if char in self.sentence_endings)
        if sentence_ending_count > 0:
            score += 0.3
            
            # Estimate sentence length
            estimated_sentences = sentence_ending_count
            avg_sentence_length = len(text) / max(1, estimated_sentences)
            
            # Good sentence length: 50-200 characters
            if 50 <= avg_sentence_length <= 200:
                score += 0.4
            elif 30 <= avg_sentence_length <= 300:
                score += 0.2
        
        # Check for capitalization patterns
        sentences = re.split(r'[.!?]+', text)
        capitalized_starts = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        if len(sentences) > 1:
            cap_ratio = capitalized_starts / len(sentences)
            score += 0.3 * cap_ratio
        
        return min(1.0, score)
    
    def _score_word_distribution(self, text: str) -> float:
        """
        Score based on word variety (not too repetitive).
        
        Returns: 0.0 to 1.0
        """
        words = text.split()
        if len(words) < 10:
            return 0.5
        
        # Calculate unique word ratio
        unique_words = len(set(words))
        unique_ratio = unique_words / len(words)
        
        # Check for excessive repetition
        word_counts = Counter(words)
        most_common_count = word_counts.most_common(1)[0][1] if word_counts else 1
        repetition_ratio = most_common_count / len(words)
        
        # Score based on uniqueness (optimal: 30-70% unique)
        if 0.3 <= unique_ratio <= 0.7:
            diversity_score = 1.0
        elif 0.2 <= unique_ratio <= 0.8:
            diversity_score = 0.7
        else:
            diversity_score = 0.4
        
        # Penalize excessive repetition
        if repetition_ratio > 0.2:
            diversity_score *= 0.5
        
        return diversity_score
    
    def _score_phrase_match(self, text: str, target_phrases: List[str]) -> float:
        """
        Score based on presence of target phrases.
        
        Returns: 0.0 to 1.0
        """
        text_lower = text.lower()
        matches = sum(1 for phrase in target_phrases if phrase.lower() in text_lower)
        
        if not target_phrases:
            return 0.0
        
        return matches / len(target_phrases)
    
    def _score_entropy(self, text: str) -> float:
        """
        Score based on character entropy.
        
        Too low entropy = too uniform/repetitive
        Too high entropy = random noise
        
        Returns: 0.0 to 1.0
        """
        if not text:
            return 0.0
        
        # Calculate character frequency
        char_counts = Counter(text.lower())
        total_chars = len(text)
        
        # Calculate Shannon entropy
        import math
        entropy = 0.0
        for count in char_counts.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalize entropy (English text typically has entropy around 4.0-4.5)
        # Library charset has 29 characters, max entropy = log2(29) ~= 4.86
        normalized_entropy = entropy / 4.86
        
        # Optimal range: 0.7-0.95
        if 0.7 <= normalized_entropy <= 0.95:
            return 1.0
        elif 0.5 <= normalized_entropy < 1.0:
            return 0.6
        else:
            return 0.3
    
    def _compute_composite_score(self, scores: Dict[str, float]) -> float:
        """
        Compute final composite score from individual metrics.
        
        Weights (tunable):
        - english_density: 35%
        - punctuation: 15%
        - sentence_structure: 20%
        - word_distribution: 10%
        - phrase_match: 15%
        - entropy: 5%
        
        Returns: 0.0 to 100.0
        """
        weights = {
            'english_density': 0.35,
            'punctuation': 0.15,
            'sentence_structure': 0.20,
            'word_distribution': 0.10,
            'phrase_match': 0.15,
            'entropy': 0.05,
        }
        
        weighted_sum = sum(
            scores.get(key, 0.0) * weight
            for key, weight in weights.items()
        )
        
        # Scale to 0-100
        return weighted_sum * 100


class PageDecoder:
    """
    High-level decoder for Library of Babel pages.
    
    Combines generation, scoring, and filtering.
    """
    
    def __init__(
        self,
        scorer: Optional[CoherenceScorer] = None,
        min_score: float = 30.0
    ):
        """
        Initialize the page decoder.
        
        Args:
            scorer: CoherenceScorer instance
            min_score: Minimum coherence score to consider a page
        """
        self.scorer = scorer or CoherenceScorer()
        self.min_score = min_score
    
    def decode_pages(
        self,
        pages: List[Tuple[str, str]],
        target_phrases: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Decode and score multiple pages.
        
        Args:
            pages: List of (address, content) tuples
            target_phrases: Optional target phrases to search for
            
        Returns:
            List of decoded page dictionaries with scores
        """
        results = []
        
        for address, content in pages:
            scores = self.scorer.score_page(content, target_phrases)
            
            if scores['composite'] >= self.min_score:
                results.append({
                    'address': address,
                    'content': content,
                    'scores': scores,
                    'coherence': scores['composite'],
                    'is_coherent': scores['composite'] >= 50.0
                })
        
        # Sort by coherence score
        results.sort(key=lambda x: x['coherence'], reverse=True)
        return results
    
    def extract_coherent_passages(
        self,
        page: str,
        min_passage_length: int = 50,
        min_coherence: float = 60.0
    ) -> List[Dict[str, any]]:
        """
        Extract coherent passages from a page.
        
        Args:
            page: Page content
            min_passage_length: Minimum length for a passage
            min_coherence: Minimum coherence score (0-100 scale) for extraction
            
        Returns:
            List of passage dictionaries with position and score
        """
        passages = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', page)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) >= min_passage_length:
                # Score this passage
                scores = self.scorer.score_page(sentence)
                
                if scores['composite'] >= min_coherence:
                    passages.append({
                        'text': sentence,
                        'index': i,
                        'length': len(sentence),
                        'coherence': scores['composite']
                    })
        
        return passages


# Convenience functions
def score_page(page: str, target_phrases: Optional[List[str]] = None) -> Dict[str, float]:
    """
    Score a Library of Babel page for coherence.
    
    Args:
        page: Page content
        target_phrases: Optional target phrases
        
    Returns:
        Dictionary of scores
    """
    scorer = CoherenceScorer()
    return scorer.score_page(page, target_phrases)


def is_coherent(page: str, min_score: float = 50.0) -> bool:
    """
    Check if a page is coherent above a threshold.
    
    Args:
        page: Page content
        min_score: Minimum score threshold (0-100)
        
    Returns:
        True if page is coherent
    """
    scores = score_page(page)
    return scores['composite'] >= min_score
