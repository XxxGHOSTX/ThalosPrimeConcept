# Library of Babel Discovery System Architecture

## Overview

The Library of Babel Discovery System is an extension to Thalos Prime that enables deterministic location, extraction, and assembly of coherent text fragments from the Library of Babel's infinite address space. This system allows for reproducible discovery of text patterns, phrases, and knowledge fragments through mathematical determinism rather than exhaustive search.

## Purpose and Constraints

The system is designed to:

1. **Deterministically locate** Library-of-Babel pages/addresses for given phrases and substrings
2. **Harvest pages** containing fragments useful to reconstruct target artifacts
3. **Identify, decode and rank** pages/books that are coherent
4. **Assemble coherent** multi-page artifacts with provenance tracking

### Hard Constraints

- The Library is mathematically deterministic; local reproduction is preferred for exactness and scale
- Exhaustive search is infeasible; use deterministic inversion and targeted enumeration
- Coherence detection is probabilistic and benefits from layered heuristics plus LLM assistance
- Respect site availability if using remote sources; prefer local generation

## High-Level Architecture

The system consists of four logical layers:

### 1. Data / Generation Layer
- Deterministic generator for pages (Basile algorithm)
- Optional site proxy/scraper for cross-reference
- Local page computation for any address without network dependency

### 2. Indexing & Search Layer
- Storage for discovered pages
- Indices for substring hits and word occurrences
- Embedding vectors for semantic queries
- Query history and provenance

### 3. Decoding & Assembly Pipeline
- Multi-stage coherence filters
- Text cleaning and reconstruction
- Sentence assembly
- Book construction from page sequences

### 4. Application Layer
- REST/GraphQL APIs
- Worker queue for background processing
- Front-end viewer and explorer
- Export capabilities

## Component Breakdown

### Generator Module (Deterministic)

**Purpose**: Reproduce the Library of Babel algorithm locally

**Responsibilities**:
- Implement Basile's generator exactly (charset, page length = 3200 characters)
- Provide inverse mapping utilities for string-to-address conversion
- Generate deterministic pseudo-random pages from canonical hex addresses

**Implementation**: Python with bigint support

**Key Algorithm**:
```python
def page_from_address(hex_address):
    state = hex_to_bigint(hex_address)
    page = ''
    for i in range(3200):
        state = (state * MULTIPLIER + INCREMENT) % M
        index = state % len(CHARSET)
        page += CHARSET[index]
    return page
```

### Enumerator Module (Targeted Address Search)

**Purpose**: Enumerate candidate addresses for substrings/split fragments

**Strategies**:
- Direct inversion when algorithm supports substring-to-address mapping
- Deterministic sampling: combine query + salt values
- Fragment enumeration: split phrase into words/ngrams and map each

**Output**: Candidate address list prioritized by likelihood score

### Storage & Indexing

**Primary Storage**: File-based or SQLite for metadata

**Schema**:
- `pages`: address_hex, text, length, hash, source, retrieval_time
- `fragments`: page_id, fragment_text, start_index, end_index
- `queries`: query_text, user_id, created_at, params
- `hits`: query_id, page_id, score, hit_type
- `books`: title, pages_json, coherence_score, exported_url

### Decoding & Filtering Pipeline

**Architecture**: Modular worker tasks with staged processing

**Stages**:
1. **Preprocessing**: Normalize charset, unify whitespace
2. **Language detection**: Fast detection to reject non-English pages
3. **English density heuristic**: Percent tokens matching English dictionary
4. **N-gram presence scoring**: Measure presence of target ngrams
5. **Punctuation/sentence detection**: Count sentence delimiters
6. **Syntactic reconstruction**: Restore spaces/punctuation heuristically
7. **LLM normalization**: Optional LLM-based reconstruction
8. **Coherence scoring**: Combine metrics into final score (0-100)
9. **Book assembly**: Find sequences of contiguous pages

**Coherence Score Formula** (tunable):
```
score = min(80, 70 * exactPhraseWeight + 30 * englishDensity) + 
        punctuationBonus + llmConfidenceScaled
```

### Assembly Engine

**Purpose**: Create "books" from groups of pages

**Definition**: A book is a group of pages (configurable, e.g., 32, 64 pages)

**Assembly Heuristics**:
- **Address adjacency**: Pages with sequential hex addresses
- **Semantic adjacency**: Embeddings distance < threshold
- **Combined adjacency**: Prioritize pages meeting both criteria

**Output**: Book artifact with:
- Pages in assembled order
- Coherence metadata per page
- Derived canonical text
- Full provenance chain

## REST API Specification

### Core Endpoints

**POST /api/v1/discovery/search**
```json
{
  "query": "Thalos Prime created by Tony Ray Macier III",
  "strategy": "exact|fragments|ngram",
  "maxCandidates": 500
}
```

**GET /api/v1/discovery/page/{address}**
- Returns page content for given hex address

**POST /api/v1/discovery/assemble**
```json
{
  "query": "target phrase",
  "book_size": 32,
  "coherence_threshold": 70
}
```

**GET /api/v1/discovery/book/{book_id}**
- Returns assembled book with all metadata

**POST /api/v1/discovery/export/{book_id}**
- Returns ZIP/TXT/PDF export

### Response Format

```json
{
  "query": "Thalos Prime created by Tony Ray Macier III",
  "candidates": [
    {
      "address": "HEX-1A2B...",
      "snippet": "Thalos Prime created by...",
      "score": 92,
      "source": "local"
    }
  ]
}
```

## Implementation Constants

### Library of Babel Parameters

```python
# Character set (29 characters)
CHARSET = " abcdefghijklmnopqrstuvwxyz,."

# Page parameters
PAGE_LENGTH = 3200  # characters per page
PAGES_PER_VOLUME = 410  # standard Library structure
VOLUMES_PER_SHELF = 32
SHELVES_PER_WALL = 5
WALLS_PER_HEXAGON = 4

# Generator constants (Basile algorithm)
# These must match the canonical implementation exactly
MULTIPLIER = 1103515245
INCREMENT = 12345
MODULUS = 2**31
```

## Workflow Example

1. **User Input**: "Thalos Prime created by Tony Ray Macier III"
2. **Search Module**: Locate all substrings / candidate fragments
3. **Decoder Stack**: Reconstruct fragments into coherent phrases
4. **Synthesis Engine**: Merge phrases, score coherence, generate output
5. **Execution Graph**: Schedule dependent tasks for parallel decoding
6. **Output**: Feed into viewer with provenance metadata
7. **Storage**: Log fragment, page, timestamp, coherence score

## Scalability Considerations

- Page generation is CPU-intensive; cache generated pages by address hash
- Embedding generation and LLM calls are cost drivers; batch requests
- Use distributed worker pools for large enumeration jobs
- Typical resource sizing:
  - 2-4 worker processes for generator + indexing
  - Local storage for page cache
  - Optional GPU for LLM operations

## Testing Strategy

- **Unit tests**: Generator must produce byte-for-byte identical output
- **Determinism tests**: Cross-platform consistency validation
- **Integration tests**: End-to-end search → fetch → decode → assemble
- **Performance tests**: Concurrent search jobs with latency measurement
- **Coherence validation**: Ground-truth set with synthetic clean passages

## Security & Compliance

- All traffic authenticated if exposed as API
- Rate limiting to prevent abuse
- Audit trails for all queries and generations
- PII handling if accepting user uploads
- Respect Library of Babel terms of service for any remote access

## Next Steps

1. Implement deterministic generator module
2. Create enumerator with fragment strategies
3. Build decoding pipeline with coherence scoring
4. Add storage layer and indexing
5. Implement REST API endpoints
6. Create example notebooks and documentation
