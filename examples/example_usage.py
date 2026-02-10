"""
Example usage of Thalos Prime Concept.

Demonstrates the complete workflow including:
- Creating signed Human Directive Records
- Building execution graphs
- Tracking artifacts and provenance
- Using the knowledge space
- Hybrid reasoning
- Simulation sandboxing
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from thalos import (
    HumanDirectiveRecord,
    generate_keypair,
    ExecutionGraph,
    Task,
    Orchestrator,
    SimulationSandbox,
    HybridReasoning,
    ReasoningRule,
    KnowledgeNode,
    KnowledgeEdge,
)
import numpy as np


def example_task_1(**kwargs):
    """Example task that generates data."""
    return {"data": [1, 2, 3, 4, 5], "sum": 15}


def example_task_2(**kwargs):
    """Example task that processes data from task 1."""
    if "task_1" in kwargs:
        data = kwargs["task_1"]["data"]
        return {"processed": [x * 2 for x in data], "count": len(data)}
    return {"processed": [], "count": 0}


def example_task_3(**kwargs):
    """Example task that aggregates results."""
    results = []
    if "task_1" in kwargs:
        results.append(kwargs["task_1"]["sum"])
    if "task_2" in kwargs:
        results.append(kwargs["task_2"]["count"])
    return {"aggregated": sum(results)}


def main():
    print("=" * 70)
    print("Thalos Prime Concept - Complete Example")
    print("=" * 70)
    
    # 1. Create a signed Human Directive Record
    print("\n1. Creating Human Directive Record...")
    private_key, public_key = generate_keypair()
    
    hdr = HumanDirectiveRecord(
        directive_id="HDR-001",
        objectives=[
            "Process data through a multi-stage pipeline",
            "Track all artifacts and their provenance",
            "Demonstrate reproducible research workflow"
        ],
        constraints=[
            "All tasks must complete successfully",
            "Execution time < 60 seconds"
        ],
        parameters={
            "input_size": 5,
            "processing_factor": 2
        },
        success_criteria=[
            "All tasks complete without errors",
            "Provenance chain is valid",
            "Knowledge graph is populated"
        ]
    )
    
    hdr.sign(private_key, "researcher@example.com")
    print(f"   Created HDR: {hdr.directive_id}")
    print(f"   Signed by: {hdr.signer}")
    print(f"   Verified: {hdr.verify(public_key)}")
    
    # 2. Create orchestrator and pipeline
    print("\n2. Creating Pipeline...")
    orchestrator = Orchestrator()
    pipeline = orchestrator.create_pipeline(
        pipeline_id="pipeline-001",
        pipeline_version="1.0.0",
        hdr=hdr,
        container_info={
            "type": "docker",
            "image": "python:3.11-slim",
            "timestamp": "2026-02-10T04:34:52Z"
        }
    )
    print(f"   Created pipeline: {pipeline.pipeline_id}")
    
    # 3. Build execution graph with tasks
    print("\n3. Building Execution Graph...")
    task1 = Task(
        task_id="task_1",
        name="Generate Data",
        function=example_task_1,
        dependencies=[]
    )
    
    task2 = Task(
        task_id="task_2",
        name="Process Data",
        function=example_task_2,
        dependencies=["task_1"]
    )
    
    task3 = Task(
        task_id="task_3",
        name="Aggregate Results",
        function=example_task_3,
        dependencies=["task_1", "task_2"]
    )
    
    pipeline.add_task(task1)
    pipeline.add_task(task2)
    pipeline.add_task(task3)
    
    print("   Execution graph:")
    print(pipeline.execution_graph.visualize())
    
    # 4. Execute pipeline
    print("\n4. Executing Pipeline...")
    results = pipeline.execute()
    
    print("   Results:")
    for task_id, result in results.items():
        print(f"     {task_id}: {result}")
    
    # 5. Check provenance
    print("\n5. Checking Provenance...")
    print(f"   Artifacts created: {len(pipeline.artifact_manager.artifacts)}")
    print(f"   Provenance records: {len(pipeline.provenance_chain.records)}")
    print(f"   Chain is valid: {pipeline.provenance_chain.verify_chain()}")
    
    # 6. Knowledge space
    print("\n6. Populating Knowledge Space...")
    
    # Add some test nodes with embeddings
    node1 = KnowledgeNode(
        node_id="concept_1",
        node_type="concept",
        properties={"name": "machine_learning", "category": "AI"},
        embedding=np.random.rand(384)
    )
    
    node2 = KnowledgeNode(
        node_id="concept_2",
        node_type="concept",
        properties={"name": "deep_learning", "category": "AI"},
        embedding=np.random.rand(384)
    )
    
    node3 = KnowledgeNode(
        node_id="concept_3",
        node_type="concept",
        properties={"name": "statistics", "category": "Math"},
        embedding=np.random.rand(384)
    )
    
    pipeline.knowledge_space.add_node(node1)
    pipeline.knowledge_space.add_node(node2)
    pipeline.knowledge_space.add_node(node3)
    
    edge1 = KnowledgeEdge(
        edge_id="edge_1",
        source_id="concept_1",
        target_id="concept_2",
        relationship_type="related_to",
        properties={"strength": 0.9}
    )
    
    pipeline.knowledge_space.add_edge(edge1)
    
    print(f"   Knowledge nodes: {len(pipeline.knowledge_space.nodes)}")
    print(f"   Knowledge edges: {len(pipeline.knowledge_space.edges)}")
    
    # Test similarity search
    query_embedding = np.random.rand(384)
    similar = pipeline.knowledge_space.find_similar(query_embedding, top_k=2)
    print(f"   Similar nodes to query: {[node_id for node_id, _ in similar]}")
    
    # 7. Hybrid reasoning
    print("\n7. Hybrid Reasoning...")
    reasoning = HybridReasoning(pipeline.knowledge_space)
    
    # Add a reasoning rule
    rule = ReasoningRule(
        rule_id="ai_category_rule",
        pattern={"node_type": "concept", "category": "AI"},
        conclusion={"is_ai_related": True}
    )
    reasoning.add_rule(rule)
    
    # Apply rules
    inferences = reasoning.apply_rules("concept_1")
    print(f"   Inferences for concept_1: {inferences}")
    
    # Explain similarity
    explanation = reasoning.explain_similarity("concept_1", "concept_2")
    print(f"   Similarity explanation: {explanation}")
    
    # 8. Simulation sandbox
    print("\n8. Simulation Sandbox...")
    sandbox = SimulationSandbox(timeout_seconds=10)
    
    # Execute safe Python code
    test_code = """
result = sum(range(10))
"""
    
    sandbox_result = sandbox.execute_python(test_code)
    print(f"   Sandbox execution success: {sandbox_result.success}")
    print(f"   Sandbox result: {sandbox_result.output}")
    print(f"   Execution time: {sandbox_result.execution_time:.3f}s")
    
    # 9. Export pipeline state
    print("\n9. Exporting Pipeline State...")
    output_path = "/tmp/thalos_pipeline_state.json"
    orchestrator.export_pipeline_state("pipeline-001", output_path)
    print(f"   Exported to: {output_path}")
    
    # 10. Summary
    print("\n10. Pipeline Summary:")
    summary = pipeline.get_pipeline_summary()
    print(f"   Pipeline ID: {summary['pipeline_id']}")
    print(f"   Version: {summary['pipeline_version']}")
    print(f"   Artifacts: {summary['artifacts_count']}")
    print(f"   Provenance Records: {summary['provenance_records_count']}")
    print(f"   Knowledge Nodes: {summary['knowledge_nodes_count']}")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
