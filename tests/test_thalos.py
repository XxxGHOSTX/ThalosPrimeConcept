"""
Unit tests for Thalos Prime Concept components.
"""

import unittest
import tempfile
from pathlib import Path
import numpy as np

from thalos import (
    HumanDirectiveRecord,
    generate_keypair,
    ExecutionGraph,
    Task,
    TaskStatus,
    Artifact,
    ArtifactManager,
    ProvenanceRecord,
    ProvenanceChain,
    KnowledgeSpace,
    KnowledgeNode,
    KnowledgeEdge,
    Orchestrator,
    SimulationSandbox,
    HybridReasoning,
    ReasoningRule,
)


class TestHDR(unittest.TestCase):
    """Tests for Human Directive Records."""
    
    def test_create_hdr(self):
        """Test creating an HDR."""
        hdr = HumanDirectiveRecord(
            directive_id="test-001",
            objectives=["test objective"],
            success_criteria=["test passes"]
        )
        self.assertEqual(hdr.directive_id, "test-001")
        self.assertEqual(len(hdr.objectives), 1)
    
    def test_sign_and_verify(self):
        """Test signing and verifying an HDR."""
        private_key, public_key = generate_keypair()
        hdr = HumanDirectiveRecord(
            directive_id="test-002",
            objectives=["test objective"],
            success_criteria=["test passes"]
        )
        
        hdr.sign(private_key, "test@example.com")
        self.assertTrue(hdr.verify(public_key))
        self.assertEqual(hdr.signer, "test@example.com")


class TestExecutionGraph(unittest.TestCase):
    """Tests for Execution Graphs."""
    
    def test_add_task(self):
        """Test adding tasks to execution graph."""
        def dummy_func(**kwargs):
            return "result"
        
        graph = ExecutionGraph()
        task = Task(task_id="t1", name="Task 1", function=dummy_func, dependencies=[])
        graph.add_task(task)
        
        self.assertIn("t1", graph.tasks)
    
    def test_validate_acyclic(self):
        """Test validation of acyclic graph."""
        def dummy_func(**kwargs):
            return "result"
        
        graph = ExecutionGraph()
        task1 = Task(task_id="t1", name="Task 1", function=dummy_func, dependencies=[])
        task2 = Task(task_id="t2", name="Task 2", function=dummy_func, dependencies=["t1"])
        
        graph.add_task(task1)
        graph.add_task(task2)
        
        self.assertTrue(graph.validate())
    
    def test_execution_order(self):
        """Test getting execution order."""
        def dummy_func(**kwargs):
            return "result"
        
        graph = ExecutionGraph()
        task1 = Task(task_id="t1", name="Task 1", function=dummy_func, dependencies=[])
        task2 = Task(task_id="t2", name="Task 2", function=dummy_func, dependencies=["t1"])
        task3 = Task(task_id="t3", name="Task 3", function=dummy_func, dependencies=["t1", "t2"])
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_task(task3)
        
        order = graph.get_execution_order()
        self.assertEqual(order, ["t1", "t2", "t3"])
    
    def test_execute_graph(self):
        """Test executing an execution graph."""
        def task1_func(**kwargs):
            return 10
        
        def task2_func(**kwargs):
            if "t1" in kwargs:
                return kwargs["t1"] * 2
            return 0
        
        graph = ExecutionGraph()
        task1 = Task(task_id="t1", name="Task 1", function=task1_func, dependencies=[])
        task2 = Task(task_id="t2", name="Task 2", function=task2_func, dependencies=["t1"])
        
        graph.add_task(task1)
        graph.add_task(task2)
        
        results = graph.execute()
        self.assertEqual(results["t1"], 10)
        self.assertEqual(results["t2"], 20)
    
    def test_generate_branch_applications(self):
        """Test generating deployment applications for each branch."""
        def dummy_func(**kwargs):
            return "result"
        
        graph = ExecutionGraph()
        task1 = Task(task_id="t1", name="Task 1", function=dummy_func, dependencies=[])
        task2 = Task(task_id="t2", name="Task 2", function=dummy_func, dependencies=["t1"])
        task3 = Task(task_id="t3", name="Task 3", function=dummy_func, dependencies=["t1"])
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_task(task3)
        
        applications = graph.generate_branch_applications()
        self.assertEqual(len(applications), 2)
        
        branch_tasks = {tuple(app["tasks"]) for app in applications}
        self.assertIn(("t1", "t2"), branch_tasks)
        self.assertIn(("t1", "t3"), branch_tasks)
        
        for app in applications:
            self.assertIn("deployment_sequence", app)
            self.assertEqual(app["deployment_sequence"][0]["task_id"], app["tasks"][0])
            self.assertEqual(
                [step["task_id"] for step in app["deployment_sequence"]],
                app["tasks"]
            )
    
    def test_generate_branch_applications_respects_limit(self):
        """Ensure branch application generation enforces max_paths limit."""
        def dummy_func(**kwargs):
            return "result"
        
        graph = ExecutionGraph()
        task1 = Task(task_id="t1", name="Task 1", function=dummy_func, dependencies=[])
        task2 = Task(task_id="t2", name="Task 2", function=dummy_func, dependencies=["t1"])
        task3 = Task(task_id="t3", name="Task 3", function=dummy_func, dependencies=["t1"])
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_task(task3)
        
        with self.assertRaises(ValueError):
            graph.generate_branch_applications(max_paths=1)


class TestArtifacts(unittest.TestCase):
    """Tests for Artifacts."""
    
    def test_create_from_content(self):
        """Test creating artifact from content."""
        artifact = Artifact.create_from_content(
            artifact_id="art-001",
            artifact_type="test",
            content="test content",
            metadata={"key": "value"}
        )
        
        self.assertEqual(artifact.artifact_id, "art-001")
        self.assertEqual(artifact.artifact_type, "test")
        self.assertIsNotNone(artifact.content_hash)
    
    def test_artifact_manager(self):
        """Test artifact manager."""
        manager = ArtifactManager()
        artifact = Artifact.create_from_content(
            artifact_id="art-002",
            artifact_type="test",
            content="test content"
        )
        
        manager.register(artifact)
        retrieved = manager.get("art-002")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.artifact_id, "art-002")
    
    def test_find_by_type(self):
        """Test finding artifacts by type."""
        manager = ArtifactManager()
        
        art1 = Artifact.create_from_content("a1", "type1", "content1")
        art2 = Artifact.create_from_content("a2", "type2", "content2")
        art3 = Artifact.create_from_content("a3", "type1", "content3")
        
        manager.register(art1)
        manager.register(art2)
        manager.register(art3)
        
        type1_artifacts = manager.find_by_type("type1")
        self.assertEqual(len(type1_artifacts), 2)


class TestProvenance(unittest.TestCase):
    """Tests for Provenance Records."""
    
    def test_create_record(self):
        """Test creating provenance record."""
        record = ProvenanceRecord(
            record_id="pr-001",
            artifact_id="art-001",
            hdr_id="hdr-001",
            pipeline_version="1.0.0",
            container_info={"type": "docker"},
            signer="test@example.com"
        )
        
        self.assertEqual(record.record_id, "pr-001")
    
    def test_provenance_chain(self):
        """Test provenance chain."""
        chain = ProvenanceChain()
        
        record1 = ProvenanceRecord(
            record_id="pr-001",
            artifact_id="art-001",
            hdr_id="hdr-001",
            pipeline_version="1.0.0",
            container_info={"type": "docker"},
            signer="test@example.com"
        )
        
        chain.add_record(record1)
        retrieved = chain.get_record("pr-001")
        self.assertIsNotNone(retrieved)
    
    def test_chain_integrity(self):
        """Test chain integrity verification."""
        chain = ProvenanceChain()
        
        record1 = ProvenanceRecord(
            record_id="pr-001",
            artifact_id="art-001",
            hdr_id="hdr-001",
            pipeline_version="1.0.0",
            container_info={"type": "docker"},
            signer="test@example.com"
        )
        
        chain.add_record(record1)
        self.assertTrue(chain.verify_chain())


class TestKnowledgeSpace(unittest.TestCase):
    """Tests for Knowledge Space."""
    
    def test_add_node(self):
        """Test adding knowledge nodes."""
        ks = KnowledgeSpace()
        node = KnowledgeNode(
            node_id="n1",
            node_type="concept",
            properties={"name": "test"}
        )
        
        ks.add_node(node)
        retrieved = ks.get_node("n1")
        self.assertIsNotNone(retrieved)
    
    def test_add_edge(self):
        """Test adding knowledge edges."""
        ks = KnowledgeSpace()
        
        node1 = KnowledgeNode("n1", "concept", {"name": "test1"})
        node2 = KnowledgeNode("n2", "concept", {"name": "test2"})
        
        ks.add_node(node1)
        ks.add_node(node2)
        
        edge = KnowledgeEdge("e1", "n1", "n2", "related", {})
        ks.add_edge(edge)
        
        self.assertIn("e1", ks.edges)
    
    def test_similarity_search(self):
        """Test vector similarity search."""
        ks = KnowledgeSpace()
        
        node1 = KnowledgeNode("n1", "concept", {"name": "test1"}, embedding=np.array([1.0, 0.0, 0.0]))
        node2 = KnowledgeNode("n2", "concept", {"name": "test2"}, embedding=np.array([0.9, 0.1, 0.0]))
        node3 = KnowledgeNode("n3", "concept", {"name": "test3"}, embedding=np.array([0.0, 1.0, 0.0]))
        
        ks.add_node(node1)
        ks.add_node(node2)
        ks.add_node(node3)
        
        query = np.array([1.0, 0.0, 0.0])
        similar = ks.find_similar(query, top_k=2)
        
        self.assertEqual(len(similar), 2)
        self.assertEqual(similar[0][0], "n1")


class TestSandbox(unittest.TestCase):
    """Tests for Simulation Sandbox."""
    
    def test_execute_python(self):
        """Test executing Python code in sandbox."""
        sandbox = SimulationSandbox(timeout_seconds=5)
        
        code = """
result = 2 + 2
"""
        
        result = sandbox.execute_python(code)
        self.assertTrue(result.success)
        self.assertEqual(result.output, 4)
    
    def test_sandbox_timeout(self):
        """Test sandbox timeout."""
        sandbox = SimulationSandbox(timeout_seconds=1)
        
        code = """
import time
time.sleep(10)
result = 1
"""
        
        result = sandbox.execute_python(code)
        self.assertFalse(result.success)
        self.assertIn("timed out", result.error.lower())


class TestReasoning(unittest.TestCase):
    """Tests for Hybrid Reasoning."""
    
    def test_add_rule(self):
        """Test adding reasoning rules."""
        ks = KnowledgeSpace()
        reasoning = HybridReasoning(ks)
        
        rule = ReasoningRule(
            rule_id="r1",
            pattern={"node_type": "concept"},
            conclusion={"is_concept": True}
        )
        
        reasoning.add_rule(rule)
        self.assertIn("r1", reasoning.rules)
    
    def test_apply_rules(self):
        """Test applying reasoning rules."""
        ks = KnowledgeSpace()
        node = KnowledgeNode("n1", "concept", {"name": "test"})
        ks.add_node(node)
        
        reasoning = HybridReasoning(ks)
        rule = ReasoningRule(
            rule_id="r1",
            pattern={"node_type": "concept"},
            conclusion={"is_concept": True}
        )
        reasoning.add_rule(rule)
        
        inferences = reasoning.apply_rules("n1")
        self.assertEqual(len(inferences), 1)
        self.assertEqual(inferences[0]["conclusion"]["is_concept"], True)


class TestOrchestrator(unittest.TestCase):
    """Tests for Pipeline Orchestrator."""
    
    def test_create_pipeline(self):
        """Test creating a pipeline."""
        orchestrator = Orchestrator()
        private_key, public_key = generate_keypair()
        
        hdr = HumanDirectiveRecord(
            directive_id="test-hdr",
            objectives=["test"],
            success_criteria=["pass"]
        )
        hdr.sign(private_key, "test@example.com")
        
        pipeline = orchestrator.create_pipeline(
            pipeline_id="p1",
            pipeline_version="1.0.0",
            hdr=hdr
        )
        
        self.assertEqual(pipeline.pipeline_id, "p1")
    
    def test_pipeline_execution(self):
        """Test executing a complete pipeline."""
        orchestrator = Orchestrator()
        private_key, public_key = generate_keypair()
        
        hdr = HumanDirectiveRecord(
            directive_id="test-hdr",
            objectives=["test"],
            success_criteria=["pass"]
        )
        hdr.sign(private_key, "test@example.com")
        
        pipeline = orchestrator.create_pipeline(
            pipeline_id="p2",
            pipeline_version="1.0.0",
            hdr=hdr
        )
        
        def test_func(**kwargs):
            return "result"
        
        task = Task("t1", "Test", test_func, [])
        pipeline.add_task(task)
        
        results = pipeline.execute()
        self.assertIn("t1", results)

    def test_pipeline_branch_applications(self):
        """Test pipeline-level branch application generation."""
        orchestrator = Orchestrator()
        private_key, public_key = generate_keypair()
        
        hdr = HumanDirectiveRecord(
            directive_id="test-hdr-branches",
            objectives=["test"],
            success_criteria=["pass"]
        )
        hdr.sign(private_key, "test@example.com")
        
        pipeline = orchestrator.create_pipeline(
            pipeline_id="p3",
            pipeline_version="1.0.0",
            hdr=hdr
        )
        
        def task_func(**kwargs):
            return "ok"
        
        task1 = Task("root", "Root", task_func, [])
        task2 = Task("child_a", "Child A", task_func, ["root"])
        task3 = Task("child_b", "Child B", task_func, ["root"])
        
        pipeline.add_task(task1)
        pipeline.add_task(task2)
        pipeline.add_task(task3)
        
        apps = pipeline.generate_deployment_applications()
        self.assertEqual(len(apps), 2)
        for app in apps:
            self.assertEqual(app["pipeline_id"], "p3")
            self.assertEqual(app["container_info"], pipeline.container_info)
            self.assertEqual(app["tasks"][0], "root")


if __name__ == "__main__":
    unittest.main()
