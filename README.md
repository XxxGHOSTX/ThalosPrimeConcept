# Thalos Prime Concept

A comprehensive system for reproducible research with full provenance tracking, automated discovery, hybrid reasoning, and simulation sandboxing.

## Overview

Thalos Prime implements a complete framework for managing research workflows with:

- **HDR (Human Directive Records)**: Signed, timestamped human directives containing objectives, constraints, parameters, and success criteria
- **EG (Execution Graphs)**: DAGs of tasks with data dependencies executed by an orchestrator
- **Artifacts**: Digital outputs (code, models, simulations, claims) with unique IDs and metadata
- **PR (Provenance Records)**: Immutable chains linking Artifacts → HDR → pipeline version → container → signer
- **Knowledge Space**: Vector embeddings + knowledge graphs + raw documents for automated discovery
- **Hybrid Reasoning**: Combines symbolic rules with vector similarity for intelligent inference
- **Simulation Sandboxing**: Safe execution environment for untrusted code
- **Reproducible Pipelines**: Complete state export for full reproducibility

## Features

### 1. Human Directive Records (HDR)
Cryptographically signed directives that guide research workflows:

```python
from thalos import HumanDirectiveRecord, generate_keypair

private_key, public_key = generate_keypair()

hdr = HumanDirectiveRecord(
    directive_id="HDR-001",
    objectives=["Process data", "Generate insights"],
    constraints=["Time limit: 60s"],
    parameters={"batch_size": 100},
    success_criteria=["All tasks complete successfully"]
)

hdr.sign(private_key, "researcher@example.com")
verified = hdr.verify(public_key)
```

### 2. Execution Graphs (EG)
Build and execute DAGs of dependent tasks:

```python
from thalos import ExecutionGraph, Task

def process_data(**kwargs):
    return {"result": "processed"}

task = Task(
    task_id="task_1",
    name="Process Data",
    function=process_data,
    dependencies=[]
)

graph = ExecutionGraph()
graph.add_task(task)
results = graph.execute()
```

### 3. Artifacts with Provenance
Track all outputs with full lineage:

```python
from thalos import Artifact, ArtifactManager

artifact = Artifact.create_from_content(
    artifact_id="artifact-001",
    artifact_type="model",
    content={"weights": [1.0, 2.0, 3.0]},
    metadata={"accuracy": 0.95}
)

manager = ArtifactManager()
manager.register(artifact)
```

### 4. Provenance Chains
Immutable records linking artifacts to their creation context:

```python
from thalos import ProvenanceRecord, ProvenanceChain

record = ProvenanceRecord(
    record_id="pr-001",
    artifact_id="artifact-001",
    hdr_id="HDR-001",
    pipeline_version="1.0.0",
    container_info={"type": "docker", "image": "python:3.11"},
    signer="researcher@example.com"
)

chain = ProvenanceChain()
chain.add_record(record)
is_valid = chain.verify_chain()
```

### 5. Knowledge Space
Store and query knowledge using vector embeddings and graphs:

```python
from thalos import KnowledgeSpace, KnowledgeNode
import numpy as np

ks = KnowledgeSpace()

node = KnowledgeNode(
    node_id="concept_1",
    node_type="concept",
    properties={"name": "machine_learning"},
    embedding=np.random.rand(384)
)

ks.add_node(node)
similar = ks.find_similar(query_embedding, top_k=5)
```

### 6. Pipeline Orchestration
Integrate all components in reproducible pipelines:

```python
from thalos import Orchestrator

orchestrator = Orchestrator()
pipeline = orchestrator.create_pipeline(
    pipeline_id="pipeline-001",
    pipeline_version="1.0.0",
    hdr=hdr
)

# Add tasks, execute, and track everything
pipeline.add_task(task)
results = pipeline.execute()

# Export complete state for reproducibility
orchestrator.export_pipeline_state("pipeline-001", "state.json")
```

### 7. Hybrid Reasoning
Combine symbolic rules with vector similarity:

```python
from thalos import HybridReasoning, ReasoningRule

reasoning = HybridReasoning(knowledge_space)

rule = ReasoningRule(
    rule_id="rule_1",
    pattern={"node_type": "concept", "category": "AI"},
    conclusion={"is_ai_related": True}
)

reasoning.add_rule(rule)
inferences = reasoning.apply_rules("concept_1")
```

### 8. Simulation Sandbox
Safely execute untrusted code:

```python
from thalos import SimulationSandbox

sandbox = SimulationSandbox(timeout_seconds=10)

code = """
result = sum(range(100))
"""

result = sandbox.execute_python(code)
print(result.success, result.output)
```

## Installation

```bash
pip install -r requirements.txt
```

## Running the Example

```bash
python examples/example_usage.py
```

This demonstrates:
1. Creating and signing HDRs
2. Building execution graphs
3. Tracking artifacts and provenance
4. Using the knowledge space
5. Applying hybrid reasoning
6. Running simulations in sandbox
7. Exporting pipeline state

## Architecture

The system implements the following architecture:

```
HDR (Directive) 
    ↓
Pipeline → EG (DAG) → Tasks → Artifacts
    ↓                            ↓
Container Info              Provenance Chain
    ↓                            ↓
    └──────────→ Knowledge Space ←───────┘
                      ↓
              Hybrid Reasoning
                      ↓
            Automated Discovery
```

## Key Concepts

### Reproducibility
- Complete pipeline state export
- Immutable provenance chains
- Signed directives with timestamps
- Container/environment tracking

### Automated Discovery
- Vector similarity search
- Knowledge graph traversal
- Hybrid reasoning combining rules and embeddings
- Relationship inference

### Safety
- Simulation sandboxing with timeouts
- Isolated execution environments
- Resource limits

### Provenance
- Full lineage tracking
- Immutable chain verification
- Links: Artifact → HDR → Pipeline → Container → Signer

## Requirements

- Python 3.8+
- networkx
- cryptography
- pydantic
- numpy

## License

MIT License - See LICENSE file for details

## Citation

If you use Thalos Prime in your research, please cite:

```
@software{thalos_prime_2026,
  title={Thalos Prime Concept: Reproducible Research with Provenance},
  author={XxxGHOSTX},
  year={2026},
  url={https://github.com/XxxGHOSTX/ThalosPrimeConcept}
}
```