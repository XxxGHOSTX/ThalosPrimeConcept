"""
Thalos Prime Concept - A system for reproducible research with provenance tracking.

This package provides:
- HDR: Human Directive Records with signing and timestamping
- EG: Execution Graphs as DAGs with task orchestration
- Artifact: Digital outputs with unique IDs and metadata
- PR: Provenance Records as immutable chains
- Knowledge Space: Vector embeddings and knowledge graphs
- Orchestrator: Pipeline orchestration with automated discovery
- Sandbox: Safe simulation execution
- Reasoning: Hybrid reasoning capabilities
- Library of Babel Discovery: Deterministic page generation, search, and assembly
"""

from .hdr import HumanDirectiveRecord, generate_keypair
from .execution_graph import ExecutionGraph, Task, TaskStatus
from .artifact import Artifact, ArtifactManager
from .provenance import ProvenanceRecord, ProvenanceChain
from .knowledge_space import KnowledgeSpace, KnowledgeNode, KnowledgeEdge, Document
from .orchestrator import Orchestrator, Pipeline
from .sandbox import SimulationSandbox, SandboxExecutionResult
from .reasoning import HybridReasoning, ReasoningRule

# Library of Babel Discovery System
from .babel_generator import BabelGenerator, BabelSearcher, generate_page, search_babel
from .babel_decoder import CoherenceScorer, PageDecoder, score_page, is_coherent
from .babel_assembler import BabelPage, BabelBook, BookAssembler, BookExporter, assemble_book
from .babel_discovery import DiscoveryEngine, DiscoveryAPI, DiscoveryQuery, DiscoveryResult

__version__ = "0.1.0"
__all__ = [
    # Core Thalos Prime
    "HumanDirectiveRecord",
    "generate_keypair",
    "ExecutionGraph",
    "Task",
    "TaskStatus",
    "Artifact",
    "ArtifactManager",
    "ProvenanceRecord",
    "ProvenanceChain",
    "KnowledgeSpace",
    "KnowledgeNode",
    "KnowledgeEdge",
    "Document",
    "Orchestrator",
    "Pipeline",
    "SimulationSandbox",
    "SandboxExecutionResult",
    "HybridReasoning",
    "ReasoningRule",
    # Library of Babel Discovery
    "BabelGenerator",
    "BabelSearcher",
    "generate_page",
    "search_babel",
    "CoherenceScorer",
    "PageDecoder",
    "score_page",
    "is_coherent",
    "BabelPage",
    "BabelBook",
    "BookAssembler",
    "BookExporter",
    "assemble_book",
    "DiscoveryEngine",
    "DiscoveryAPI",
    "DiscoveryQuery",
    "DiscoveryResult",
]
