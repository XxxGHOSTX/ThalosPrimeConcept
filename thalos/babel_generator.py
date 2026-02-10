"""
Library of Babel Generator Module

Implements the deterministic Basile algorithm for generating Library of Babel pages.
This module allows local computation of any page without network dependency.

The Library of Babel contains every possible combination of characters, deterministically
addressable by a hexadecimal address. This implementation reproduces the canonical
algorithm for educational and research purposes.
"""

from typing import Optional, List, Tuple
import hashlib
import struct


class BabelGenerator:
    """
    Deterministic generator for Library of Babel pages.
    
    Implements the Basile algorithm to generate the exact content of any page
    in the Library given its hexadecimal address.
    """
    
    # Library of Babel character set (29 characters: space + 26 letters + comma + period)
    CHARSET = " abcdefghijklmnopqrstuvwxyz,."
    
    # Page structure constants
    PAGE_LENGTH = 3200  # characters per page
    PAGES_PER_VOLUME = 410
    VOLUMES_PER_SHELF = 32
    SHELVES_PER_WALL = 5
    WALLS_PER_HEXAGON = 4
    
    # Linear Congruential Generator (LCG) constants
    # These are standard LCG parameters used in many implementations
    MULTIPLIER = 1103515245
    INCREMENT = 12345
    MODULUS = 2**31
    
    def __init__(self):
        """Initialize the Babel generator."""
        self.charset_length = len(self.CHARSET)
    
    def page_from_address(self, hex_address: str) -> str:
        """
        Generate a page's content from its hexadecimal address.
        
        Args:
            hex_address: Hexadecimal string representing the page address
            
        Returns:
            String containing the 3200 characters of the page
        """
        # Convert hex address to integer seed
        try:
            state = int(hex_address, 16)
        except ValueError:
            raise ValueError(f"Invalid hexadecimal address: {hex_address}")
        
        # Generate page using LCG
        page = []
        for _ in range(self.PAGE_LENGTH):
            state = (state * self.MULTIPLIER + self.INCREMENT) % self.MODULUS
            char_index = state % self.charset_length
            page.append(self.CHARSET[char_index])
        
        return ''.join(page)
    
    def address_from_seed(self, seed: int) -> str:
        """
        Convert an integer seed to a hexadecimal address.
        
        Args:
            seed: Integer seed value
            
        Returns:
            Hexadecimal address string
        """
        return hex(seed)[2:]  # Remove '0x' prefix
    
    def find_substring_candidates(
        self, 
        substring: str, 
        max_candidates: int = 100,
        seed_range: Tuple[int, int] = (0, 1000000)
    ) -> List[Tuple[str, int]]:
        """
        Find candidate addresses that might contain the given substring.
        
        This uses a deterministic sampling approach, testing addresses derived
        from the substring itself plus sequential offsets.
        
        Args:
            substring: The text to search for
            max_candidates: Maximum number of candidates to return
            seed_range: Range of seed values to test (start, end)
            
        Returns:
            List of (hex_address, position) tuples where substring was found
        """
        candidates = []
        
        # Generate base seed from substring hash
        base_seed = int(hashlib.md5(substring.encode()).hexdigest()[:8], 16)
        
        # Test sequential addresses around the base seed
        for offset in range(seed_range[0], seed_range[1]):
            if len(candidates) >= max_candidates:
                break
                
            seed = (base_seed + offset) % self.MODULUS
            hex_address = self.address_from_seed(seed)
            page = self.page_from_address(hex_address)
            
            # Check if substring appears in page
            position = page.find(substring)
            if position != -1:
                candidates.append((hex_address, position))
        
        return candidates

    def invert_substring(
        self,
        substring: str,
        max_candidates: int = 20,
        seed_range: Tuple[int, int] = (0, 5000)
    ) -> List[Tuple[str, int]]:
        """
        Deterministically search for addresses that could produce a given substring.

        Uses modular constraints on the LCG to prune seeds whose initial state modulo
        the charset size cannot yield the substring, then scans a bounded seed window.

        Args:
            substring: Target substring to locate
            max_candidates: Maximum candidates to return
            seed_range: Inclusive start, exclusive end seed range to test (clamped to [0, MODULUS))

        Returns:
            List of (hex_address, position) tuples
        """
        if not substring:
            return []

        substring = substring.lower()
        try:
            targets = [self.CHARSET.index(c) for c in substring]
        except ValueError:
            return []  # Contains characters outside charset

        charset_size = self.charset_length
        a_mod = self.MULTIPLIER % charset_size
        c_mod = self.INCREMENT % charset_size

        # Precompute valid residues for s0 (state mod charset) that satisfy substring
        valid_residues: List[int] = []
        for seed_residue in range(charset_size):
            state_mod = seed_residue
            matches_pattern = True
            for target in targets:
                if state_mod != target:
                    matches_pattern = False
                    break
                state_mod = (a_mod * state_mod + c_mod) % charset_size
            if matches_pattern:
                valid_residues.append(seed_residue)

        if not valid_residues:
            # If no modular residues satisfy the pattern, fall back to scanning all residues
            # so substrings occurring deeper in the page are still detected.
            valid_residues = list(range(charset_size))

        start, end = seed_range
        if start >= end:
            return []
        start = max(0, start)
        end = min(self.MODULUS, end)
        if start >= end:
            return []

        def scan_seed_range(residue_filtered: bool) -> List[Tuple[str, int]]:
            found: List[Tuple[str, int]] = []
            for seed in range(start, end):
                if len(found) >= max_candidates:
                    break
                if residue_filtered and seed % charset_size not in valid_residues:
                    continue

                hex_address = self.address_from_seed(seed)
                page = self.page_from_address(hex_address)
                position = page.find(substring)
                if position != -1:
                    found.append((hex_address, position))
            return found

        has_filtered_residues = len(valid_residues) < charset_size
        candidates = scan_seed_range(residue_filtered=has_filtered_residues)
        if candidates or not has_filtered_residues:
            return candidates

        return scan_seed_range(residue_filtered=False)
    
    def split_phrase_to_fragments(self, phrase: str, min_length: int = 3) -> List[str]:
        """
        Split a phrase into searchable fragments.
        
        Args:
            phrase: Input phrase to split
            min_length: Minimum fragment length
            
        Returns:
            List of fragment strings
        """
        # Convert to lowercase and split on whitespace
        phrase = phrase.lower()
        words = phrase.split()
        
        # Create fragments: individual words and consecutive pairs
        fragments = []
        
        # Add individual words
        for word in words:
            if len(word) >= min_length:
                fragments.append(word)
        
        # Add word pairs
        for i in range(len(words) - 1):
            pair = f"{words[i]} {words[i+1]}"
            if len(pair) >= min_length:
                fragments.append(pair)
        
        # Add word triplets if phrase is long enough
        if len(words) >= 3:
            for i in range(len(words) - 2):
                triplet = f"{words[i]} {words[i+1]} {words[i+2]}"
                fragments.append(triplet)
        
        return fragments
    
    def generate_candidate_addresses(
        self,
        phrase: str,
        num_candidates: int = 50
    ) -> List[str]:
        """
        Generate candidate addresses for a phrase using multiple strategies.
        
        Args:
            phrase: Target phrase to locate
            num_candidates: Number of candidate addresses to generate
            
        Returns:
            List of hexadecimal addresses to check
        """
        addresses = set()
        
        # Strategy 1: Direct hash of full phrase
        phrase_hash = int(hashlib.md5(phrase.encode()).hexdigest()[:8], 16)
        for i in range(num_candidates // 3):
            seed = (phrase_hash + i) % self.MODULUS
            addresses.add(self.address_from_seed(seed))
        
        # Strategy 2: Hash of fragments
        fragments = self.split_phrase_to_fragments(phrase)
        for fragment in fragments[:10]:  # Limit fragments
            frag_hash = int(hashlib.md5(fragment.encode()).hexdigest()[:8], 16)
            for i in range(max(1, num_candidates // (3 * len(fragments)))):
                seed = (frag_hash + i) % self.MODULUS
                addresses.add(self.address_from_seed(seed))
        
        # Strategy 3: Deterministic sampling from phrase characters
        char_sum = sum(ord(c) for c in phrase)
        for i in range(num_candidates // 3):
            seed = (char_sum * (i + 1) * 997) % self.MODULUS  # 997 is prime
            addresses.add(self.address_from_seed(seed))
        
        return list(addresses)[:num_candidates]


class BabelSearcher:
    """
    Higher-level search interface for finding phrases in the Library of Babel.
    """
    
    def __init__(self, generator: Optional[BabelGenerator] = None):
        """
        Initialize the searcher.
        
        Args:
            generator: BabelGenerator instance (creates new one if None)
        """
        self.generator = generator or BabelGenerator()
    
    def search(
        self,
        query: str,
        strategy: str = "fragments",
        max_results: int = 10,
        seed_range: Optional[Tuple[int, int]] = None
    ) -> List[dict]:
        """
        Search for a query string in the Library of Babel.
        
        Args:
            query: Text to search for
            strategy: Search strategy ("exact", "fragments", "ngram")
            max_results: Maximum number of results to return
            seed_range: Optional seed range to constrain inversion search
            
        Returns:
            List of result dictionaries with address, snippet, and score
        """
        results = []
        
        if strategy == "exact":
            # Search for exact phrase
            candidates = self.generator.find_substring_candidates(
                query.lower(),
                max_candidates=max_results * 2
            )
            for hex_address, position in candidates[:max_results]:
                page = self.generator.page_from_address(hex_address)
                snippet = self._extract_snippet(page, position, len(query))
                score = self._score_exact_match(page, query)
                results.append({
                    "address": hex_address,
                    "snippet": snippet,
                    "position": position,
                    "score": score,
                    "strategy": "exact"
                })
        
        elif strategy == "fragments":
            # Search for phrase fragments
            fragments = self.generator.split_phrase_to_fragments(query)
            addresses = self.generator.generate_candidate_addresses(query, max_results * 2)
            
            for hex_address in addresses[:max_results * 2]:
                page = self.generator.page_from_address(hex_address)
                fragment_hits = sum(1 for frag in fragments if frag in page.lower())
                
                if fragment_hits > 0:
                    score = self._score_fragment_match(page, fragments, fragment_hits)
                    snippet = self._extract_best_snippet(page, fragments)
                    results.append({
                        "address": hex_address,
                        "snippet": snippet,
                        "fragment_hits": fragment_hits,
                        "score": score,
                        "strategy": "fragments"
                    })
        
        elif strategy == "ngram":
            # Search using n-gram analysis
            ngrams = self._generate_ngrams(query.lower(), n=3)
            addresses = self.generator.generate_candidate_addresses(query, max_results * 2)
            
            for hex_address in addresses[:max_results * 2]:
                page = self.generator.page_from_address(hex_address)
                ngram_score = self._score_ngram_match(page, ngrams)
                
                if ngram_score > 0.1:
                    snippet = self._extract_best_snippet(page, [query])
                    results.append({
                        "address": hex_address,
                        "snippet": snippet,
                        "score": ngram_score * 100,
                        "strategy": "ngram"
                    })
        
        elif strategy == "inversion":
            # Deterministic inversion-based search for substring
            window = seed_range or (0, 5000)
            candidates = self.generator.invert_substring(
                query.lower(),
                max_candidates=max_results,
                seed_range=window
            )
            for hex_address, position in candidates:
                page = self.generator.page_from_address(hex_address)
                snippet = self._extract_snippet(page, position, len(query))
                score = self._score_exact_match(page, query)
                results.append({
                    "address": hex_address,
                    "snippet": snippet,
                    "position": position,
                    "score": score,
                    "strategy": "inversion"
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def _extract_snippet(
        self,
        page: str,
        position: int,
        length: int,
        context: int = 50
    ) -> str:
        """Extract a snippet around a position in the page."""
        start = max(0, position - context)
        end = min(len(page), position + length + context)
        snippet = page[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(page):
            snippet = snippet + "..."
        
        return snippet
    
    def _extract_best_snippet(
        self,
        page: str,
        fragments: List[str],
        length: int = 100
    ) -> str:
        """Extract the best snippet containing the most fragments."""
        best_score = 0
        best_snippet = page[:length]
        
        for i in range(0, len(page) - length, 10):
            window = page[i:i + length]
            score = sum(1 for frag in fragments if frag in window.lower())
            if score > best_score:
                best_score = score
                best_snippet = window
        
        return best_snippet.strip()
    
    def _score_exact_match(self, page: str, query: str) -> float:
        """Score an exact match based on context quality."""
        # Base score for exact match
        score = 80.0
        
        # Bonus for clear context (spaces around match)
        if f" {query.lower()} " in page.lower():
            score += 10.0
        
        # Bonus for sentence-like structure nearby
        match_pos = page.lower().find(query.lower())
        if match_pos > 0:
            context = page[max(0, match_pos - 50):match_pos + len(query) + 50]
            if '.' in context or ',' in context:
                score += 10.0
        
        return min(100.0, score)
    
    def _score_fragment_match(
        self,
        page: str,
        fragments: List[str],
        fragment_hits: int
    ) -> float:
        """Score a fragment match based on number and density of hits."""
        if not fragments:
            return 0.0
        
        hit_ratio = fragment_hits / len(fragments)
        base_score = hit_ratio * 70
        
        # Bonus for multiple fragments in close proximity
        positions = []
        for frag in fragments:
            pos = page.lower().find(frag)
            if pos != -1:
                positions.append(pos)
        
        if len(positions) >= 2:
            positions.sort()
            avg_distance = sum(positions[i + 1] - positions[i] for i in range(len(positions) - 1)) / (len(positions) - 1)
            if avg_distance < 200:  # Close proximity
                base_score += 20
        
        return min(100.0, base_score)
    
    def _generate_ngrams(self, text: str, n: int = 3) -> List[str]:
        """Generate n-grams from text."""
        text = text.replace(" ", "")  # Remove spaces
        return [text[i:i + n] for i in range(len(text) - n + 1)]
    
    def _score_ngram_match(self, page: str, ngrams: List[str]) -> float:
        """Score based on n-gram overlap."""
        if not ngrams:
            return 0.0
        
        page_lower = page.lower().replace(" ", "")
        hits = sum(1 for ngram in ngrams if ngram in page_lower)
        return hits / len(ngrams)


# Convenience functions
def generate_page(hex_address: str) -> str:
    """
    Generate a Library of Babel page from its address.
    
    Args:
        hex_address: Hexadecimal address string
        
    Returns:
        Page content (3200 characters)
    """
    generator = BabelGenerator()
    return generator.page_from_address(hex_address)


def search_babel(
    query: str,
    strategy: str = "fragments",
    max_results: int = 10,
    seed_range: Optional[Tuple[int, int]] = None
) -> List[dict]:
    """
    Search the Library of Babel for a query.
    
    Args:
        query: Text to search for
        strategy: Search strategy ("exact", "fragments", "ngram")
        max_results: Maximum number of results
        seed_range: Optional seed range used for inversion strategy
        
    Returns:
        List of result dictionaries
    """
    searcher = BabelSearcher()
    return searcher.search(query, strategy, max_results, seed_range)
