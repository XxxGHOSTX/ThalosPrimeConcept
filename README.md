# Thalos Prime — Discovery Execution Engine

Purpose: Formalize human-directed discovery via HDR-anchored execution graphs, hybrid reasoning, and immutable provenance, with integrated Library of Babel discovery capabilities.

Goals: reproducible discoverability, patentable capture of human inventorship, safe in-silico experimentation, and deterministic knowledge discovery.

## Features

- **Human Directive Records (HDR)**: Cryptographically signed records of human-provided objectives and constraints
- **Execution Graphs**: DAG-based task orchestration with automatic dependency resolution
- **Provenance Tracking**: Immutable chains linking artifacts to inputs, HDRs, and execution history
- **Knowledge Space**: Vector embeddings and knowledge graph storage
- **Hybrid Reasoning**: Combines symbolic graph traversal with language model synthesis
- **Simulation Sandbox**: Safe, isolated execution environment for experiments
- **Library of Babel Discovery**: Deterministic page generation, coherence scoring, and book assembly

## Quickstart

### Core Thalos Prime
1. Submit HDR via `POST /hdr` (signed).
2. Upload `pipeline.yaml` to `/pipelines`.
3. Run `POST /run` with `hdr_id` + `pipeline_id`.
4. Retrieve artifacts: `GET /run/{id}/artifacts`.

### Library of Babel Discovery
```python
from thalos import DiscoveryEngine, generate_page, search_babel

# Generate a specific page by address
page = generate_page("1a2b3c4d")
print(f"Page content: {page[:100]}...")

# Search for phrases
results = search_babel("thalos prime", strategy="fragments", max_results=10)
for result in results:
    print(f"Address: {result['address']}, Score: {result['score']}")

# Use the full discovery engine
engine = DiscoveryEngine(min_coherence=30.0)
result = engine.search("knowledge discovery", max_results=10)
print(f"Found {result.coherent_pages} coherent pages")

# Assemble a book from discovered pages
book = engine.assemble_book(
    query="thalos prime discovery",
    book_size=32,
    coherence_threshold=50.0
)
if book:
    engine.export_book(book, "discovered_book.txt", format="text")
```

## Documentation

- Full specification: `docs/spec.md`
- Discovery architecture: `docs/discovery_architecture.md`
- Multi-stage runbook: `docs/multi_stage_steps.md`
- Chatbot/epistemic engine (Step 1): `docs/chatbot_architecture.md`
- Example usage: `examples/babel_discovery_example.py`
- Test coverage: `tests/test_babel_discovery.py`

## Library of Babel Discovery System

The discovery system implements a deterministic generator for Library of Babel pages with:

### Components

1. **BabelGenerator**: Deterministic page generation using the Basile algorithm
   - Generates 3200-character pages from hexadecimal addresses
   - Supports phrase-to-address mapping
   - Fragment-based search strategies

2. **CoherenceScorer**: Multi-stage coherence detection
   - English density scoring
   - Punctuation and sentence structure analysis
   - N-gram presence matching
   - Composite scoring (0-100 scale)

3. **BookAssembler**: Assembles coherent books from page sequences
   - Address adjacency detection
   - Coherence-based grouping
   - Phrase relevance optimization
   - Multiple assembly strategies

4. **DiscoveryEngine**: High-level API for search and discovery
   - Unified search interface
   - Page caching for performance
   - Book export capabilities (text, JSON, metadata)

### Search Strategies

- **Exact**: Search for exact phrase matches
- **Fragments**: Search for phrase fragments (words, pairs, triplets)
- **N-gram**: Character n-gram based similarity
- **Inversion**: Deterministic substring-to-address inversion over a bounded seed window

### API Overview

The discovery system provides both programmatic and REST-like APIs:

```python
# Programmatic API
from thalos import DiscoveryEngine, DiscoveryAPI

engine = DiscoveryEngine()
result = engine.search("query", strategy="fragments", max_results=10)

# REST-like API (for web service integration)
api = DiscoveryAPI(engine)
response = api.post_search({
    "query": "thalos prime",
    "strategy": "fragments",
    "maxCandidates": 50,
    "minCoherence": 30.0
})
```

## Security

All HDR payloads must be cryptographically signed. System enforces "no_wetlab" filter by default.
