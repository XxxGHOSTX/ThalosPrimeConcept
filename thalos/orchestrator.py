"""
Orchestrator - Main orchestration system for reproducible pipelines.

Integrates all components: HDR, EG, Artifacts, Provenance, and Knowledge Space.
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json
from pathlib import Path

from .hdr import HumanDirectiveRecord
from .execution_graph import ExecutionGraph, Task, TaskStatus
from .artifact import Artifact, ArtifactManager
from .provenance import ProvenanceRecord, ProvenanceChain
from .knowledge_space import KnowledgeSpace, KnowledgeNode, KnowledgeEdge


class Pipeline:
    """
    A reproducible pipeline with full provenance tracking.
    """
    
    def __init__(
        self,
        pipeline_id: str,
        pipeline_version: str,
        hdr: HumanDirectiveRecord,
        container_info: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a pipeline.
        
        Args:
            pipeline_id: Unique identifier for this pipeline
            pipeline_version: Version of the pipeline
            hdr: Human Directive Record guiding this pipeline
            container_info: Container/environment information
        """
        self.pipeline_id = pipeline_id
        self.pipeline_version = pipeline_version
        self.hdr = hdr
        self.container_info = container_info or {
            "type": "local",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.execution_graph = ExecutionGraph()
        self.artifact_manager = ArtifactManager()
        self.provenance_chain = ProvenanceChain()
        self.knowledge_space = KnowledgeSpace()
        
    def add_task(self, task: Task) -> None:
        """Add a task to the execution graph."""
        self.execution_graph.add_task(task)
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the pipeline and track provenance.
        
        Returns:
            Dictionary mapping task IDs to their results
        """
        # Validate the execution graph
        if not self.execution_graph.validate():
            raise ValueError("Execution graph contains cycles")
        
        # Execute all tasks
        results = self.execution_graph.execute()
        
        # Create artifacts and provenance records for results
        for task_id, result in results.items():
            task = self.execution_graph.tasks[task_id]
            
            # Create artifact
            artifact_id = f"{self.pipeline_id}_{task_id}_{int(datetime.utcnow().timestamp())}"
            artifact = Artifact.create_from_content(
                artifact_id=artifact_id,
                artifact_type="task_result",
                content=result,
                metadata={
                    "task_id": task_id,
                    "task_name": task.name,
                    "pipeline_id": self.pipeline_id,
                    "pipeline_version": self.pipeline_version,
                },
                tags=["task_result", task_id]
            )
            self.artifact_manager.register(artifact)
            
            # Create provenance record
            record_id = f"pr_{artifact_id}"
            provenance_record = ProvenanceRecord(
                record_id=record_id,
                artifact_id=artifact_id,
                hdr_id=self.hdr.directive_id,
                pipeline_version=self.pipeline_version,
                container_info=self.container_info,
                signer=self.hdr.signer or "unknown",
                execution_metadata={
                    "task_id": task_id,
                    "task_name": task.name,
                    "start_time": task.start_time.isoformat() if task.start_time else None,
                    "end_time": task.end_time.isoformat() if task.end_time else None,
                    "status": task.status.value,
                }
            )
            self.provenance_chain.add_record(provenance_record)
            
            # Add to knowledge space
            node = KnowledgeNode(
                node_id=artifact_id,
                node_type="artifact",
                properties={
                    "artifact_type": "task_result",
                    "task_id": task_id,
                    "task_name": task.name,
                }
            )
            self.knowledge_space.add_node(node)
        
        return results
    
    def generate_deployment_applications(self) -> List[Dict[str, Any]]:
        """
        Generate deployment-ready application plans for each branch.
        
        Returns:
            List of branch application dictionaries enriched with pipeline context
        """
        branch_apps = self.execution_graph.generate_branch_applications()
        return [
            {
                **app,
                "pipeline_id": self.pipeline_id,
                "container_info": self.container_info,
            }
            for app in branch_apps
        ]
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the pipeline execution.
        
        Returns:
            Dictionary with pipeline summary
        """
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_version": self.pipeline_version,
            "hdr": self.hdr.to_dict(),
            "execution_graph": self.execution_graph.visualize(),
            "artifacts_count": len(self.artifact_manager.artifacts),
            "provenance_records_count": len(self.provenance_chain.records),
            "knowledge_nodes_count": len(self.knowledge_space.nodes),
        }


class Orchestrator:
    """
    Main orchestrator for managing pipelines and automated discovery.
    """
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.global_knowledge_space = KnowledgeSpace()
    
    def create_pipeline(
        self,
        pipeline_id: str,
        pipeline_version: str,
        hdr: HumanDirectiveRecord,
        container_info: Optional[Dict[str, str]] = None
    ) -> Pipeline:
        """
        Create a new pipeline.
        
        Args:
            pipeline_id: Unique identifier for this pipeline
            pipeline_version: Version of the pipeline
            hdr: Human Directive Record guiding this pipeline
            container_info: Container/environment information
            
        Returns:
            New Pipeline instance
        """
        if pipeline_id in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} already exists")
        
        pipeline = Pipeline(pipeline_id, pipeline_version, hdr, container_info)
        self.pipelines[pipeline_id] = pipeline
        return pipeline
    
    def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """Get a pipeline by ID."""
        return self.pipelines.get(pipeline_id)
    
    def discover_related_artifacts(
        self,
        artifact_id: str,
        pipeline_id: str
    ) -> List[Artifact]:
        """
        Discover artifacts related to a given artifact.
        
        Args:
            artifact_id: ID of the artifact
            pipeline_id: ID of the pipeline
            
        Returns:
            List of related artifacts
        """
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return []
        
        # Get the artifact
        artifact = pipeline.artifact_manager.get(artifact_id)
        if not artifact:
            return []
        
        # Find related artifacts through provenance
        related = []
        
        # Get descendants
        descendants = pipeline.artifact_manager.get_descendants(artifact_id)
        related.extend(descendants)
        
        # Get artifacts from parent provenance chain
        provenance_records = pipeline.provenance_chain.get_chain_for_artifact(artifact_id)
        for record in provenance_records:
            if record.previous_record_id:
                lineage = pipeline.provenance_chain.get_lineage(record.previous_record_id)
                for pr in lineage:
                    related_artifact = pipeline.artifact_manager.get(pr.artifact_id)
                    if related_artifact and related_artifact.artifact_id != artifact_id:
                        related.append(related_artifact)
        
        return related
    
    def export_pipeline_state(self, pipeline_id: str, output_path: str) -> None:
        """
        Export the complete state of a pipeline for reproducibility.
        
        Args:
            pipeline_id: ID of the pipeline
            output_path: Path to save the state
        """
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        state = {
            "pipeline_id": pipeline.pipeline_id,
            "pipeline_version": pipeline.pipeline_version,
            "hdr": pipeline.hdr.to_dict(),
            "container_info": pipeline.container_info,
            "artifacts": [
                artifact.to_dict()
                for artifact in pipeline.artifact_manager.artifacts.values()
            ],
            "provenance_chain": pipeline.provenance_chain.export_chain(),
            "knowledge_graph": pipeline.knowledge_space.export_graph(),
        }
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(state, indent=2))
    
    def list_pipelines(self) -> List[Dict[str, str]]:
        """
        List all pipelines.
        
        Returns:
            List of pipeline summaries
        """
        return [
            {
                "pipeline_id": p.pipeline_id,
                "pipeline_version": p.pipeline_version,
                "hdr_id": p.hdr.directive_id,
            }
            for p in self.pipelines.values()
        ]
